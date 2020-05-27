import json
import os

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse


def test_view(request):
    example_ocds_path = os.path.join(settings.BASE_DIR, "example_files", "ocds_tenderers.json")
    example_ocds_json = json.load(open(example_ocds_path))
    json_pretty = json.dumps(example_ocds_json, sort_keys=True, indent=4)
    context = {
        "ocds_full": example_ocds_json,
        "ocds_full_pretty": json_pretty,
    }
    return render(request, "test.html", context)

def tenders_view(request):
    context = {}
    return render(request, "tenders.html", context)

def tender_view(request):
    context = {}
    return render(request, "tender.html", context)

def tenderer_view(request):
    context = {}
    return render(request, "tenderer.html", context)
