import json
import logging
import os

from django.core.management import BaseCommand
from django.conf import settings
from ocdskit.combine import merge

from bluetail.helpers import UpsertDataHelpers

logger = logging.getLogger('django')

DATA_DIR = os.path.join(settings.BASE_DIR, "data")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """Add dummy example data to database for demo."""

        # Create combined package
        cf_ocds_path = os.path.join(DATA_DIR, "contracts_finder", "ocds")
        package_path = os.path.join(DATA_DIR, "contracts_finder", "package.json")
        def generate_cf():
            for root, dirs, files in os.walk(cf_ocds_path):
                for f in files:
                    if not f.endswith(".json"):
                        continue
                    f_path = os.path.join(root, f)
                    try:
                        ocds_json = json.load(open(f_path))
                        yield ocds_json
                    except:
                        logger.exception("Failed to insert file %s", f_path)

        rp = merge(generate_cf(), return_package=True)

        with open(package_path, 'w') as out:
            for r in rp:
                out.write(json.dumps(r, indent=4))
