""" Script to create initial Postgres database for all archives.
"""
import psycopg

if __name__ == "__main__":
    with psycopg.connect("dbname=postgres user=rsc") as conn:
     conn.autocommit = True
     with conn.cursor() as cur:
       cur.execute("CREATE TABLESPACE sa_files LOCATION '/moons-archive/database/'")
       cur.execute("CREATE DATABASE sa TABLESPACE sa_files")
