import json
import os

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import DetailView

from bluetail.models import OCDSReleaseJSON, OCDSReleaseView, BODSPersonStatementJSON, BODSEntityStatementJSON, BODSOwnershipStatementJSON


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
    context = {
        "tenders": [
            {
                "id": "PROC-20-0001",
                "title": "Tachograph Forensic Services",
                "publisher": "H M Revenue & Customs",
                "closed_date": "1st April",
                "is_closed": True,
                "received": 5,
            },
            {
                "id": "PROC-20-0002",
                "title": "Dynamic Purchasing System for the Supply of Protective Equipment",
                "publisher": "Gateshead Council",
                "closed_date": "1st April",
                "is_closed": True,
                "received": 8,
            },
            {
                "id": "PROC-20-0003",
                "title": "Radio Communication Services for the Birmingham 2022 Commonwealth Games",
                "publisher": "The Organising Committee for the 2022 Birmingham Commonwealth Games",
                "closed_date": "13th April",
                "is_closed": False,
                "received": 4,
            },
            {
                "id": "PROC-20-0004",
                "title": "Town Centre Gift Card Scheme",
                "publisher": "Knowsley Council",
                "closed_date": "21st April",
                "is_closed": False,
                "received": 0,
            },
        ],
    }
    return render(request, "tenders.html", context)


def tender_view(request):
    context = {
        "id": "PROC-20-0001",
        "title": "Tachograph Forensic Services",
        "publisher": "H M Revenue & Customs",
        "published_date": "1st January",
        "closed_date": "1st April",
        "is_closed": True,
        "start_date": "1st June",
        "value": "£120,000",
        "received": [
            {
                "id": "PROC-20-0001/a",
                "tenderer": {
                    "name": "Synomus Technology Services Ltd.",
                },
                "total_errors": 1,
                "total_warnings": 1,
            },
            {
                "id": "PROC-20-0001/b",
                "tenderer": {
                    "name": "Frost Group Ltd.",
                },
                "total_errors": 0,
                "total_warnings": 0,
            },
            {
                "id": "PROC-20-0001/c",
                "tenderer": {
                    "name": "Mitchell Systems Ltd.",
                },
                "total_errors": 0,
                "total_warnings": 2,
            },
            {
                "id": "PROC-20-0001/d",
                "tenderer": {
                    "name": "Gough-Hunt Ltd.",
                },
                "total_errors": 0,
                "total_warnings": 3,
            },
            {
                "id": "PROC-20-0001/e",
                "tenderer": {
                    "name": "Future Tech Horizons Ltd.",
                },
                "total_errors": 0,
                "total_warnings": 1,
            }
        ]
    }
    return render(request, "tender.html", context)


def tenderer_view(request):
    context = {
        "notice": {
            "id": "PROC-20-0001",
        },
        "id": "PROC-20-0001/a",
        "total_errors": 1,
        "total_warnings": 1,
        "tenderer": {
            "total_errors": 1,
            "total_warnings": 0,
            "name": "Synomus Technology Services Ltd.",
            "company_id": {
                "value": "1602647563",
                "error": "Invalid company ID",
            },
            "jurisdiction": {
                "value": "UK",
            },
        },
        "owners": [
            {
                "total_errors": 0,
                "total_warnings": 0,
                "name": "Jasmine Wilkins",
                "national_id": {
                    "value": "FZDS12383607776793",
                },
            },
            {
                "total_errors": 0,
                "total_warnings": 1,
                "name": "Jasmine Wilkins",
                "national_id": {
                    "value": "YDAZ21513405928609",
                    "warning": "Name and ID match a currently serving cabinet minister.",
                },
            },
            {
                "total_errors": 0,
                "total_warnings": 0,
                "name": "Mr. Joe Jones",
                "national_id": {
                    "value": "PFQY03765447964910",
                },
            },
        ],
        "parents": [
            {
                "total_errors": 0,
                "total_warnings": 0,
                "name": "Synomus International Ltd.",
                "company_id": {
                    "value": "6235874596",
                },
                "jurisdiction": {
                    "value": "UK",
                },
            },
            {
                "total_errors": 0,
                "total_warnings": 0,
                "name": "S C M Holdings LLC.",
                "company_id": {
                    "value": "6321254583",
                },
                "jurisdiction": {
                    "value": "UK",
                },
            },
        ],
    }
    return render(request, "tenderer.html", context)


class OCDSDetailView(DetailView):
    model = OCDSReleaseView
    template_name = "ocds.html"
    queryset = OCDSReleaseView.objects.all()


class BODSPersonStatementView(DetailView):
    template_name = "bods_statment.html"
    model = BODSPersonStatementJSON
    queryset = BODSPersonStatementJSON.objects.all()


class BODSEntityStatementView(DetailView):
    template_name = "bods_statment.html"
    model = BODSEntityStatementJSON
    queryset = BODSEntityStatementJSON.objects.all()


class BODSOwnershipStatementView(DetailView):
    template_name = "bods_statment.html"
    model = BODSOwnershipStatementJSON
    queryset = BODSOwnershipStatementJSON.objects.all()
