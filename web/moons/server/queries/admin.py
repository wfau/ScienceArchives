from django.contrib import admin

from .models import ExecuteSQL, AnonymousQuery, QueryPermissions, QueryTemplate

admin.site.register(ExecuteSQL)
admin.site.register(AnonymousQuery)
admin.site.register(QueryPermissions)
admin.site.register(QueryTemplate)
