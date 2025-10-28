from django.http import StreamingHttpResponse, FileResponse

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from queries.models import ExecuteSQL
from queries.tasks import execute

from .serializers import ExecuteSQLSerializer, ExecuteSQLStatusSerializer

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
    def get(self, request, pk, format=None):
        job = ExecuteSQL.objects.filter(user=self.request.user).get(pk=pk)
        if job.results_file:
            return FileResponse(open(job.results_file, 'rb'), filename='result.parquet')
        else:
            return Response({'error': 'not found'}, status=status.HTTP_404_NOT_FOUND)

class ExecuteSQLResultGraphView(APIView):

    def validate_filename(self, filename):
        from pathlib import Path
        base = Path('/moons-flatfiles/products/ges/giraffe/stacked_v5.00/')
        local_base = Path('/files/')
        path = Path(filename)
        print(path)
        if not path.is_relative_to(base):
            print(f'not relative to {base}')
            return None
        return local_base / path.relative_to(base)

    def get(self, request, pk, format=None):
        try:
            # check if job id is owned by user
            job = ExecuteSQL.objects.filter(user=self.request.user).get(pk=pk)
            filename = request.query_params.get('filename')
            print(filename)
            if filename:
                filename = self.validate_filename(filename)
                print(filename)
                if filename is None:
                    return Response({'error': 'not found'}, status=status.HTTP_404_NOT_FOUND)
                from . import spec_csv
                import io
                f = spec_csv.get_csv(filename)
                return StreamingHttpResponse(
                    streaming_content=io.StringIO(f),
                    content_type="text/plain")
        except:
            import traceback
            traceback.print_exc()

        return Response({'error': 'not found'}, status=status.HTTP_404_NOT_FOUND)

class EnsureCSRFView(APIView):
    # template_name = 'core/simple.html'
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        return Response({'detail': 'CSRF cookie set'})