import json
import logging
import os

from django.core.management import BaseCommand
from django.conf import settings

from bluetail.helpers import UpsertDataHelpers
from bluetail.tests.fixtures import insert_flags, insert_flag_attachments

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(settings.BASE_DIR, "data")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """Add dummy example data to database for demo."""

        upsert_helper = UpsertDataHelpers()

        # Insert PROTOTYPE OCDS JSON
        example_ocds_path = os.path.join(DATA_DIR, "prototype", "ocds", "ocds_tenderers_package.json")
        logger.info("Insert sample OCDS")
        upsert_helper.upsert_ocds_data(example_ocds_path)

        # Insert BODS JSON
        logger.info("Insert sample BODS")
        example_bods_path = os.path.join(DATA_DIR, "prototype", "bods", "PROC-20-0001")
        files = os.listdir(example_bods_path)

        for f in files:
            try:
                f_path = os.path.join(example_bods_path, f)
                upsert_helper.upsert_bods_data(f_path)

            except:
                logger.exception("Failed to insert example file %s", f_path)

        # Insert Flags
        logger.info("Insert sample Flags")
        insert_flags()

        # Insert assigned Flags
        logger.info("Insert sample FlagAttachments")
        insert_flag_attachments()
