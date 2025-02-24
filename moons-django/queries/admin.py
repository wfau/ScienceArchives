from django.contrib import admin

from .models import ExecuteSQL, AnonymousQuery

admin.site.register(ExecuteSQL)
admin.site.register(AnonymousQuery)
