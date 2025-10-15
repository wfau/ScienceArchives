from django.http.response import FileResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

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
    queryset = ExecuteSQL.objects.all()
    serializer_class = ExecuteSQLStatusSerializer

class ExecuteSQLResultView(APIView):
    def get(self, request, pk, format=None):
        job = ExecuteSQL.objects.get(pk=pk)
        if job.results_file:
            return FileResponse(open(job.results_file, 'rb'), filename='result.parquet')
        else:
            return Response({'error': 'not found'}, status=status.HTTP_404_NOT_FOUND)

class EnsureCSRFView(APIView):
    # template_name = 'core/simple.html'
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        return Response({'detail': 'CSRF cookie set'})