import django_tables2 as tables
from django_tables2.utils import A

from .models import ExecuteSQL

class QueryTable(tables.Table):
    started = tables.DateTimeColumn(format="d/m/Y H:i")
    completed = tables.DateTimeColumn(format="d/m/Y H:i")
    format = tables.LinkColumn(
        verbose_name='Results',
        viewname='queries:query-detail',
        orderable=False,
        args=[A('pk')])
    query = tables.Column(orderable=False)
    class Meta:
        model = ExecuteSQL
        fields = ("query", 'status', 'started', 'completed', 'format' )
        order_by = ('-completed')