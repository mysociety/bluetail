import json
import logging
import os

from django.core.management import BaseCommand
from django.conf import settings
from faker import Faker

from bluetail.helpers import UpsertDataHelpers

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


def anonymise_ocds_json_data(ocds_json):
    # extract release
    if ocds_json.get("compiledRelease"):
        releases = [ocds_json.get("compiledRelease")]
    else:
        releases = ocds_json["releases"]

    for release in releases:
        # anonimise buyer
        orig_buyer = release["buyer"]["name"]
        fake_buyer = f"{fake.city()} City Council"

        release["buyer"]["name"] = fake_buyer
        for party in release["parties"]:
            if party.get("name") == orig_buyer:
                party["name"] = fake_buyer

        # anonimise tenderers
        for j, tenderer in enumerate(release["tender"]["tenderers"]):
            id = tenderer.get("id")
            orig_name = tenderer.get("name")
            fake_name = fake.company()

            release["tender"]["tenderers"][j]["name"] = fake_name
            for j, party in enumerate(release["parties"]):
                if party.get("id") == id:
                    release["parties"][j]["name"] = fake_name
                    fake_address = {
                        "streetAddress": fake.street_address(),
                        "locality": fake.city(),
                        "postalCode": fake.postcode(),
                        "countryName": "United Kingdom",
                    }
                    release["parties"][j]["address"] = fake_address
                    release["parties"][j]["contactPoint"] = fake.name()

            for k, award in enumerate(release.get("awards", [])):
                for l, supplier in enumerate(award.get("suppliers", [])):
                    if supplier.get("id") == id:
                        release["awards"][k]["suppliers"][l]["name"] = fake_name
    ocds_dict = json.dumps(ocds_json)
    return ocds_json


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--anonymise", action='store_true', help="Anonymise names/addresses during insert")

    def handle(self, *args, **kwargs):
        """Add dummy example data to database for demo."""
        anonymise = kwargs['anonymise']
        if anonymise:
            anonymise_ocds_function = anonymise_ocds_json_data
            anonymise_bods_function = anonymise_bods_json_data
        else:
            anonymise_ocds_function = None
            anonymise_bods_function = None

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
                    upsert_helper.upsert_ocds_data(f_path, process_json=anonymise_ocds_function)
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
                    upsert_helper.upsert_bods_data(f_path, process_json=anonymise_bods_function)
                except:
                    logger.exception("Failed to insert file %s", f_path)


