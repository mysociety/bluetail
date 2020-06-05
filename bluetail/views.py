import json
import os

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import DetailView, ListView, TemplateView

from bluetail.helpers import BodsHelperFunctions, FlagHelperFunctions, ContextHelperFunctions
from bluetail.models import BODSPersonStatementJSON, BODSEntityStatementJSON, BODSOwnershipStatementJSON, OCDSTender, OCDSParty, BODSEntityStatement, \
    BODSOwnershipStatement, BODSPersonStatement


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


class OCDSList(ListView):
    template_name = "ocds-list.html"
    queryset = OCDSTender.objects.order_by('-ocid')
    context_object_name = 'tenders'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # WIP to get total errors/warnings for tenders list

        # new_context = {
        #
        # }
        #
        # # get the tender from the DetailView context "object"
        # for tender in self.object_list:
        #
        #     # Get tenderers
        #     tenderers = OCDSParty.objects.filter(ocid=tender.ocid, party_role="tenderer")
        #
        #     # Augment context
        #     new_context = {
        #         "tender": tender,
        #         "tenderers": [],
        #     }
        #
        #     # Lookup flags and append tenderers to context
        #     context_helper = ContextHelperFunctions()
        #
        #     for tenderer in tenderers:
        #         tenderer_context = context_helper.get_tenderer_context(tenderer)
        #         new_context["tenderers"].append(tenderer_context)

        # context.update(new_context)

        return context


class OCDSTenderDetailView(DetailView):
    model = OCDSTender
    template_name = "ocds.html"
    queryset = OCDSTender.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get the tender from the DetailView context "object"
        tender = self.object

        # Get tenderers
        tenderers = OCDSParty.objects.filter(ocid=tender.ocid, party_role="tenderer")

        # Augment context
        new_context = {
            "tender": tender,
            "tenderers": [],
        }

        # Lookup flags and append tenderers to context
        context_helper = ContextHelperFunctions()

        for tenderer in tenderers:
            tenderer_context = context_helper.get_tenderer_context(tenderer)
            new_context["tenderers"].append(tenderer_context)

        context.update(new_context)
        return context


class OCDSTendererDetailView(TemplateView):
    template_name = "ocds-tenderer.html"

    def get_context_data(self, ocid, tenderer_id, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get tender
        tender = OCDSTender.objects.get(ocid=ocid)

        # Get tenderer
        tenderer = OCDSParty.objects.get(ocid=ocid, party_id=tenderer_id)
        if not tenderer:
            return context

        # get interested_parties
        bods_helper = BodsHelperFunctions()
        interested_parties = bods_helper.get_related_bods_data_for_tenderer(tenderer)

        new_context = {
            "tender": tender,
            "tenderer": tenderer,
            "owners": interested_parties["interested_persons"],
            "parents": interested_parties["interested_entities"],

        }
        context.update(new_context)
        return context


class BODSPersonStatementView(DetailView):
    template_name = "bods_statement.html"
    model = BODSPersonStatementJSON
    queryset = BODSPersonStatementJSON.objects.all()


class BODSEntityStatementView(DetailView):
    template_name = "bods_statement.html"
    model = BODSEntityStatementJSON
    queryset = BODSEntityStatementJSON.objects.all()


class BODSOwnershipStatementView(DetailView):
    template_name = "bods_statement.html"
    model = BODSOwnershipStatementJSON
    queryset = BODSOwnershipStatementJSON.objects.all()
