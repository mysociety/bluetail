"""
A management command to retrieve files uploaded to an S3 bucket using cove-ocds (Silvereye)
"""
import logging
import os
from datetime import datetime, timezone

from django.core.files.storage import get_storage_class
from django.core.management import BaseCommand
from django.conf import settings
from cove.input.models import SuppliedData

from bluetail.helpers import UpsertDataHelpers

logger = logging.getLogger('django')


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """Add dummy example data to database for demo."""
        s3_storage = get_storage_class(settings.S3_FILE_STORAGE)()

        upsert_helper = UpsertDataHelpers()

        # Loop through directories in /media/ on S3 bucket
        directories, filenames = s3_storage.listdir(name=".")
        for id in directories:
            logger.info(id)
            if SuppliedData.objects.filter(id=id):
                logger.info("SuppliedData object already exists.")
                continue
            directories, filenames = s3_storage.listdir(name=id)
            for filename in filenames:
                original_file_path = os.path.join(id, filename)
                logger.info(f"Downloading {original_file_path}")
                filename_root = os.path.splitext(filename)[0]
                created = datetime.strptime(filename_root, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
                supplied_data = SuppliedData(
                    id=id,
                    original_file=original_file_path,
                    created=created
                )
                supplied_data.current_app = "bluetail"
                supplied_data.save()

                package_json = s3_storage._open(original_file_path).read()

                upsert_helper.upsert_ocds_data(package_json, supplied_data=supplied_data)






