from pathlib import Path

from queries.tasks import execute_sync
from .helpers import validate_path

metadata_query = '''
SELECT Target.cName, ra, dec, gl, gb, bMag, instrument, gratings, gesType, gesField, gesObject, TEff, logg, FeH, vRad, fileName
FROM SpectrumGroup, RecommendedAstroAnalysis, Target
WHERE RecommendedAstroAnalysis.specGroupId=SpectrumGroup.specGroupID
and Target.targetID=RecommendedAstroAnalysis.targetID
and Target.cName='{cname}'
'''

metadata_with_fallback = '''
SELECT
  t.cName,
  t.ra,
  t.dec,
  t.gl,
  t.gb,
  t.bMag,
  t.jMag,
  raa.instrument,
  raa.gratings,
  raa.gesType,
  raa.gesField,
  raa.gesObject,
  raa.TEff,
  raa.logg,
  raa.FeH,
  raa.vRad,
  sg.fileName
FROM Target t
LEFT JOIN RecommendedAstroAnalysis raa
  ON raa.targetID = t.targetID
LEFT JOIN SpectrumGroup sg
  ON sg.specGroupID = raa.specGroupId
WHERE t.cName = '{cname}'
'''

def get_rounded(value, ndigits=4):
    try:
        return round(value, ndigits=ndigits)
    except:
        return value


def get_targetpage(schema, cname, user):
    query = metadata_with_fallback.format(cname=cname)
    metadata_table = execute_sync(user, query, schema)
    filenames = []
    result = {}
    item = None
    # list files for cname in jpeg folder
    db_path = Path('/moons-flatfiles/products/ges/jpeg/')
    img_path = validate_path(db_path)
    img_files = list(img_path.glob(f'{cname}*.jpeg'))
    if img_files:
        thumbnail = db_path / img_files[0].name
    else:
        thumbnail = db_path / 'unavailable.jpeg'
    for item in metadata_table.to_pylist():
        filenames.append(item['filename'])
    # use only the last row (if there were any) as the rest of the data is the same
    if item:
        result = {
            'metadata': {
                cname: {
                    'RA': get_rounded(item['ra']),
                    'DEC': get_rounded(item['dec']),
                    'gl': get_rounded(item['gl']),
                    'gb': get_rounded(item['gb']),
                    'bMag': get_rounded(item['bmag']),
                    'jMag': get_rounded(item['jmag']),
                },
            },
            'files': filenames,
            'thumbnail': str(thumbnail),
        }
        if item['instrument'] is not None:
            result['metadata'][cname]['Instrument'] = item['instrument']
        if item['gestype'] is not None:
            result['metadata'][cname]['GES Type'] = item['gestype']
        if item['gratings'] is not None:
            result['metadata'][cname]['Gratings'] = item['gratings']
        if item['gesobject'] is not None:
            result['metadata'][cname]['GES Object'] = item['gesobject']
        if item['gesfield'] is not None:
            result['metadata'][cname]['GES Field'] = item['gesfield']
        astro_md = {}
        if item['teff'] is not None:
            astro_md['Teff'] = {
                'unit': 'K',
                'value': get_rounded(item['teff']),
            }
        if item['logg'] is not None:
            astro_md['logg'] = get_rounded(item['logg'])
        if item['feh'] is not None:
            astro_md['FeH'] = get_rounded(item['feh'])
        if item['vrad'] is not None:
            astro_md['vRad'] = {
                'unit': 'km/s',
                'value': get_rounded(item['vrad']),
            }
        if astro_md:
            result['metadata']['Astrophysical Parameters'] = astro_md
        print(result)
    else:
        result = {
            'cname': cname,
            'thumbnail': str(thumbnail),
        }

    return result