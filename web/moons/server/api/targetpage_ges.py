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

def get_rounded(value, ndigits=4):
    try:
        return round(value, 4)
    except:
        return value


def get_targetpage(schema, cname, user):
        query = metadata_query.format(cname=cname)
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
        if item:
            result = {
                'metadata': {
                    cname: {
                        'RA': get_rounded(item['ra']),
                        'DEC': get_rounded(item['dec']),
                        'gl': get_rounded(item['gl']),
                        'gb': get_rounded(item['gb']),
                        'bMag': get_rounded(item['bmag']),
                        'Instrument': item['instrument'],
                        'GES Type': item['gestype'],
                        'Gratings': item['gratings'],
                        'GES Object': item['gesobject'],
                        'GES Field': item['gesfield'],
                    },
                    'Astrophysical Parameters': {
                        'Teff': get_rounded(item['teff']),
                        'logg': get_rounded(item['logg']),
                        'FeH': get_rounded(item['feh']),
                        'Vrad': get_rounded(item['vrad']),
                    },
                },
                'files': filenames,
                'thumbnail': str(thumbnail),
            }
        return result   