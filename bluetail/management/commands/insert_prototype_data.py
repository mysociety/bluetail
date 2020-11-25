import logging
import os

from django.core.management import BaseCommand
from django.conf import settings

from bluetail.helpers import UpsertDataHelpers
from bluetail.tests.fixtures import insert_flags, insert_flag_attachments

logger = logging.getLogger('django')

DATA_DIR = os.path.join(settings.BLUETAIL_APP_DIR, "data", "prototype", settings.LANGUAGE_CODE)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """Add simple prototype data to database for demo."""

        upsert_helper = UpsertDataHelpers()

        # Insert PROTOTYPE OCDS JSON
        example_ocds_path = os.path.join(DATA_DIR, "ocds", "ocds_tenderers_package.json")
        logger.info("Insert prototype OCDS")
        upsert_helper.upsert_ocds_data(example_ocds_path)

        # Insert BODS JSON
        logger.info("Insert prototype BODS")
        example_bods_path = os.path.join(DATA_DIR, "bods", "PROC-20-0001")
        files = os.listdir(example_bods_path)

        for f in files:
            if not f.endswith(".json"):
                continue
            f_path = os.path.join(example_bods_path, f)
            try:
                upsert_helper.upsert_bods_data(f_path)
            except:
                logger.exception("Failed to insert example file %s", f_path)

        # Insert Flags
        logger.info("Insert prototype Flags")
        insert_flags()

        # Insert assigned Flags
        logger.info("Insert prototype FlagAttachments")
        insert_flag_attachments()
