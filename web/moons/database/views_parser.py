'''
python views_parser.py -v GES_Views.json -t GES_SpectrumSchema.json GES_CurationLogsSchema.json GES_NeighboursSchema.json GES_ErrorLogsSchema.json -j 4 -o GES_Tables_Views.json
'''

import argparse
from collections import defaultdict
import json
import re

from sqlglot import parse_one, exp
from sqlglot.expressions import Star, Alias
from sqlglot.optimizer.qualify import qualify

def parse_tables(tables_file):
    schema = defaultdict(dict)
    for filename in tables_file:
        with open(filename) as f:
            s = json.load(f)
            for sn, st in s['tables'].items():
                schema[sn].update(st)
    return schema

def construct_view(view_file, tables_schema):
    with open(view_file) as f:
        v = json.load(f)

    view_schemas = {}
    for sn, sv in v['views'].items():
        view_schemas[sn] = {}
        for vn, vd in sv.items():
            statement = ' '.join([l.strip() for l in vd['statement']]).strip()
            ast = parse_one(statement)
            
            table_alias = {}
            for a in ast.find_all(exp.Table):
                table_alias[a.alias] = a.this.name
                table_alias[a.this.name] = a.this.name
            
            columns = {}
            col_source_map = {}  # view_col_name -> (source_table_name, source_col_name)
            
            for select in ast.find_all(exp.Select):
                for proj in select.expressions:
                    try:
                        if isinstance(proj, Alias):
                            ta = proj.this.table
                        else:
                            try:
                                ta = proj.table
                            except:
                                ta = ''
                        table_name = table_alias[ta]
                        table = tables_schema[sn].get(table_name)
                        if not table:
                            print(f'could not find table {table_name}')
                        else:
                            if isinstance(proj.this, Star) or isinstance(proj, Star):
                                columns = table['columns']
                                # Track all columns from this table
                                for col_name in table['columns']:
                                    col_source_map[col_name] = (table_name, col_name)
                            else:
                                if isinstance(proj, Alias):
                                    colname = proj.alias
                                    src_colname = proj.this.name
                                else:
                                    colname = proj.this.name
                                    src_colname = proj.this.name
                                column = dict(table['columns'].get(proj.this.name))
                                column['name'] = colname
                                columns[colname] = column
                                # Track where this view column came from
                                col_source_map[colname] = (table_name, src_colname)
                    except:
                        print(repr(proj))
                        import traceback
                        traceback.print_exc()
                        pass

                # Reverse map: (source_table, source_col) -> view_col_name
                # Used to remap FK source column names to their view equivalents
                reverse_map = {(st, sc): vc for vc, (st, sc) in col_source_map.items()}

                view_primary_keys = []
                view_references = []
                seen_refs = set()

                for view_col, (src_table, src_col) in col_source_map.items():
                    src_table_def = tables_schema[sn].get(src_table, {})

                    # Carry over primary key if this source column is a PK
                    if src_col in src_table_def.get('primary_keys', []):
                        if view_col not in view_primary_keys:
                            view_primary_keys.append(view_col)

                    # Carry over FK references only if ALL columns in the relationship
                    # are present in the view (otherwise the join condition is incomplete)
                    for ref in src_table_def.get('references', []):
                        src_cols = ref.get('sourceCol', [])
                        if all(reverse_map.get((src_table, sc)) for sc in src_cols):
                            mapped_src_cols = [reverse_map[(src_table, sc)] for sc in src_cols]
                            ref_key = (tuple(mapped_src_cols), ref.get('target'), tuple(ref.get('targetCol', [])))
                            if ref_key not in seen_refs:
                                seen_refs.add(ref_key)
                                view_references.append({
                                    'sourceCol': mapped_src_cols,
                                    'target': ref.get('target'),
                                    'targetCol': ref.get('targetCol', [])
                                })

                # Scan all tables looking for FKs that point at columns this view contains
                for other_table_name, other_table_def in tables_schema[sn].items():
                    if other_table_name == vn:  # skip the view itself
                        continue
                    for ref in other_table_def.get('references', []):
                        target_table = ref.get('target')
                        target_cols = ref.get('targetCol', [])
                        other_src_cols = ref.get('sourceCol', [])

                        # Check if ALL of the FK's target columns are present in this view
                        if all(reverse_map.get((target_table, tc)) for tc in target_cols):
                            mapped_view_cols = [reverse_map[(target_table, tc)] for tc in target_cols]
                            ref_key = (tuple(mapped_view_cols), other_table_name, tuple(other_src_cols))
                            if ref_key not in seen_refs:
                                seen_refs.add(ref_key)
                                view_references.append({
                                    'sourceCol': mapped_view_cols,   # the column in this view
                                    'target': other_table_name,       # the table that can join to us
                                    'targetCol': other_src_cols       # the FK column in that table
                                })

                view_data = {'columns': columns}
                if view_primary_keys:
                    view_data['primary_keys'] = view_primary_keys
                if view_references:
                    view_data['references'] = view_references

                tables_schema[sn][vn] = view_data
                vd.update(view_data)
                view_schemas[sn][vn] = vd

    return view_schemas

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='ViewParser',
        description='Parse a json view schema and write out for the SQL query display',
    )
    parser.add_argument('-t', '--tables-file', nargs='+', default=[])
    parser.add_argument('-v', '--view-file')
    parser.add_argument('-o', '--output-file', required=False)
    parser.add_argument('-j', '--json-indent', type=int)
    args = parser.parse_args()
    tables_schema = parse_tables(args.tables_file)
    views_schema = construct_view(args.view_file, tables_schema)
    if views_schema:
        tables = parse_tables(args.tables_file)
        result = {k: {'tables': v} for k,v in tables.items()}
        for k,v in views_schema.items():
            if k in result:
                result[k]['views'] = v
            else:
                result[k] = {'views': v}
        if args.output_file:
            with open(args.output_file, 'w') as o:
                json.dump(result, o, indent=args.json_indent)
        else:
            print(json.dumps(views_schema, indent=args.json_indent))
    else:
        print('No output produced')
