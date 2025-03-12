from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import TemplateView, CreateView, DetailView, ListView, View
from django.views.generic.detail import SingleObjectMixin
from django_tables2.views import SingleTableMixin

from .models import ExecuteSQL, AnonymousQuery
from .forms import SQLQueryForm
from .tasks import execute, read_table, to_json
from .tables import QueryTable

import logging
logger = logging.getLogger(__name__)

def linebreaksbr(text):
    if not text:
        return text
    import re
    re_newlines = re.compile(r"\r\n|\r")
    value = re_newlines.sub("\n", text)
    return value.replace("\n", "<br>")


class DatabaseSchemaView(TemplateView):
    template_name = 'queries/schema_detail.html'

class QueryCreateView(LoginRequiredMixin, CreateView):
    model = ExecuteSQL
    form_class = SQLQueryForm

    def form_valid(self, form):
        if self.request.user.is_authenticated:
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resulturl'] = reverse("queries:query-result", args=[self.object.pk])
        context['statusurl'] = reverse("queries:query-status", args=[self.object.pk])
        return context

class QueryListView(LoginRequiredMixin, SingleTableMixin, ListView):
    model = ExecuteSQL
    table_class = QueryTable

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


def get_results(results_file):
    if results_file:
        try:
            table = read_table(results_file)
            if table:
                df = table.to_pandas()
                result = {
                    'columns': table.colnames,
                    'data': df.to_dict(orient='split', index=False)['data'],
                }
                return result
        except Exception as exc:
            logger.error(exc)
            pass
    return {}

class QueryStatusView(LoginRequiredMixin, DetailView):
    model = ExecuteSQL

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        status = {
            'status': self.object.current_status,
            'started': self.object.started,
            'completed': self.object.completed,
            'results_error': linebreaksbr(self.object.results_error),
        }
        return JsonResponse(status)

class QueryResultView(LoginRequiredMixin, DetailView):
    model = ExecuteSQL

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        result = get_results(self.object.results_file)
        return JsonResponse(result)

# Anonymous Queries

class AnonymousQueryCreateView(CreateView):
    model = ExecuteSQL
    form_class = SQLQueryForm

    def form_valid(self, form):
        form.save()
        self.anon = form.instance.anonymousquery_set.create()
        execute.delay(exec_pk=form.instance.pk)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('queries:anonymous-query-detail', args=[self.anon.slug])

class AnonymousQueryDetailView(DetailView):
    model = AnonymousQuery
    template_name = 'queries/executesql_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.object.sqlquery
        context['resulturl'] = reverse("queries:anonymous-query-result", args=[self.kwargs['slug']])
        context['statusurl'] = reverse("queries:anonymous-query-status", args=[self.kwargs['slug']])
        return context

class AnonymousQueryStatusView(DetailView):
    model = AnonymousQuery

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        status = {
            'status': self.object.sqlquery.current_status,
            'started': self.object.sqlquery.started,
            'completed': self.object.sqlquery.completed,
            'results_error': linebreaksbr(self.object.sqlquery.results_error),
        }
        return JsonResponse(status)

class AnonymousQueryResultView(DetailView):
    model = AnonymousQuery

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        result = get_results(self.object.sqlquery.results_file)
        return JsonResponse(result)
