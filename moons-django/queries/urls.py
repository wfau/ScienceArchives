from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "queries"

urlpatterns = [
    path('', views.QueryCreateView.as_view(), name='query-create'),
    # path('schema', views.DatabaseSchemaView.as_view(), name='schema-view'),
    path('query', views.QueryListView.as_view(), name='query-list'),
    path('query/<int:pk>', views.QueryDetailView.as_view(), name='query-detail'),
    path('query/result/<int:pk>', views.QueryResultView.as_view(), name='query-result'),
]