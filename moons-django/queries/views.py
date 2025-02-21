from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import TemplateView, CreateView, DetailView, ListView, View
from django.views.generic.detail import SingleObjectMixin
from django_tables2.views import SingleTableMixin

from .models import ExecuteSQL
from .forms import SQLQueryForm
from .tasks import execute, read_table, to_json
from .tables import QueryTable

import logging
logger = logging.getLogger(__name__)

class DatabaseSchemaView(TemplateView):
    template_name = 'queries/schema_detail.html'

class QueryCreateView(CreateView):
    model = ExecuteSQL
    form_class = SQLQueryForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        result = super().form_valid(form)
        execute.delay(exec_pk=form.instance.pk)
        return result
    
    def get_success_url(self):
        return reverse('queries:query-detail', args=[self.object.pk])

class QueryDetailView(LoginRequiredMixin, DetailView):
    model = ExecuteSQL

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class QueryListView(LoginRequiredMixin, SingleTableMixin, ListView):
    model = ExecuteSQL
    table_class = QueryTable

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class QueryResultView(LoginRequiredMixin, SingleObjectMixin, View):
    model = ExecuteSQL

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.results_file:
            try:
                table = read_table(self.object.results_file)
                if table:
                    schema = to_json(table.schema)
                    df = table.to_pandas()
                    result = {
                        'schema': schema,
                        'data': df.to_dict(orient='split', index=False)['data'],
                    }
                    return JsonResponse(result)
            except Exception as exc:
                logger.error(exc)
                pass
        return JsonResponse({})
