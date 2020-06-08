import json
import logging
import os

from django.core.management import BaseCommand
from django.conf import settings

from bluetail import models
from bluetail.tests.fixtures import insert_flags, insert_flag_attachments

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """Add dummy example data to database for demo."""
        # Insert OCDS JSON
        example_ocds_path = os.path.join(settings.BASE_DIR, "example_files", "ocds_tenderers.json")
        example_ocds_json = json.load(open(example_ocds_path))

        logger.info("Insert sample OCDS")
        models.OCDSReleaseJSON.objects.update_or_create(
            ocid=example_ocds_json.get("ocid"),
            defaults={
                "release_id": example_ocds_json.get("id"),
                "release_json": example_ocds_json,
            }
        )

        # Insert BODS JSON
        logger.info("Insert sample BODS")
        example_bods_path = os.path.join(settings.BASE_DIR, "example_files", "PROC-20-0001")
        files = os.listdir(example_bods_path)

        for f in files:
            try:
                f_path = os.path.join(example_bods_path, f)
                f_json = json.load(open(f_path))
                for statement in f_json:
                    statement_id = statement.get("statementID")
                    statement_type = statement.get("statementType")
                    logger.info("Inserting statement: %s %s", statement_id, statement_type)
                    if statement_type == "entityStatement":
                        models.BODSEntityStatementJSON.objects.update_or_create(
                            statement_id=statement_id,
                            defaults={
                                # "statement_id": statement_id,
                                "statement_json": statement,
                            }
                        )
                    elif statement_type == 'ownershipOrControlStatement':
                        models.BODSOwnershipStatementJSON.objects.update_or_create(
                            statement_id=statement_id,
                            defaults={
                                # "statement_id": statement.get("statementID"),
                                "statement_json": statement,
                            }
                        )
                    elif statement_type == "personStatement":
                        models.BODSPersonStatementJSON.objects.update_or_create(
                            statement_id=statement_id,
                            defaults={
                                # "statement_id": statement.get("statementID"),
                                "statement_json": statement,
                            }
                        )

            except:
                logger.exception("Failed to insert example file %s", f_path)

        # Insert Flags
        logger.info("Insert sample Flags")
        insert_flags()

        # Insert assigned Flags
        logger.info("Insert sample FlagAttachments")
        insert_flag_attachments()
