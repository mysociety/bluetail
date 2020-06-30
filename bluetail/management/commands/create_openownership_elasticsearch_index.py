"""
Command to create an elasticsearch index from the Open Ownership register
"""
import logging
import json
import uuid
import os

from django.core.management import BaseCommand
from elasticsearch import Elasticsearch, helpers
from smart_open import open

logger = logging.getLogger('django')

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
ELASTICSEARCH_BODS_INDEX = os.getenv("ELASTICSEARCH_BODS_INDEX", "bods-open_ownership_register")


class Command(BaseCommand):
    help = "Create an Elasticsearch index from the Open Ownership register bulk download for Bluetail to lookup BODS data"

    def handle(self, *args, **kwargs):
        logger.info("Creating Elasticsearch index of Open Ownership register: %s", ELASTICSEARCH_BODS_INDEX)

        elastic_conn = Elasticsearch(ELASTICSEARCH_URL)
        latest_oo_register_url = "https://oo-register-production.s3-eu-west-1.amazonaws.com/public/exports/statements.latest.jsonl.gz"
        id_jsonpath = "statementID"

        iterator = elasticsearch_bulk_index_json_iterator(latest_oo_register_url, ELASTICSEARCH_BODS_INDEX, id_jsonpath=id_jsonpath)

        elasticsearch_bulk_wrapper(elastic_conn, iterator)


def elasticsearch_bulk_index_json_iterator(json_file, target_index, op_type='index', id_jsonpath=None, json_file_encoding="utf-8"):
    """
    Uses `smart_open` to stream line-delimited JSON from any supported source or file.
    Returns generator to use in elasticsearch.helpers.bulk index

    :param json_file: Line-delimeted JSON file
    :param target_index:
    :param op_type:
    :param id_jsonpath: json path to the field containing a unique value to use as _id eg. "data.links.self"
    :return: generator to use in elasticsearch.helpers.bulk index
    """
    with open(json_file, encoding=json_file_encoding) as reader:
        for json_line in reader:
            if id_jsonpath:
                j = json.loads(json_line)
                id = j
                for nestedKey in id_jsonpath.split('.'):
                    id = id.get(nestedKey, id)
            else:
                id = uuid.uuid4()

            # filter objects if needed
            # json_line

            yield {
                "_op_type": op_type,
                "_index": target_index,
                "_type": "_doc",  # Mapping types removed in ES6+. Must be _doc
                "_id": id,
                "_source": json_line
            }


def elasticsearch_bulk_wrapper(elastic_conn, source_iterator):
    """
    Simple wrapper around the elasticsearch.helpers.bulk command for common configuration

    :param elastic_conn:
    :param source_iterator:
    :return:
    """
    response = helpers.bulk(
        elastic_conn,
        source_iterator,
        chunk_size=1000,
        max_retries=10,
        request_timeout=60,
    )
    logger.info("\nbulk_json_data() RESPONSE:", response)
    return response
