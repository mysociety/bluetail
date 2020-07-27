"""
Acquire BODS data for any Companies House IDs we have in the OCDS data
This uses an Elasticsearch index of OpenOwnership register for looking up BODS statements
Use the command "create_openownership_elasticsearch_index" to create the index
The BODS statements are stored in a local directory
To insert to database use the insert_example_data command
"""
import json
import shutil
import logging
import os

import pandas as pd
from sqlalchemy import create_engine
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Term, Q
from django.conf import settings
from django.core.management import BaseCommand

from bluetail.models import OCDSTenderer

logger = logging.getLogger('django')

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
ELASTICSEARCH_BODS_INDEX = os.getenv("ELASTICSEARCH_BODS_INDEX", "bods-open_ownership_register")
DATABASE_URL = os.environ.get('DATABASE_URL')
BODS_OUTPUT_DIR = os.path.join(settings.BLUETAIL_APP_DIR, "data", "contracts_finder", "bods")
ELASTICSEARCH_CONN = None


class Command(BaseCommand):
    help = "Download BODS JSON relating to Companies House IDs from the OCDS Party scheme/id in the database"

    def handle(self, *args, **kwargs):
        lookup_ch_ids()


def get_entity_statements(
        company_id,
        scheme=settings.COMPANY_ID_SCHEME,
        elasticsearch_conn=ELASTICSEARCH_CONN,
):
    """
    Get entity statements about this Company
    """
    s = Search(using=elasticsearch_conn, index="bods") \
        .filter("term", identifiers__scheme__keyword=scheme) \
        .filter("term", identifiers__id__keyword=company_id)
    res = s.execute()
    statements = [h["_source"] for h in res.hits.hits]
    return statements


def get_ownership_statements_with_subject_as(
        statementID,
        elasticsearch_conn=ELASTICSEARCH_CONN,
):
    """
    Get ownership statements about subject
    """
    s = Search(using=elasticsearch_conn, index="bods") \
        .filter("term", subject__describedByEntityStatement__keyword=statementID)
    res = s.execute()
    statements = [h["_source"] for h in res.hits.hits]
    return statements


def get_interested_party(
        statementID,
        elasticsearch_conn=ELASTICSEARCH_CONN,
):
    """
    Get statementID for interested party
    """
    s = Search(using=elasticsearch_conn, index="bods") \
        .filter("term", subject__describedByEntityStatement__keyword=statementID)
    res = s.execute()
    statements = [h["_source"] for h in res.hits.hits]
    return statements


def get_statements_by_statementIDs(
        list_of_ids,
        elasticsearch_conn=ELASTICSEARCH_CONN,
):
    """
    Get statements from list of statementIDs
    """
    s = Search(using=elasticsearch_conn, index="bods") \
        .filter('ids', values=list_of_ids)
    res = s.execute()
    statements = [h["_source"] for h in res.hits.hits]
    return statements



def get_bods_statements_for_company(
        company_id,
        scheme=settings.COMPANY_ID_SCHEME,
        elasticsearch_conn=ELASTICSEARCH_CONN,
):
    """
    This requires multiple steps

    - Get entity statement referencing the company scheme/ID
    - Get all ownership statements that have this statementID as subject
    - Get interestedParty statementIDs from the ownership statements
    - Get entity/person statements from these interestedParty statementIDs
    """
    statements = []

    # Get entity statements
    entity_statements = get_entity_statements(company_id, scheme, elasticsearch_conn)
    if len(entity_statements) > 1:
        logger.info("more than 1 entity statement: %s", company_id)
    statements.extend(entity_statements)

    # Get interested party statements
    for e in entity_statements:
        entity_statementID = e["statementID"]
        ownership_statements = get_ownership_statements_with_subject_as(entity_statementID, elasticsearch_conn)
        if ownership_statements:
            interested_party_statementIDs = []
            for o in ownership_statements:
                statements.append(o)
                interested_party = o["interestedParty"]
                if hasattr(interested_party, "unspecified"):
                    continue
                if hasattr(interested_party, "describedByPersonStatement"):
                    interested_party_statementIDs.append(interested_party.describedByPersonStatement)
                if hasattr(interested_party, "describedByEntityStatement"):
                    interested_party_statementIDs.append(interested_party.describedByEntityStatement)
            if interested_party_statementIDs:
                interested_party_statements = get_statements_by_statementIDs(interested_party_statementIDs, elasticsearch_conn)
                statements.extend(interested_party_statements)

    return statements


def lookup_ch_ids():
    # Get list of Company Numbers from the OCDS Parties
    logger.info("Getting OCDS Party scheme/id queryset")

    ids = OCDSTenderer.objects.filter(party_identifier_scheme=settings.COMPANY_ID_SCHEME)

    elasticsearch_conn = Elasticsearch(ELASTICSEARCH_URL, verify_certs=True)
    OUTPUT_DIR = os.path.join(BODS_OUTPUT_DIR, "ch_id_openownership_bods")

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    logger.info("Downloading BODS statements to %s", BODS_OUTPUT_DIR)

    for item in ids:
        scheme = item.party_identifier_scheme
        id = item.party_identifier_id

        # Ignore bad CH IDs
        if len(id) != 8:
            continue

        logger.debug("Looking up %s, %s", scheme, id)
        statements = get_bods_statements_for_company(company_id=id, scheme=scheme, elasticsearch_conn=elasticsearch_conn)
        statements = [s.to_dict() for s in statements]

        # recursive lookups?
        # for statement in statements:
        #     scheme = item.get("party_identifier_scheme")
        #     id = item.get("party_identifier_id")
        #     new_statements = get_bods_statements_for_company(company_id=id, scheme=scheme, elasticsearch_conn=elasticsearch_conn)
        #     statements.extend(new_statements)

        save_path = os.path.join(OUTPUT_DIR, "{0}_{1}_bods.json".format(scheme, id))
        with open(save_path, "w") as writer:
            json.dump(statements, writer, indent=4)
