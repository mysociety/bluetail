import json
import os

from django.core.management import BaseCommand
from django.conf import settings

from bluetail.models import OCDSReleaseJSON


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """Add dummy example data to database for demo."""

        example_ocds_path = os.path.join(settings.BASE_DIR, "example_files", "ocds_tenderers.json")
        example_ocds_json = json.load(open(example_ocds_path))
        OCDSReleaseJSON.objects.create(
            ocid="ocds-123abc-PROC-20-0001",
            release_id="PROC-20-0001-02-tender",
            release_json=example_ocds_json
        )



