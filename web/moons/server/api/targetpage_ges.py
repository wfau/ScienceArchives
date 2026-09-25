import json
from pathlib import Path

from django.conf import settings

from queries.tasks import execute_sync
from .helpers import validate_path

# speed of light in km/s
C_SPEED_KM_S = 299792.458

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

def get_line_list():
    path = settings.BASE_DIR / 'resources' / 'GES' / 'ges_lines.json'
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def shift_line_list(line_list, vrad):
    """Apply the radial velocity Doppler shift to each line's rest wavelength.

    The display wavelength is passed to the frontend so it does not need to
    compute the shift itself.
    """
    shift = 1 + vrad / C_SPEED_KM_S
    shifted = []
    for line in line_list:
        entry = dict(line)
        entry['wavelength_display_angstrom'] = get_rounded(
            entry.pop('wavelength_air_angstrom') * shift, ndigits=4
        )
        shifted.append(entry)
    return shifted

def get_targetpage(schema, cname, user):
    query = metadata_with_fallback.format(cname=cname)
    metadata_table = execute_sync(user, query, schema)
    filenames = []
    result = {}
    item = None
    # list files for cname in jpeg folder
    db_path = Path(settings.MOONS_DB['BASE_FILE_PATH']) / 'jpeg'
    img_path = validate_path(db_path)
    img_files = list(img_path.glob(f'{cname}*.jpeg'))
    if img_files:
        thumbnails = [
            str(db_path / ifile.name) for ifile in img_files
        ]
    else:
        thumbnails = [ str(db_path / 'unavailable.jpeg') ]
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
            'thumbnails': thumbnails,
            'lineList': shift_line_list(get_line_list(), item['vrad'] or 0),
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
    else:
        result = {
            'cname': cname,
            'thumbnails': thumbnails,
            'lineList': shift_line_list(get_line_list(), 0),
        }

    return result

def custom_prompt():
    return (
        "SPECIAL COLUMNS:\n"
        "The following columns have special meaning in the frontend and MUST follow these rules:\n"
        "- 'cName': NEVER rename or alias this column. Include it in SELECT if the user requests "
        "a target page, target link, or wants to identify/navigate to a target.\n"
        "- 'fileName': NEVER rename or alias this column. Include it in SELECT if the user requests "
        "a download link, spectrum file, file access, or any reference to retrieving a file.\n"
        "If either column is included, it must appear exactly as 'cName' or 'fileName' with no alias.\n"
    )