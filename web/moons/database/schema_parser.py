
import argparse
import json
import re


columndef = r'(\w+)\s+(TIMESTAMP|real|float|INTEGER|int|tinyint|SMALLINT|smallint|bigint|varchar)(\(\d+\))?\s+(not\s+null)?(\s+default\s(-?\d+(\.\d+)?(e[+-]?\d+)?|[\"\'][\w\s\-\:]+[\'\"]))?\,?'
pattern = re.compile(columndef, re.IGNORECASE)

def extract_comment(line):
    if line.startswith('/H'):
        return {'h': line[3:]}
    elif line.startswith('/T'):
        return {'t': line[3:]}
    # ignore other comment lines
    return None

def extract_column_info(line):
    parts = line.split('--')
    col_info = {}
    if len(parts) > 1:
        if 'datetime' in parts[0]:
            print(parts[0])
        match = pattern.search(parts[0].strip())
        if match:
            groups = match.groups()
            col_name = groups[0]
            col_type = groups[1].lower()
            col_length = int(groups[2][1:-1]) if groups[2] else None
            if col_type == 'integer':
                col_type = 'int'
            if col_length is None:
                if col_type == 'real':
                    col_length = 4
                elif col_type == 'float':
                    col_length = 8
                elif col_type == 'bigint':
                    col_length = 8
                elif col_type == 'int':
                    col_length = 4
                elif col_type == 'smallint':
                    col_length = 2
                elif col_type == 'tinyint':
                    col_length = 1
                elif col_type == 'timestamp':
                    col_length = 8
            col_default = groups[5]
            col_info = {
                'name': col_name,
                'type': col_type,
                'size': col_length,
                'default': col_default,
            }
        for part in parts[1:]:
            text = part.strip()[3:]
            if part.startswith('/U'):
                col_info['unit'] = text
            elif part.startswith('/D'):
                col_info['description'] = text
            elif part.startswith('/N'):
                col_info['default'] = text
            elif part.startswith('/K'):
                col_info['casu_keyword'] = text
            elif part.startswith('/F'):
                col_info['fits_ttype'] = text
            elif part.startswith('/C'):
                col_info['unified_content_descriptor'] = text
            elif part.startswith('/Q'):
                col_info['derived_from'] = text
            elif part.startswith('/R'):
                col_info['range'] = text
            elif part.startswith('/V'):
                col_info['values'] = text
    # print(col_info)
    return col_info

def extract_schema_description(f, markdown):
    line = f.readline()
    while line and not line.startswith('--=='):
        if line.startswith('--'):
            text = line[3:]
            if text.strip():
                markdown.append(text)
        line = f.readline()

def extract_table_description(f, output):
    line = f.readline()
    in_view_stmt = False
    view_name = None
    while line and not line.startswith('-- --'):
        if line.startswith('CREATE VIEW'):
            view_name = line[len('CREATE VIEW '):].strip()
            current_context = {'name': view_name, 'markdown': [], 'statement': []}
            output['views'][view_name] = current_context
        elif line.startswith('CREATE TABLE'):
            table_name = line[len('CREATE TABLE '):].strip()[:-1]
            current_context = {'name': table_name, 'markdown': [], 'columns': {}}
            output['tables'][table_name] = current_context
        elif line.startswith('create table'):
            # continue parsing but don't store the output
            current_context = {'markdown': [], 'columns': {}}
        elif view_name and line.startswith('AS'):
            # create view as... we store what comes after this line
            in_view_stmt = True
        elif in_view_stmt:
            current_context['statement'].append(line)
            if line.strip().endswith(';'):
                view_name = None
                in_view_stmt = False
        elif line.startswith('--'): # comment after the tag
            markdown = extract_comment(line[2:])
            if markdown:
                current_context['markdown'].append(markdown)
        elif '--' in line:
            col_info = extract_column_info(line)
            if not 'name' in col_info:
                print(line)
            current_context['columns'][col_info['name']] = col_info
        elif line.startswith(')'):
            return f.readline()
        line = f.readline()
    return line
    
def parse_schema(args):
    with open(args.input_file) as f:
        output = {'tables': {}, 'views': {}}
        current_context = None
        line = f.readline()
        while line:
            if line.startswith('--=='):
                current_context = {'markdown': []}
                output['schema'] = current_context
                extract_schema_description(f, current_context['markdown'])
            elif line.startswith('-- --'):
                line = extract_table_description(f, output)
                continue
            line = f.readline()
        return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='SchemaParser',
        description='Parse the comments in a schema and write to a json structure',
    )
    parser.add_argument('-i', '--input-file')
    parser.add_argument('-o', '--output-file')
    parser.add_argument('-j', '--json-indent', type=int)
    args = parser.parse_args()
    output = parse_schema(args)
    with open(args.output_file, 'w') as o:
        json.dump(output, o, indent=args.json_indent)
