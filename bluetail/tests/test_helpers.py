import csv
import os

from django.conf import settings
from django.test import TestCase

from bluetail import models
from bluetail.helpers import FlagHelperFunctions
from bluetail.tests.fixtures import insert_flags, insert_flag_attachments


class TestFlagHelperFunctions(TestCase):
    helper = FlagHelperFunctions()

    def setUp(self):
        insert_flags()
        insert_flag_attachments()

    def test_get_flags_for_ocds_party_identifier(self):
        identifier = {
            "scheme": "GB-LAC",
            "id": "1602647563",
            "legalName": "Synomus Technology Services Ltd."
        }
        flags = self.helper.get_flags_for_ocds_party_identifier(identifier)
        assert any(flag.flag_name == "company_id_invalid" for flag in flags)

    def test_get_flags_for_ocid(self):
        ocid = "ocds-123abc-PROC-20-0001"
        flags = self.helper.get_flags_for_ocid(ocid)
        assert any(flag.flag_name == "person_in_multiple_applications_to_tender" for flag in flags)
        assert any(flag.flag_name == "company_in_multiple_applications_to_tender" for flag in flags)

    def test_get_flags_for_bods_identifier(self):
        identifier = {
            "id": "HMCI17014140912423",
            "schemeName": "National ID"
        }
        flags = self.helper.get_flags_for_bods_identifier(identifier)
        assert any(flag.flag_name == "person_in_multiple_applications_to_tender" for flag in flags)

    def test_get_flags_for_bods_identifier_with_ocid(self):
        identifier = {
            "id": "HMCI17014140912423",
            "schemeName": "National ID"
        }
        ocid = "ocds-123abc-PROC-20-0001"

        # Test we get back all flags for identifier with and without OCID
        flags = self.helper.get_flags_for_bods_identifier(identifier, ocid)
        assert any(flag.flag_name == "person_in_multiple_applications_to_tender" for flag in flags)
        assert any(flag.flag_name == "person_id_matches_cabinet_minister" for flag in flags)

        # Test we do NOT get flags for identifier where the flag is only for a particular OCID
        flags = self.helper.get_flags_for_bods_identifier(identifier)
        assert not any(flag.flag_name == "person_in_multiple_applications_to_tender" for flag in flags)
        assert any(flag.flag_name == "person_id_matches_cabinet_minister" for flag in flags)
