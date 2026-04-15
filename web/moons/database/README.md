# SQL Schema Parser

Parse the SQL schema for the GES database and create a configuration for the freeform SQL web interface.

## Prerequisites

Create a Python envirnoment and install the requirements with

```
pip install -r requirements.txt
```

## Create tables and views description for web server

Run the bash script
```
./parse_schema.sh <output_dir>
```
to parse the schema files (assumed to be in `../../../schema/ges/`) and output the table and views configuration file for the web server.

## Manual process

### Intermediate files

First SQL schema files are parsed individually to create an output in an intermediate JSON representation.

```
% python schema_parser.py --help
usage: SchemaParser [-h] -i INPUT_FILE [-o OUTPUT_FILE] [-j JSON_INDENT]

Parse the comments in a schema and write to a json structure

options:
  -h, --help            show this help message and exit
  -i, --input-file INPUT_FILE
                        input schema SQL file
  -o, --output-file OUTPUT_FILE
                        output JSON file (optional, default prints to stdout)
  -j, --json-indent JSON_INDENT
                        indentation of json output (optional)
```

For example:
```
python schema_parser.py -i ../../../schema/ges/GES_SpectrumSchema.sql -j 4
```

### Create tables and views description

Process intermediate files to create table and views configuration:

```
python views_parser.py -v GES_Views.json -t GES_SpectrumSchema.json GES_CurationLogsSchema.json -j 4 -o GES_View_Tables.json
```
