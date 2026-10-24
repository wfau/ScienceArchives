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

import logging
logger = logging.getLogger(__name__)


def compress_markdown(markdown_blocks):
    """Flatten markdown block fragments into one readable paragraph.

    The h/t keys only distinguish header vs text (purely presentational),
    so we collapse them into plain text and join the line fragments.
    """
    if not markdown_blocks:
        return ""
    parts = []
    for block in markdown_blocks:
        text = (block.get("t") or block.get("h") or "").strip()
        if text:
            parts.append(text)
    return " ".join(parts)


def simplify_table(table_def):
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
        "kind": "table",
        "purpose": compress_markdown(table_def.get("markdown", [])),  # compact paragraph
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

def simplify_view(view_def):
    # Simple views are SELECT/WHERE pass-throughs over a single base table,
    # so we do NOT repeat their columns (they come from the base table).
    sql = " ".join(view_def.get("statement", [])) or ""

    entry = {
        "kind": "view",
        "sql": sql,
        "purpose": compress_markdown(view_def.get("markdown", [])),
    }

    # Complex views (joins/aliasing) expose their aliased output columns,
    # which cannot be derived from base tables.
    if view_def.get("is_complex"):
        entry["columns"] = {
            k: {"type": v.get("type"), "description": v.get("description")}
            for k, v in (view_def.get("columns") or {}).items()
        }

    return entry

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

        schema_key = task.data_release  # Get database release context

        if schema_key in raw_schemas:
            schema_data = raw_schemas[schema_key]

            # Always load the full schema: tables get full detail (with
            # compressed markdown), views are slimmed to their pass-through
            # delta (sql + purpose), except complex views which keep columns.
            selected_schema_context[schema_key] = {}

            for obj_name, defs in schema_data.get('tables', {}).items():
                selected_schema_context[schema_key][obj_name] = simplify_table(defs)

            for obj_name, defs in schema_data.get('views', {}).items():
                selected_schema_context[schema_key][obj_name] = simplify_view(defs)

        # 2. Assemble Prompt
        system_prompt = (
            "You are an expert SQL generation assistant. "
            "Output ONLY the executable SQL statement — no markdown fences, no explanations, "
            "no commentary, and no code-block wrappers. "
            "Format the SQL itself neatly with line breaks and indentation for readability.\n\n"
            "STRICT RULES:\n"
            "1. Only use tables, views and columns that exist in the DATABASE SCHEMAS provided below.\n"
            "2. Only use JOIN conditions explicitly defined in 'foreign_keys'. "
            "Do NOT infer or guess relationships from column name similarities.\n"
            "3. If two tables cannot be directly joined, look for an intermediary table in the schema "
            "whose foreign keys connect them, and include it in the query.\n"
            "4. Follow the full foreign key path even if it requires multiple intermediary tables.\n"
            "5. If no foreign key path exists between two tables, do not attempt to join them.\n\n"
            "COLUMN NAMES:\n"
            "- For tables, use ONLY column names exactly as they appear in the 'columns' field.\n"
            "- For views, use the column names as shown in the view's 'sql' definition "
            "(for 'SELECT *' / pass-through views, this is all columns of the view's source table; "
            "for complex views, use the view's own 'columns' field).\n"
            "- Do NOT invent, abbreviate, or modify column names.\n"
            "- Do NOT assume a column exists unless it is explicitly listed (tables) or "
            "appears in the view's defining SELECT (views).\n\n"
            "VIEWS:\n"
            "- Views are pre-filtered logical datasets. When a user asks about the data a view "
            "represents, query the view directly (e.g. SELECT ... FROM view_name) rather than "
            "rebuilding its logic from base tables, unless the query needs data or filters that "
            "the view does not provide.\n"
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
                "- 'kind': 'table' or 'view'\n"
                "- 'purpose': human-readable description/legend of the table or view\n"
                "- 'columns': available columns and their types (tables only; also present on complex views)\n"
                "- 'primary_keys': columns that uniquely identify a row (tables only)\n"
                "- 'foreign_keys': ONLY valid JOIN conditions (tables only). "
                "Format is from_columns in this table match to_columns in to_table.\n"
                "- 'sql': the view's defining SELECT statement (views only)\n\n"
                "IMPORTANT — VIEWS:\n"
                "- Views have no 'foreign_keys'; their contents/relationships are defined by "
                "'sql' (base tables + filters) and described by 'purpose'.\n"
                "- To join a view, resolve its base table from its 'sql', then use that base "
                "table's 'foreign_keys'.\n"
                "- Simple pass-through views expose the columns of their source table (given in "
                "the base table's 'columns'); complex views (marked with a 'columns' field) define "
                "their own output columns and are aliased.\n\n"
                f"{json.dumps(selected_schema_context)}"
            )

        # Inject the user's preferred view hints (if any) so the model
        # knows which views are likely relevant. This is a hint, not a
        # filter: the full schema is still available above.
        if task.tables:
            preferred = [
                v.split(".", 1)[-1] if "." in v else v
                for v in task.tables
            ]
            system_prompt += (
                "\n\nPREFERRED VIEWS (USER-SELECTED):\n"
                "The user explicitly indicated the following views for this query. "
                "When a preferred view is relevant to the request, SELECT from that view "
                "directly (e.g. SELECT ... FROM view_name) rather than from its base table(s). "
                "Do not substitute the view's base table unless the query needs data, columns "
                "or filters that the view does not provide.\n"
                + "\n".join(f"- {name}" for name in preferred)
                + "\n"
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
        sql = sql.strip()

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