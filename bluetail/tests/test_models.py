import json
import os

# from django.conf import settings
from django.test import TestCase
from bluetail.models import OCDSReleaseJSON

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class OcdsReleaseTestCase(TestCase):
    def setUp(self):
        example_ocds_path = os.path.join(BASE_DIR, "../../example_files", "ocds_tenderers.json")
        example_ocds_json = json.load(open(example_ocds_path))

        OCDSReleaseJSON.objects.create(
            ocid="ocds-123abc-PROC-20-0001",
            release_id="PROC-20-0001-02-tender",
            release_json=example_ocds_json
        )

    def test_release(self):
        release = OCDSReleaseJSON.objects.get(name="ocds-123abc-PROC-20-0001")
        self.assertEqual(release.release_id, "PROC-20-0001-02-tender")
