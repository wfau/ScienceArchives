from django.shortcuts import render
from django.views.generic.base import TemplateView

from django.http import HttpResponse, HttpResponseRedirect

class IndexView(TemplateView):
    template_name = 'core/index.html'

class LoginInfoView(TemplateView):
    template_name = 'core/login-info.html'

    def get(self, request, *args, **kwargs):
        if request.COOKIES.get('skip_login_info'):
            return HttpResponseRedirect('/frontend/')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        response = HttpResponseRedirect('/frontend/')
        if request.POST.get('skip') == '1':
            response.set_cookie('skip_login_info', '1', max_age=31536000, path='/')
        return response