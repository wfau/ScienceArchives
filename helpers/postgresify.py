import os
import re

def convert_sql(sql):
    # Patterns to convert data types and remove GO statements
    replacements = {
        r'\bint\b': 'INTEGER',
        r'\btinyint\b': 'SMALLINT',
        r'\bdatetime\b': 'TIMESTAMP',
        r'\bGO\b': '',
        r'\bON [A-Za-z_]+\s*$': ''
    }

    # Add schema prefix to table and view creation
    table_view_pattern = re.compile(r'(CREATE TABLE|CREATE VIEW)\s+(\w+)', re.IGNORECASE)
    sql = table_view_pattern.sub(r'\1 GES.\2', sql)

    # Convert data types and remove unsupported syntax
    for pattern, replacement in replacements.items():
        sql = re.sub(pattern, replacement, sql, flags=re.IGNORECASE)

    return sql

def process_file(file_path, filename):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    new_lines = []
    in_statement = False
    statement_lines = []

    for line in lines:
        stripped_line = line.strip()

        if stripped_line.upper().startswith(('CREATE TABLE', 'CREATE VIEW')):
            in_statement = True

        if in_statement:
            statement_lines.append(line)
            if stripped_line.endswith(');') or stripped_line.upper().startswith('AS'):
                if stripped_line.upper().startswith('AS'):
                    # Handle view larger predicate until semicolon
                    if ';' not in stripped_line:
                        continue  # continue appending lines until a semicolon is found

                in_statement = False
                full_statement = ''.join(statement_lines)
                new_statement = convert_sql(full_statement)
                new_lines.append(new_statement)
                statement_lines = []
        else:
            new_lines.append(line)

    if statement_lines:
        full_statement = ''.join(statement_lines)
        new_statement = convert_sql(full_statement)
        new_lines.append(new_statement)

    new_file_path = os.path.join("/Users/rsc/Code/git/ScienceArchives/schema/ges", filename)
    with open(new_file_path, 'w') as file:
        file.writelines(new_lines)

def process_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith('Schema.sql') or filename.endswith('Views.sql'):
            file_path = os.path.join(directory, filename)
            process_file(file_path, filename)

if __name__ == "__main__":
    directory = "/Users/rsc/Code/VDFS/GES/sql/"
    process_directory(directory)
