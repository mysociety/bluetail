from django.views.generic import TemplateView
from django.shortcuts import render


class UploadResults(TemplateView):
    template_name = "silvereye/upload_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['test'] = "Hello, world"
        return context

def publisher(request):
    return render(request, "publisher.html", {})