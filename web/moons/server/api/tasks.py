import json
import importlib
import time
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from openai import OpenAI

from .models import SQLGenerationTask
from .helpers import schema_view_schemas
from queries.models import QueryPermissions

from collections import defaultdict, deque

import logging
logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def generate_sql_celery_task(self, task_id: str):
    task = None
    try:
        # Fetch status record
        for attempt in range(3):
            try:
                task = SQLGenerationTask.objects.get(id=task_id)
                break
            except SQLGenerationTask.DoesNotExist:
                if attempt == 2:
                    return f"Task {task_id} aborted."
                time.sleep(1)

        task.status = SQLGenerationTask.Status.PROCESSING
        task.save(update_fields=['status'])

        # 1. Fetch entire system schema map
        raw_schemas = schema_view_schemas(QueryPermissions.AccessType.PROPRIETARY) or {}
        selected_schema_context = {}
        
        schema_key = task.data_release # Get database release context
        
        if schema_key in raw_schemas:
            schema_data = raw_schemas[schema_key]
            
            # Helper to simplify details
            def simplify(table_def):
                # Remap references into a clearly named FK structure for the LLM
                foreign_keys = [
                    {
                        "from_columns": ref.get("sourceCol", []),
                        "to_table": ref.get("target"),
                        "to_columns": ref.get("targetCol", [])
                    }
                    for ref in table_def.get("references", [])
                ]

                return {
                    "columns": {
                        k: {
                            "type": v.get("type"),
                            "description": v.get("description")
                        }
                        for k, v in table_def.get("columns", {}).items()
                    },
                    "primary_keys": table_def.get("primary_keys", []),  # e.g. ["specID"]
                    "foreign_keys": foreign_keys  # clearly structured for the LLM
                }

            # 2. CORE CONTEXT FALLBACK LOGIC
            # If NO tables are specified, grab EVERYTHING in this data release
            if not task.tables:
                selected_schema_context[schema_key] = {}
                
                # Combine both tables map and views map
                all_objects = {
                    **schema_data.get('tables', {}),
                    **schema_data.get('views', {})
                }
                
                for obj_name, defs in all_objects.items():
                    selected_schema_context[schema_key][obj_name] = simplify(defs)
                    
            # Else, grab only the user's selected tables
            else:
                for composite_key in task.tables:
                    if '.' not in composite_key:
                        continue
                    s_name, object_name = composite_key.split('.', 1)
                    
                    if s_name == schema_key: # Safety context alignment
                        table_def = schema_data.get('tables', {}).get(object_name) or schema_data.get('views', {}).get(object_name)
                        if table_def:
                            if schema_key not in selected_schema_context:
                                selected_schema_context[schema_key] = {}
                            selected_schema_context[schema_key][object_name] = simplify(table_def)

        # 3. Assemble Prompt
        system_prompt = (
            "You are an expert SQL generation assistant. Return ONLY valid executable SQL "
            "inside standard markdown blocks:\n\n```sql\nSELECT ...\n```.\n\n"
            "STRICT RULES:\n"
            "1. Only use tables, views and columns that exist in the DATABASE SCHEMAS provided below.\n"
            "2. Only use JOIN conditions explicitly defined in 'foreign_keys'/'join_on'. "
            "Do NOT infer or guess relationships from column name similarities.\n"
            "3. If two tables cannot be directly joined, look for an intermediary table in the schema "
            "whose foreign keys connect them, and include it in the query.\n"
            "4. Follow the full foreign key path even if it requires multiple intermediary tables.\n"
            "5. If no foreign key path exists between two tables, do not attempt to join them.\n\n"
            "COLUMN NAMES:\n"
            "- Use ONLY column names exactly as they appear in the 'columns' field of the schema.\n"
            "- Do NOT invent, abbreviate, or modify column names.\n"
            "- Do NOT assume a column exists in a table unless it is explicitly listed in that table's 'columns'.\n"
        )
        # add data release specific instructions
        try:
            targetpage_module = settings.MOONS_DB['TARGET_PAGE'].get(schema_key)
            if targetpage_module:
                targetpage = importlib.import_module(targetpage_module)
                system_prompt += targetpage.custom_prompt()
        except:
            logger.error(f'Failed to load {targetpage_module} or load data release instructions', exc_info=True)

        if selected_schema_context:
            system_prompt += (
                "\n\nDATABASE SCHEMAS:\n"
                "Each table/view entry contains:\n"
                "- 'columns': available columns and their types\n"
                "- 'primary_keys': columns that uniquely identify a row\n"
                "- 'foreign_keys'/'join_on': ONLY valid JOIN conditions. Format is "
                "from_columns in this table/view match to_columns in to_table.\n\n"
                f"{json.dumps(selected_schema_context, indent=2)}"
            )

        # OpenAI pipeline setups
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        base_url = getattr(settings, "OPENAI_API_URL", None)
        model_name = getattr(settings, "OPENAI_MODEL_NAME", None)

        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate SQL query: {task.prompt}"}
            ],
            temperature=0.1
        )
        
        ai_msg = response.choices[0].message.content
        
        sql = ai_msg
        if "```sql" in ai_msg:
            sql = ai_msg.split("```sql")[1].split("```")[0].strip()
        elif "```" in ai_msg:
            sql = ai_msg.split("```")[1].split("```")[0].strip()

        task.generated_sql = sql
        task.status = SQLGenerationTask.Status.SUCCESS
        task.completed_at = timezone.now()
        task.save(update_fields=['generated_sql', 'status', 'completed_at'])
        
        return f"Successfully generated SQL for task: {task_id}"

    except Exception as exc:
        if task:
            task.status = SQLGenerationTask.Status.FAILED
            task.error_message = f"Inference Error: {str(exc)}"
            task.completed_at = timezone.now()
            task.save(update_fields=['status', 'error_message', 'completed_at'])
        raise exc
