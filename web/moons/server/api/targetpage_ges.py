from queries.tasks import execute_sync

metadata_query = '''
SELECT Target.cName, ra, dec, instrument, gratings, gesType, gesField, gesObject, TEff, logg, FeH, vRad, fileName
FROM SpectrumGroup, RecommendedAstroAnalysis, Target
WHERE RecommendedAstroAnalysis.specGroupId=SpectrumGroup.specGroupID
and Target.targetID=RecommendedAstroAnalysis.targetID
and Target.cName='{cname}'
'''

def get_targetpage(schema, cname, user):
        query = metadata_query.format(cname=cname)
        metadata_table = execute_sync(user, query, schema)
        filenames = []
        result = {}
        item = None
        for item in metadata_table.to_pylist():
            filenames.append(item['filename'])
        if item:
            result = {
                'metadata': {
                    cname: {
                        'Instrument': item['instrument'],
                        'GES Type': item['gestype'],
                        'Gratings': item['gratings'],
                        'RA': item['ra'],
                        'DEC': item['dec'],
                        'GES Object': item['gesobject'],
                        'GES Field': item['gesfield'],
                    },
                    'Astrophysical Parameters': {
                        'Teff': item['teff'],
                        'logg': item['logg'],
                        'FeH': item['feh'],
                        'Vrad': item['vrad'],
                    },
                },
                'files': filenames,
            }
        return result   