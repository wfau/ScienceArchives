from rest_framework import pagination
from rest_framework.response import Response


class TabulatorPagination(pagination.PageNumberPagination):

    page_size_query_param = 'size'

    def paginate_queryset(self, queryset, request, view=None):
        order_by = request.query_params.get('sort', [])
        if order_by:
            queryset = queryset.order_by(order_by)
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response({
            'links': {
               'next': self.get_next_link(),
               'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'last_page': self.page.paginator.num_pages,
            'data': data
        })