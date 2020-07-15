from django.views.generic import TemplateView
from django.shortcuts import render


from silvereye.models import PublisherMetrics


class UploadResults(TemplateView):
    template_name = "silvereye/upload_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['test'] = "Hello, world"
        return context

def publisher(request, publisher_id='test'):
    context = {}
    context['metrics'] = PublisherMetrics.objects.get(publisher_id=publisher_id)
    return render(request, "silvereye/publisher.html", context)
