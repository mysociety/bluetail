import json
import os

from django.conf import settings
from django.test import TestCase

from bluetail.helpers import UpsertDataHelpers
from bluetail.models import OCDSReleaseJSON, BODSStatementJSON, BODSEntityStatement, BODSPersonStatement
from bluetail.tests.fixtures import insert_flags, insert_flag_attachments

PROTOTYPE_DATA_PATH = os.path.join(settings.BASE_DIR, "data", "prototype")
TEST_DATA_PATH = os.path.join(settings.BASE_DIR, "bluetail", "tests", "data")


class OcdsReleaseTestCase(TestCase):
    def setUp(self):
        example_ocds_path = os.path.join(PROTOTYPE_DATA_PATH, "ocds", "ocds_tenderers_package.json")
        example_ocds_json = json.load(open(example_ocds_path))
        example_ocds_json = example_ocds_json["releases"][0]

        OCDSReleaseJSON.objects.update_or_create(
            ocid=example_ocds_json.get("ocid"),
            defaults={
                "release_id": example_ocds_json.get("id"),
                "release_json": example_ocds_json,
            }

        )

    def test_release(self):
        release = OCDSReleaseJSON.objects.get(ocid="ocds-123abc-PROC-20-0001")
        self.assertEqual(release.release_id, "PROC-20-0001-02-tender")


class BODSEntityStatementTestCase(TestCase):
    def setUp(self):
        json_path = os.path.join(TEST_DATA_PATH, "GB-COH_00088456_bods.json")
        UpsertDataHelpers().upsert_bods_data(json_path)

    def test_release(self):
        statement = BODSEntityStatement.objects.get(statement_id="openownership-register-4501624486344343879")
        self.assertEqual(statement.entity_name, "INTERSERVE PLC")

    def test_CH_id(self):
        ch_id = "00088456"
        entity_statments = BODSEntityStatement.objects.filter(identifiers_json__contains=[{'scheme': 'GB-COH', 'id': ch_id}])
        assert any(s.statement_id == "openownership-register-4501624486344343879" for s in entity_statments)


class BODSPersonStatementTestCase(TestCase):
    def setUp(self):
        insert_flags()
        insert_flag_attachments()
        bods_test_file_path = os.path.join(PROTOTYPE_DATA_PATH, "bods", "PROC-20-0001", "d_ownership.json")
        UpsertDataHelpers().upsert_bods_data(bods_test_file_path)
        bods_test_file_path = os.path.join(PROTOTYPE_DATA_PATH, "bods", "PROC-20-0001", "c_ownership.json")
        UpsertDataHelpers().upsert_bods_data(bods_test_file_path)

    def test_filter_bods_using_identifier(self):
        identifier = {
            "id": "HMCI17014140912423",
            "schemeName": "National ID"
        }
        p = BODSPersonStatement.objects.filter(identifiers_json__contains=[identifier])
        assert len(p) == 2
