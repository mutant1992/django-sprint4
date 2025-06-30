from django.views.generic import TemplateView
from django.shortcuts import render


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


class PageNotFoundView(TemplateView):
    template_name = 'pages/404.html'

    def get(self, request, exception, *args, **kwargs):
        return self.render_to_response({}, status=404)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


class ServerErrorView(TemplateView):
    template_name = 'pages/500.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({}, status=500)

# def about(request):
#     template = 'pages/about.html'
#     return render(request, template)


# def rules(request):
#     template = 'pages/rules.html'
#     return render(request, template)
