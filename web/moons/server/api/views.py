import importlib
import io
from pathlib import Path

from django.db.models import Subquery
from django.conf import settings
from django.http import StreamingHttpResponse, HttpResponse, FileResponse

from rest_framework import generics, status, permissions, mixins
from rest_framework.response import Response
from rest_framework.views import APIView

from queries.models import ExecuteSQL, QueryPermissions, QueryTemplate
from queries.tasks import execute

from .serializers import ExecuteSQLSerializer, ExecuteSQLStatusSerializer, QueryTemplateSerializer
from .renderers import FileRenderer, CSVTextRenderer, FitsFileRenderer, VOTableFileRenderer
from .helpers import schema_view_schemas

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

class ExecuteSQLDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = ExecuteSQLStatusSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return ExecuteSQL.objects.filter(user=self.request.user)
        else:
            return ExecuteSQL.objects.none()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        results_file = instance.results_file
        if results_file:
            try:
                path = Path(results_file)
                path.unlink(missing_ok=True)
            except:
                # any other error
                pass
        return super().delete(request, *args, **kwargs)

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

class ExecuteSQLPageResultView(generics.RetrieveAPIView):
    default_pagination_size = 20
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return ExecuteSQL.objects.filter(user=self.request.user)
        else:
            return ExecuteSQL.objects.none()
    def retrieve(self, request, *args, **kwargs):
        job = self.get_object()
        if job.results_file:
            import pyarrow.parquet as pq
            import pyarrow as pa
            import math
            # start = int(request.query_params.get('start'), 0)
            page_no = int(request.query_params.get('page', 1))
            last_page = math.ceil(job.num_rows / self.default_pagination_size)
            if page_no <= 0 or page_no > last_page:
                return Response({'error': 'invalid page'}, status=status.HTTP_404_NOT_FOUND)
            start = (page_no - 1) * self.default_pagination_size
            result_table = pq.read_table(job.results_file)
            page = result_table.slice(start, self.default_pagination_size)
            schema = {}
            for name in result_table.schema.names:
                field = result_table.schema.field(name)
                schema[name] = str(field.type)

            return Response({
                'last_row': result_table.num_rows,
                'last_page': last_page,
                'data': page.to_pylist(),
                'schema': schema,
            })
            # pq.write_table(page, f)
            # f.flush()
            # return FileResponse(
            #     io.BytesIO(f.getvalue()),
            #     content_type='application/vnd.apache.parquet'
            # )
        return Response('ok')

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

class UserDatabaseSchemaView(APIView):

    def get(self, request):
        if request.user.has_perm('queries.view_executesql'):
            result = schema_view_schemas(QueryPermissions.AccessType.PROPRIETARY)
        else:
            # public tables only
            result = schema_view_schemas(QueryPermissions.AccessType.PUBLIC)
        return Response(result)

class QueryTemplateListView(generics.ListAPIView):
    serializer_class = QueryTemplateSerializer
    pagination_class = None

    def get_queryset(self):
        if self.request.user.has_perm('queries.view_executesql'):
            access = QueryPermissions.AccessType.PROPRIETARY
        else:
            access = QueryPermissions.AccessType.PUBLIC
        schemas = QueryPermissions.objects.filter(access=access).values_list('schema', flat=True)
        return QueryTemplate.objects.filter(schema__in=schemas)

class QueryTemplateRetrieveView(generics.RetrieveAPIView):
    serializer_class = QueryTemplateSerializer

    def get_queryset(self):
        if self.request.user.has_perm('queries.view_executesql'):
            access = QueryPermissions.AccessType.PROPRIETARY
        else:
            access = QueryPermissions.AccessType.PUBLIC
        schemas = QueryPermissions.objects.filter(access=access).values_list('schema', flat=True)
        return QueryTemplate.objects.filter(schema__in=schemas)

class MetadataRetrieveView(APIView):
    def get(self, request):
        cname = request.query_params.get('cname')
        schema = request.query_params.get('schema')
        targetpage_module = settings.MOONS_DB['TARGET_PAGE'].get(schema)
        if not targetpage_module:
            logger.error(f'No target page query for {schema}')
            return Response({'error': 'not found'}, status=status.HTTP_404_NOT_FOUND)

        targetpage = importlib.import_module(targetpage_module)
        result = targetpage.get_targetpage(schema=schema, cname=cname, user=request.user)

        return Response(result)