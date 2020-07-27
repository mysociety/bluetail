import json
import os

from django.conf import settings
from django.db.models import Q
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import DetailView, ListView, TemplateView

from bluetail.helpers import BodsHelperFunctions, FlagHelperFunctions, ContextHelperFunctions
from bluetail.models import OCDSTender, OCDSTenderer, BODSEntityStatement, \
    BODSOwnershipStatement, BODSPersonStatement, FlagAttachment


class OCDSTenderList(ListView):
    template_name = "bluetail/ocds-tender-list.html"
    context_object_name = 'tenders'

    def get_queryset(self, **kwargs):
        queryset = OCDSTender.objects.order_by('ocid')

        ocid_prefixes = self.request.GET.getlist('ocid_prefix')
        has_flags = self.request.GET.get('has_flags')
        flags = self.request.GET.getlist('flag')

        if ocid_prefixes:
            query = Q()
            for ocid_prefix in ocid_prefixes:
                query.add(Q(ocid__startswith=ocid_prefix), Q.OR)
            queryset = queryset.filter(query)

        if has_flags:
            ocids_with_flags = [x.ocid for x in queryset if len(x.flags) > 0]
            queryset = queryset.filter(ocid__in=ocids_with_flags)

        if flags:
            flag_attachments = FlagAttachment.objects.filter(flag_name__in=flags)
            ocids = flag_attachments.values_list('ocid', flat=True)
            queryset = queryset.filter(ocid__in=ocids)

        return queryset


class OCDSTenderDetailView(DetailView):
    model = OCDSTender
    template_name = "bluetail/ocds-tender.html"
    queryset = OCDSTender.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get the tender from the DetailView context "object"
        tender = self.object

        # Get tenderers
        tenderers = OCDSTenderer.objects.filter(ocid=tender.ocid, party_role="tenderer")

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
    template_name = "bluetail/ocds-tender-tenderer.html"

    def get_context_data(self, ocid, tenderer_id, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get tender
        tender = OCDSTender.objects.get(ocid=ocid)

        # Get tenderer
        tenderer = OCDSTenderer.objects.get(ocid=ocid, party_id=tenderer_id)
        if not tenderer:
            return context

        # get interested_parties
        bods_helper = BodsHelperFunctions()
        interested_parties = bods_helper.get_related_bods_data_for_tenderer(tenderer)

        # Lookup flags and append tenderers to context
        context_helper = ContextHelperFunctions()

        tenderer_context = context_helper.get_tenderer_context(tenderer)

        new_context = {
            "tender": tender,
            "company_id_scheme": settings.COMPANY_ID_SCHEME,
            "tenderer": tenderer_context,
            "owners": interested_parties["interested_persons"],
            "parents": interested_parties["interested_entities"],

        }
        context.update(new_context)
        return context


class BODSPersonStatementView(DetailView):
    template_name = "bluetail/bods_statement.html"
    model = BODSPersonStatement
    queryset = BODSPersonStatement.objects.all()


class BODSEntityStatementView(DetailView):
    template_name = "bluetail/bods_statement.html"
    model = BODSEntityStatement
    queryset = BODSEntityStatement.objects.all()


class BODSOwnershipStatementView(DetailView):
    template_name = "bluetail/bods_statement.html"
    model = BODSOwnershipStatement
    queryset = BODSOwnershipStatement.objects.all()
