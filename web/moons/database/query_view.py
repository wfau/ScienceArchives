import argparse
import json

def parse_schema(args):
    output = {}
    with open(args.input_file) as f:
        schema = json.load(f)
        for table_name in args.table:
            table_schema = schema['tables'].get(table_name)
            if table_schema and 'columns' in table_schema:
                output[table_name] = {
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
    parser.add_argument('-i', '--input-file')
    parser.add_argument('-o', '--output-file')
    parser.add_argument('-t', '--table', help='include table', nargs='+')
    parser.add_argument('-j', '--json-indent', type=int)
    args = parser.parse_args()
    output = parse_schema(args)
    if output:
        with open(args.output_file, 'w') as o:
            json.dump(output, o, indent=args.json_indent)
    else:
        print('No output produced')
