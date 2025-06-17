'''
Query all identifiers from the registry and write out the active resource files
to the folder "output/".
'''

import io
import requests
import xml.etree.ElementTree as ET

tree = ET.parse('registry_identifiers.xml')
root = tree.getroot()

# Pull all identifiers from the existing registry
base_url = 'http://publishing-registry.roe.ac.uk/astrogrid-registry_v1_0/OAIHandlerv1_0'
identifier_tag = 'oai:identifier'
oai_ns = "http://www.openarchives.org/OAI/2.0/"
num_files = 0
for el in root.findall(".//{http://www.openarchives.org/OAI/2.0/}identifier"):
    ivo_id = el.text
    print(ivo_id)
    # Request the resource for the identifier
    response = requests.get(f'{base_url}?verb=GetRecord&metadataPrefix=ivo_vor&identifier={ivo_id}')
    rf = io.StringIO(response.text)
    ivo_id_tree = ET.parse(rf)
    for r in ivo_id_tree.findall('.//{http://www.ivoa.net/xml/RegistryInterface/v1.0}Resource'):
        status = r.get('status')
        # Only store resources that are active, otherwise ignore
        if status == 'active':
            # Need the zero timezone added to the ISO timestamp
            r.set('created', f"{r.get('created')}Z")
            r.set('updated', f"{r.get('updated')}Z")
            if ivo_id == 'ivo://wfau.roe.ac.uk':
                output_name = 'output/authority.xml'
            else:
                output_name = f"{ivo_id[len('ivo://wfau.roe.ac.uk/'):]}.xml"
                output_name = 'output/' + output_name.replace('/', '-')
            ET.ElementTree(r).write(output_name, encoding='utf-8')
            print(f'wrote {output_name}')
            num_files += 1
        else:
            print(f'resource has status {status}')

print(f'Wrote {num_files} output files')