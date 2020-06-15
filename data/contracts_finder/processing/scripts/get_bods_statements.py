"""
Acquire BODS data for any Companies House IDs we have in the OCDS data

This script uses Spend Networks Elasticsearch index of OpenOwnership register for lookups

This requires multiple steps

- Get entity statement for the company scheme/ID
    - store the statementID (s)
- Get ownership statements that have this statementID as subject

"""
import json
import sys
from urllib.parse import urlparse
import logging
import os

import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Term, Q
from django.conf import settings

logger = logging.getLogger(__name__)

ELASTICSEARCH_7_TEST = os.getenv("ELASTICSEARCH_7_TEST")
DATABASE_URL = os.environ.get('DATABASE_URL')
SQL_DIR = os.path.join(settings.BASE_DIR, "data", "contracts_finder", "processing", "sql")
BODS_OUTPUT_DIR = os.path.join(settings.BASE_DIR, "data", "contracts_finder", "processing", "bods")
ELASTICSEARCH_CONN = None


def get_entity_statements(
        company_id,
        scheme='GB-COH',
        elastic_conn=ELASTICSEARCH_CONN,
):
    """
    Get entity statements about this Company
    """
    s = Search(using=elastic_conn, index="bods") \
        .filter("term", identifiers__scheme__keyword=scheme) \
        .filter("term", identifiers__id__keyword=company_id)
    res = s.execute()
    statements = [h["_source"] for h in res.hits.hits]
    # Convert AttrDict to Dict
    # statements = [s.to_dict() for s in statements]
    return statements


def get_ownership_statements_with_subject_as(
        statementID,
        elastic_conn=ELASTICSEARCH_CONN,
):
    """
    Get ownership statements about subject
    """
    s = Search(using=elastic_conn, index="bods") \
        .filter("term", subject__describedByEntityStatement__keyword=statementID)
    res = s.execute()
    statements = [h["_source"] for h in res.hits.hits]
    # Convert AttrDict to Dict
    # statements = [s.to_dict() for s in statements]
    return statements


def get_interested_party(
        statementID,
        elastic_conn=ELASTICSEARCH_CONN,
):
    """
    Get statementID for interested party
    """
    s = Search(using=elastic_conn, index="bods") \
        .filter("term", subject__describedByEntityStatement__keyword=statementID)
    res = s.execute()
    statements = [h["_source"] for h in res.hits.hits]
    # Convert AttrDict to Dict
    # statements = [s.to_dict() for s in statements]
    return statements


def get_statements_by_statementIDs(
        list_of_ids,
        elastic_conn=ELASTICSEARCH_CONN,
):
    """
    Get statements from list of statementIDs
    """
    s = Search(using=elastic_conn, index="bods") \
        .filter('ids', values=list_of_ids)
    res = s.execute()
    statements = [h["_source"] for h in res.hits.hits]
    # Convert AttrDict to Dict
    # statements = [s.to_dict() for s in statements]
    return statements



def get_company_statements(
        company_id,
        scheme='GB-COH',
        elastic_conn=ELASTICSEARCH_CONN,
):
    statements = []

    # Get entity statements
    entity_statements = get_entity_statements(company_id, scheme, ELASTICSEARCH_CONN)
    if len(entity_statements) > 1:
        logger.info("more than 1 entity statement: %s", company_id)
    statements.extend(entity_statements)

    # Get interested party statements
    for e in entity_statements:
        entity_statementID = e["statementID"]
        ownership_statements = get_ownership_statements_with_subject_as(entity_statementID, elastic_conn)
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
                interested_party_statements = get_statements_by_statementIDs(interested_party_statementIDs, ELASTICSEARCH_CONN)
                statements.extend(interested_party_statements)

    return statements


def connect_from_url(url):
    result = urlparse(url)
    # TODO add common exceptions
    connection = psycopg2.connect(user=result.username,
                                  password=result.password,
                                  host=result.hostname,
                                  port=result.port,
                                  database=result.path[1:])
    return connection


def lookup_ch_ids():
    sql_filename = "distinct_GB-COH_ids_from_bluetail.sql"
    sql = os.path.join(SQL_DIR, sql_filename)

    engine = create_engine(DATABASE_URL)
    elastic_conn = Elasticsearch(ELASTICSEARCH_7_TEST, verify_certs=True)
    sql = open(sql).read()
    df = pd.read_sql(sql, engine)

    OUTPUT_DIR = os.path.join(BODS_OUTPUT_DIR, "ch_id_openownership_bods")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for i, item in df.iterrows():
        scheme = item.get("party_identifier_scheme")
        id = item.get("party_identifier_id")

        # Ignore bad CH IDs
        if len(id) != 8:
            continue

        logger.info("Looking up %s, %s", scheme, id)
        statements = get_company_statements(company_id=id, scheme=scheme, elastic_conn=elastic_conn)
        statements = [s.to_dict() for s in statements]

        # for s in statements:
        save_path = os.path.join(OUTPUT_DIR, "{0}_{1}_bods.json".format(scheme, id))
        with open(save_path, "w") as writer:
            json.dump(statements, writer)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
                        level=logging.INFO,
                        format='%(asctime)s:%(name)s:%(levelname)s:%(message)s',
                        datefmt="%Y-%m-%dT%H:%M:%S")

    ELASTICSEARCH_CONN = Elasticsearch(ELASTICSEARCH_7_TEST, verify_certs=True)
    lookup_ch_ids()
