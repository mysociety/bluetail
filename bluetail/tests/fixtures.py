import csv
import os

from django.conf import settings

from bluetail import models

PROTOTYPE_DATA_PATH = os.path.join(settings.BLUETAIL_APP_DIR, "data", "prototype", settings.LANGUAGE_CODE)


def insert_flags():
    # Insert Flags
    example_flags_path = os.path.join(PROTOTYPE_DATA_PATH, "flags", "flags.csv")

    with open(example_flags_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            # More concise, Less explicit..
            # models.Flag.objects.update_or_create(defaults=row, **row)
            models.Flag.objects.update_or_create(
                flag_name=row["flag_name"],
                defaults={
                    "flag_name": row["flag_name"],
                    "flag_type": row["flag_type"],
                    "flag_text": row["flag_text"],
                    "flag_field": row["flag_field"],
                }
            )

def insert_flag_attachments():
    # Insert assigned Flags
    example_flags_path = os.path.join(PROTOTYPE_DATA_PATH, "flags", "flag_attachments.csv")

    with open(example_flags_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            flag = models.Flag.objects.get(flag_name=row["flag_name"])
            models.FlagAttachment.objects.update_or_create(
                identifier_schemeName=row.get("identifier_schemeName") or None,
                identifier_scheme=row.get("identifier_scheme") or None,
                identifier_id=row.get("identifier_id") or None,
                ocid=row.get("ocid") or None,
                flag_name=flag,
                defaults={
                    "identifier_schemeName": row.get("identifier_schemeName") or None,
                    "identifier_scheme": row.get("identifier_scheme") or None,
                    "identifier_id": row.get("identifier_id") or None,
                    "ocid": row.get("ocid") or None,
                    "flag_name": flag,
                }
            )
