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
            # print(vn)
            # if vn != 'RecommendedOutlierAnalysis':
            #     continue
            statement = ' '.join([l.strip() for l in vd['statement']]).strip()
            # print(statement)
            ast = parse_one(statement)
            # print(repr(ast))
            table_alias = {}
            for a in ast.find_all(exp.Table):
                # this could be empty
                # but columns would not use a table name either
                table_alias[a.alias] = a.this.name
                table_alias[a.this.name] = a.this.name
            # print(table_alias)
            columns = {}
            for select in ast.find_all(exp.Select):
                for proj in select.expressions:
                    try:
                        # print(repr(proj))
                        # print(proj.this)
                        if isinstance(proj, Alias):
                            ta = proj.this.table
                        else:
                            try:
                                ta = proj.table
                            except:
                                # there is no table atribute
                                ta = ''
                        table_name = table_alias[ta]
                        # print(table_name)
                        table = tables_schema[sn].get(table_name)
                        if not table:
                            print(f'could not find table {table_name}')
                        else:
                            # print(table)
                            if isinstance(proj.this, Star) or isinstance(proj, Star):
                                # print('all columns')
                                columns = table['columns']
                            else:
                                if isinstance(proj, Alias):
                                    colname = proj.alias
                                else:   
                                    colname = proj.this.name
                                column = dict(table['columns'].get(proj.this.name))
                                column['name'] = colname
                                # print(column)
                                columns[colname] = column
                    except:
                        print(repr(proj))
                        import traceback
                        traceback.print_exc()
                        pass
                tables_schema[sn][vn] = {'columns': columns}
                vd.update({'columns': columns})
                view_schemas[sn][vn] = vd
                # print(tables_schema[sn][vn])
        return view_schemas

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='ViewParser',
        description='Parse a json view schema and write out for the SQL query display',
    )
    parser.add_argument('-t', '--tables-file', nargs='+', default=[])
    parser.add_argument('-v', '--view-file')
    parser.add_argument('-o', '--output-file')
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
