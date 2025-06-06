""" Script to prepare MOONS archive schema within the sa Postgres database.
"""
import os
import psycopg

def execute_statements(file_path, conn):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    statement_lines = []
    in_statement = False

    for line in lines:
        stripped_line = line.strip()

        if stripped_line.upper().startswith(('CREATE TABLE', 'CREATE VIEW')):
            in_statement = True
            line = line.replace("GES.", "GESDR4.")

        if in_statement:
            statement_lines.append(line)
            if stripped_line.endswith(';'):
                in_statement = False
                full_statement = ''.join(statement_lines)

                # Execute the SQL statement
                try:
                    with conn.cursor() as cur:
                        print(f"Executing statement: {statement_lines[0].strip()}")
                        cur.execute(full_statement)
                except Exception as e:
                    print(f"Error executing statement starting with: {statement_lines[0].strip()}")
                    print(e)

                statement_lines = []

if __name__ == "__main__":
    directory = "/home/rsc/ScienceArchives/schema/ges"
    with psycopg.connect("dbname=sa user=rsc") as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS GESDR4 CASCADE")
            cur.execute("CREATE SCHEMA GESDR4")

        for filename in os.listdir(directory):
            if filename.endswith('.sql'):
                file_path = os.path.join(directory, filename)
                execute_statements(file_path, conn)
