import importlib
import io
from pathlib import Path

from django.conf import settings
from django.http import StreamingHttpResponse, HttpResponse, FileResponse

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from queries.models import ExecuteSQL
from queries.tasks import execute

from .serializers import ExecuteSQLSerializer, ExecuteSQLStatusSerializer
from .renderers import FileRenderer, CSVTextRenderer, FitsFileRenderer, VOTableFileRenderer

import logging
logger = logging.getLogger(__name__)

class ExecuteSQLListCreateView(generics.ListCreateAPIView):
    serializer_class = ExecuteSQLSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return ExecuteSQL.objects.filter(user=self.request.user).order_by('-pk')
        else:
            return ExecuteSQL.objects.none()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ExecuteSQLStatusSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        execute_sql = serializer.save(user=self.request.user)
        execute.delay(exec_pk=execute_sql.pk)

class ExecuteSQLDetailView(generics.RetrieveAPIView):
    serializer_class = ExecuteSQLStatusSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return ExecuteSQL.objects.filter(user=self.request.user)
        else:
            return ExecuteSQL.objects.none()

class ExecuteSQLResultView(APIView):

    renderer_classes = [
        FileRenderer,
        CSVTextRenderer,
        FitsFileRenderer,
        VOTableFileRenderer,
    ]

    def finalize_response(self, request, response, *args, **kwargs):
        """
        Return the response with the proper content disposition and the customized
        filename instead of the browser default (or lack thereof).
        """
        response = super().finalize_response(request, response, *args, **kwargs)
        if isinstance(response, Response):
            format = response.accepted_renderer.format
            if format in ["fits", 'votable']:
                filename = f'result.{format}'
                response["content-disposition"] = (
                    f"attachment; filename={filename}"
                )
        return response

    def get(self, request, pk, format=None):
        job = ExecuteSQL.objects.filter(user=self.request.user).get(pk=pk)
        if job.results_file:
            if request.accepted_renderer.format == 'parquet':
                return FileResponse(open(job.results_file, 'rb'), filename='result.parquet')
            return Response(job.results_file)
        else:
            return Response({'error': 'not found'}, status=status.HTTP_404_NOT_FOUND)

class LocalFileMixin():

    def validate_filename(self, filename):
        if not filename:
            return None
        base = Path(settings.MOONS_DB['BASE_FILE_PATH'])
        local_base = Path('/files/')
        path = Path(filename)
        if not path.is_relative_to(base):
            logger.error(f'Requested file path {filename} not relative to {base}')
            return None
        return local_base / path.relative_to(base)

class ExecuteSQLResultGraphView(LocalFileMixin, APIView):

    def generate_csv(self, schema, filename):
        converter = settings.MOONS_DB['SPECTRA_CONVERTER'].get(schema)
        if not converter:
            raise Exception(f'No converter registered for schema {schema}. Please check your settings.')
        spec_csv = importlib.import_module(converter)
        f = spec_csv.get_csv(filename)
        return StreamingHttpResponse(
            streaming_content=io.StringIO(f),
            content_type="text/plain")

    def get(self, request, pk, format=None):
        try:
            # check if job id is owned by user
            job = ExecuteSQL.objects.filter(user=self.request.user).get(pk=pk)
            qp = request.query_params.get('filename')
            filename = self.validate_filename(qp)
            if filename is None:
                raise Exception(f'Invalid filename {qp}')

            return self.generate_csv(job.schema, filename)
        except:
            logger.error('Failed to generate spectra data', exc_info=True)

        return Response({'error': 'not found'}, status=status.HTTP_404_NOT_FOUND)

class ExecuteSQLResultFilenameView(LocalFileMixin, APIView):

    def get(self, request, pk, format=None):
        try:
            # check if job id is owned by user
            job = ExecuteSQL.objects.filter(user=self.request.user).get(pk=pk)
            qp = request.query_params.get('filename')
            filename = self.validate_filename(qp)
            if filename is None:
                raise Exception(f'Invalid filename {qp}')

            return FileResponse(open(filename, 'rb'), filename=filename.name)
        except:
            logger.error('Cannot fetch file for download', exc_info=True)

        return Response({'error': 'not found'}, status=status.HTTP_404_NOT_FOUND)

class EnsureCSRFView(APIView):
    # template_name = 'core/simple.html'
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        return Response({'detail': 'CSRF cookie set'})