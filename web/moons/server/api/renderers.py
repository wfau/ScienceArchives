import io
from rest_framework import renderers
from astropy.table import Table

class FileRenderer(renderers.BaseRenderer):
    media_type = 'application/vnd.apache.parquet'
    format = 'parquet'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return None

class CSVTextRenderer(renderers.BaseRenderer):
    media_type = 'text/csv'
    format = 'csv'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        atable = Table.read(data)
        output = io.StringIO()
        atable.write(output, format='ascii.ecsv', delimiter=',')
        return output.getvalue()

class FitsFileRenderer(renderers.BaseRenderer):
    media_type = 'application/octet-stream'
    format = 'fits'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        atable = Table.read(data)
        output = io.BytesIO()
        atable.write(output, format='fits')
        return output.getvalue()

class VOTableFileRenderer(renderers.BaseRenderer):
    media_type = 'application/octet-stream'
    format = 'votable'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        atable = Table.read(data)
        output = io.BytesIO()
        atable.write(output, format='votable')
        return output.getvalue()
