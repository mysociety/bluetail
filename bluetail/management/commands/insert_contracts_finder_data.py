import logging
import os

from django.core.management import BaseCommand
from django.conf import settings

from bluetail.helpers import UpsertDataHelpers

logger = logging.getLogger('django')

DATA_DIR = os.path.join(settings.BASE_DIR, "data")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """Add dummy example data to database for demo."""

        upsert_helper = UpsertDataHelpers()

        # Insert CF OCDS JSON
        logger.info("Insert sample Contracts Finder OCDS")
        cf_ocds_path = os.path.join(DATA_DIR, "contracts_finder", "ocds")

        for root, dirs, files in os.walk(cf_ocds_path):
            for f in files:
                if not f.endswith(".json"):
                    continue
                f_path = os.path.join(root, f)
                try:
                    upsert_helper.upsert_ocds_data(f_path)
                except:
                    logger.exception("Failed to insert file %s", f_path)

        # Insert BODS JSON
        logger.info("Insert sample Contracts Finder BODS")
        cf_bods_path = os.path.join(DATA_DIR, "contracts_finder", "bods")

        for root, dirs, files in os.walk(cf_bods_path):
            for f in files:
                if not f.endswith(".json"):
                    continue
                f_path = os.path.join(root, f)
                try:
                    upsert_helper.upsert_bods_data(f_path)
                except:
                    logger.exception("Failed to insert file %s", f_path)


