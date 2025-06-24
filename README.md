# WFAU Science Archives

## Contributors
### Active Contributors

* Ross Collins (rsc@roe.ac.uk)
* Amy Krause (a.krause@epcc.ed.ac.uk)

## Purpose

Software repository for the curation and website hosting of the WFAU Science Archives:
* Python curation scripts and common database access tools
* Database schema
* Website pages and server backend code

## Dependencies
* Python 3.12.8
### Python libraries
* psycopg-3.2.4
* astropy-7.0.0
* numpy-2.2.2
* scipy-1.15.1
* pandas-2.2.3

## Installation

### VM

See https://github.com/wfau/ScienceArchives/wiki/Server-Configuration-Details

### Python library installation

Python is installed from miniconda3 in /home/dev-env

Enable the correct Python environment via:

    source /home/dev-env/miniconda3/bin/activate

Use pip3 to install:

    pip3 install psycopg
    pip3 install "psycopg[binary]"
    pip3 install astropy
    pip3 install scipy

### Code installation

    git clone -b <branch_name> git@github.com:wfau/ScienceArchives.git

### Configuration files

TBD

### Apache configuration

TBD

## Running the software

TBD

## Troubleshooting

TBD
