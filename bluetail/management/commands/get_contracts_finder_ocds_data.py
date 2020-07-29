"""
"""
import logging
from pprint import pprint

from django.core.management import BaseCommand

from bluetail.data.contracts_finder.processing.scripts import cf_notices_ocds_api

logger = logging.getLogger('django')


class Command(BaseCommand):
    def add_arguments(self, parser):
        cf_notices_ocds_api.add_arguments(parser)

    def handle(self, *args, **kwargs):
        """
        Wrapper Django command to call the custom script at bluetail/data/contracts_finder/processing/scripts/cf_notices_ocds_api.py
        """
        logger.info("Running cf_notices_ocds_api.run(**kwargs) with kwargs: \n {0}".format(pprint(kwargs)))
        cf_notices_ocds_api.run(**kwargs)
