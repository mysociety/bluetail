import json
import os

from django.conf import settings
from django.test import TestCase
from bluetail.models import OCDSReleaseJSON

PROTOTYPE_DATA_PATH = os.path.join(settings.BASE_DIR, "data", "prototype")


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
