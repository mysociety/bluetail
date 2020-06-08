import csv
import os

from django.conf import settings

from bluetail import models


def insert_flags():
    # Insert Flags
    example_flags_path = os.path.join(settings.BASE_DIR, "example_files", "flags", "flags.csv")

    with open(example_flags_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            models.Flag.objects.update_or_create(defaults=row, **row)
            # models.Flag.objects.update_or_create(
            #     flag_name=row["flag_name"],
            #     defaults={
            #         "flag_name": row["flag_name"],
            #         "flag_type": row["flag_type"],
            #         "flag_text": row["flag_text"],
            #     }
            # )

def insert_flag_attachments():
    # Insert assigned Flags
    example_flags_path = os.path.join(settings.BASE_DIR, "example_files", "flags", "flag_attachments.csv")

    with open(example_flags_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            flag = models.Flag.objects.get(flag_name=row["flag_name"])
            models.FlagAttachment.objects.update_or_create(
                identifier_scheme=row["identifier_scheme"],
                identifier_id=row["identifier_id"],
                flag_name=flag,
                defaults={
                    "identifier_scheme": row["identifier_scheme"],
                    "identifier_id": row["identifier_id"],
                    "flag_name": flag,
                }
            )
