from django.urls import include, path

from . import views

app_name = "api"

urlpatterns = [
    path('queries', views.ExecuteSQLListCreateView.as_view(), name='queries'),
    path('queries/<int:pk>', views.ExecuteSQLDetailView.as_view(), name='query-detail'),
    path('results/<int:pk>/json', views.ExecuteSQLPageResultView.as_view(), name='result-page'),
    path('results/<int:pk>', views.ExecuteSQLResultView.as_view(), name='result-detail'),
    path('results/<int:pk>/plot', views.ExecuteSQLResultGraphView.as_view(), name='plot-detail'),
    path('results/<int:pk>/file', views.ExecuteSQLResultFilenameView.as_view(), name='file-detail'),
    path('csrf', views.EnsureCSRFView.as_view(), name='csrf-view'),
]