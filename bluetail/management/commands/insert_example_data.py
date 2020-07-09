import glob
import json
import logging
import os
import shutil

from faker import Faker

from django.core.management import BaseCommand
from django.conf import settings

from bluetail.helpers import UpsertDataHelpers
from bluetail.tests.fixtures import insert_flags, insert_flag_attachments

logger = logging.getLogger('django')

DATA_DIR = os.path.join(settings.BASE_DIR, "data")

fake = Faker('en_GB')
# Generate the same dataset on each run.
# Note that the data might change if faker is updated.
Faker.seed(1234)


def anonymise_bods_json_data(bods_json):
    for statement in bods_json:
        statement['birthDate'] = fake.date_of_birth(minimum_age=18, maximum_age=65).strftime('%Y-%m-%d')
        if statement['statementType'] == 'personStatement':
            if 'names' in statement:
                for name in statement['names']:
                    name['fullName'] = fake.name()
            if 'addresses' in statement:
                for address in statement['addresses']:
                    address['address'] = fake.address()
    return bods_json


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
                upsert_helper.upsert_bods_data(f_path, process_json=anonymise_bods_json_data)

            except:
                logger.exception("Failed to insert example file %s", f_path)

        # Insert Flags
        logger.info("Insert sample Flags")
        insert_flags()

        # Insert assigned Flags
        logger.info("Insert sample FlagAttachments")
        insert_flag_attachments()

        # Insert CF Data

        # Insert CF OCDS JSON
        logger.info("Insert sample OCDS")
        cf_ocds_path = os.path.join(DATA_DIR, "contracts_finder", "ocds")

        for root, dirs, files in os.walk(cf_ocds_path):
            for f in files:
                try:
                    f_path = os.path.join(root, f)
                    upsert_helper.upsert_ocds_data(f_path)
                except:
                    logger.exception("Failed to insert file %s", f_path)

        # Insert BODS JSON
        logger.info("Insert sample BODS")
        cf_bods_path = os.path.join(DATA_DIR, "contracts_finder", "bods")

        for root, dirs, files in os.walk(cf_bods_path):
            for f in files:
                if not f.endswith(".json"):
                    continue
                try:
                    f_path = os.path.join(root, f)
                    upsert_helper.upsert_bods_data(f_path, process_json=anonymise_bods_json_data)
                except:
                    logger.exception("Failed to insert file %s", f_path)
