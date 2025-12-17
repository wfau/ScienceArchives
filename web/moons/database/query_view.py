import argparse
import json
from collections import defaultdict

def parse_schema(args):
    output = {}
    schema = defaultdict(dict)
    for filename in args.input_file:
        with open(filename) as f:
            s = json.load(f)
            for sn, st in s['tables'].items():
                schema[sn].update(st)

    for table_name in args.table:
        sn, tn = table_name.split('.')
        table_schema = schema.get(sn, {}).get(tn)
        if sn not in output:
            output[sn] = {}
        if table_schema and 'columns' in table_schema:
            output[sn][tn] = {
                'data': [
                    [col['name'], col['type'], col['size']]
                    for col_name, col in table_schema['columns'].items()
                ]
            }
            print(f'Wrote table {table_name}')
        else:
            print(f'Table not found: {table_name}')
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='SchemaParser',
        description='Parse a json table schema and write out for the SQL query display',
    )
    parser.add_argument('-i', '--input-file', nargs='+')
    parser.add_argument('-o', '--output-file')
    parser.add_argument('-t', '--table', help='include table', nargs='+')
    parser.add_argument('-j', '--json-indent', type=int)
    args = parser.parse_args()
    output = parse_schema(args)
    if output:
        if args.output_file:
            with open(args.output_file, 'w') as o:
                json.dump(output, o, indent=args.json_indent)
        else:
            print(json.dumps(output, indent=args.json_indent))
    else:
        print('No output produced')
