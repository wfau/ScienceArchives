#! /bin/bash

schema_dir="../../../schema/ges/"
output_dir=$1
mkdir -p $output_dir

# parse all SQL table schema files and output intermediate files
python schema_parser.py -i $schema_dir/GES_CurationLogsSchema.sql -j 4 -o $output_dir/GES_CurationLogsSchema.json
python schema_parser.py -i $schema_dir/GES_ErrorLogsSchema.sql -j 4 -o $output_dir/GES_ErrorLogsSchema.json
python schema_parser.py -i $schema_dir/GES_NeighboursSchema.sql -j 4 -o $output_dir/GES_NeighboursSchema.json
python schema_parser.py -i $schema_dir/GES_SpectrumSchema.sql -j 4 -o $output_dir/GES_SpectrumSchema.json
python schema_parser.py -i $schema_dir/GES_Views.sql -j 4 -o $output_dir/GES_Views.json

# parse all intermediate files into the tables and views data file
python views_parser.py -v $output_dir/GES_Views.json \
    -t $output_dir/GES_SpectrumSchema.json \
       $output_dir/GES_CurationLogsSchema.json \
       $output_dir/GES_NeighboursSchema.json \
       $output_dir/GES_ErrorLogsSchema.json \
    -j 4 \
    -o $output_dir/GES_Tables_Views.json
