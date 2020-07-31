import csv
import os

from django.conf import settings
from django.test import TestCase

from bluetail.helpers import FlagHelperFunctions, UpsertDataHelpers, ContextHelperFunctions, BodsHelperFunctions
from bluetail.models import BODSPersonStatement, OCDSTenderer
from bluetail.tests.fixtures import insert_flags, insert_flag_attachments


PROTOTYPE_DATA_PATH = os.path.join(settings.BLUETAIL_APP_DIR, "data", "prototype")
TEST_DATA_PATH = os.path.join(settings.BASE_DIR, "bluetail", "tests", "data")


class TestFlagHelperFunctions(TestCase):
    flag_helper = FlagHelperFunctions()
    upsert_helper = UpsertDataHelpers()

    def setUp(self):
        insert_flags()
        insert_flag_attachments()
        bods_test_file_path = os.path.join(PROTOTYPE_DATA_PATH, "bods", "PROC-20-0001", "d_ownership.json")
        self.upsert_helper.upsert_bods_data(bods_test_file_path)

    def test_get_flags_for_ocds_party_identifier(self):
        identifier = {
            "scheme": "GB-LAC",
            "id": "1602647563",
            "legalName": "Synomus Technology Services Ltd."
        }
        flags = self.flag_helper.get_flags_for_ocds_party_identifier(identifier)
        assert any(flag.flag_name == "company_id_invalid" for flag in flags)

    def test_get_flags_for_ocid(self):
        ocid = "ocds-123abc-PROC-20-0001"
        flags = self.flag_helper.get_flags_for_ocid(ocid)
        assert any(flag.flag_name == "person_in_multiple_applications_to_tender" for flag in flags)
        assert any(flag.flag_name == "company_in_multiple_applications_to_tender" for flag in flags)

    def test_get_flags_for_bods_identifier(self):
        identifier = {
            "id": "HMCI17014140912423",
            "schemeName": "National ID"
        }
        flags = self.flag_helper.get_flags_for_bods_identifier(identifier)
        assert any(flag.flag_name == "person_id_matches_cabinet_minister" for flag in flags)

    def test_get_flags_for_bods_identifier_with_ocid(self):
        identifier = {
            "id": "HMCI17014140912423",
            "schemeName": "National ID"
        }
        ocid = "ocds-123abc-PROC-20-0001"

        # Test we get back all flags for identifier with and without OCID
        flags = self.flag_helper.get_flags_for_bods_identifier(identifier, ocid)
        assert any(flag.flag_name == "person_in_multiple_applications_to_tender" for flag in flags)
        assert any(flag.flag_name == "person_id_matches_cabinet_minister" for flag in flags)

        # Test we do NOT get flags for identifier where the flag is only for a particular OCID
        flags = self.flag_helper.get_flags_for_bods_identifier(identifier)
        assert not any(flag.flag_name == "person_in_multiple_applications_to_tender" for flag in flags)
        assert any(flag.flag_name == "person_id_matches_cabinet_minister" for flag in flags)

    def test_get_flags_for_bods_entity_or_person(self):
        identifier = {
            "id": "HMCI17014140912423",
            "schemeName": "National ID"
        }
        ocid = "ocds-123abc-PROC-20-0001"
        person = BODSPersonStatement.objects.get(statement_id="019a93f1-e470-42e9-957b-03554681b2e3")

        # Test we get back all flags for identifier with and without OCID
        flags = self.flag_helper.get_flags_for_bods_entity_or_person(person, ocid)
        assert any(flag.flag_name == "person_in_multiple_applications_to_tender" for flag in flags)
        assert any(flag.flag_name == "person_id_matches_cabinet_minister" for flag in flags)

        # Test we do NOT get flags for identifier where the flag is only for a particular OCID
        flags = self.flag_helper.get_flags_for_bods_identifier(identifier)
        assert not any(flag.flag_name == "person_in_multiple_applications_to_tender" for flag in flags)
        assert any(flag.flag_name == "person_id_matches_cabinet_minister" for flag in flags)


class TestBodsHelperFunctions(TestCase):
    upsert_helper = UpsertDataHelpers()
    bods_helper = BodsHelperFunctions()

    def setUp(self):
        ocds_test_file_path = os.path.join(TEST_DATA_PATH, "ocds-b5fd17suppliermatch-b3f725cb-5a11-4a33-9a37-e068bd48b3e0.json")
        bods_test_file_path = os.path.join(TEST_DATA_PATH, "GB-COH_SC115530_bods.json")
        self.upsert_helper.upsert_bods_data(bods_test_file_path)
        self.upsert_helper.upsert_ocds_data(ocds_test_file_path)


    def test_get_tenderer_context(self):
        t = OCDSTenderer.objects.get(
            ocid="ocds-b5fd17suppliermatch-b3f725cb-5a11-4a33-9a37-e068bd48b3e0",
            party_id='4'
        )
        a = self.bods_helper.get_related_bods_data_for_tenderer(t)
        assert a
