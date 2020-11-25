import csv
import glob
import logging
import os

from django.core.management import BaseCommand
from django.conf import settings

logger = logging.getLogger('django')

DATA_DIR = os.path.join(settings.BLUETAIL_APP_DIR, "data")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('people_translations', nargs=1, type=str)
        parser.add_argument('company_translations', nargs=1, type=str)
        parser.add_argument('tender_translations', nargs=1, type=str)
        parser.add_argument('flag_translations', nargs=1, type=str)
        parser.add_argument('language', nargs=1, type=str)

    def handle(self, *args, **kwargs):
        """Localise prototype data using a spreadsheet of translations"""

        prototype_data_dir = os.path.join(
            DATA_DIR,
            "prototype",
            kwargs['language'][0]
        )
        bods_dir = os.path.join(prototype_data_dir, "bods", "PROC-20-0001")
        flags_dir = os.path.join(prototype_data_dir, "flags")
        ocds_dir = os.path.join(prototype_data_dir, "ocds")

        bods_files = glob.glob(os.path.join(bods_dir, '*.json'))
        ocds_files = glob.glob(os.path.join(ocds_dir, '*.json'))

        bods_ocds_replacements = []
        flag_replacements = []
        tender_replacements = []

        language = kwargs['language'][0]

        with(open(kwargs['people_translations'][0])) as people_translations:
            reader = csv.DictReader(people_translations)
            for row in reader:
                if(row['en'] != ''):
                    bods_ocds_replacements.append((row['en'], row[language]))

        with(open(kwargs['company_translations'][0])) as company_translations:
            reader = csv.DictReader(company_translations)
            for row in reader:
                if(row['en'] != ''):
                    bods_ocds_replacements.append((row['en'], row[language]))

        with(open(kwargs['tender_translations'][0])) as tender_translations:
            reader = csv.DictReader(tender_translations)
            for row in reader:
                if(row['en'] != ''):
                    tender_replacements.append((row['en'], row[language]))

        with(open(kwargs['flag_translations'][0])) as flag_translations:
            reader = csv.DictReader(flag_translations)
            for row in reader:
                if(row['en'] != ''):
                    flag_replacements.append((row['en'], row[language]))

        for file in bods_files:
            with(open(file, 'r')) as bods_file:
                contents = bods_file.read()
                for original, replacement in bods_ocds_replacements:
                    contents = contents.replace(original, replacement)
            with(open(file, 'w')) as bods_file:
                bods_file.write(contents)

        for file in ocds_files:
            with(open(file, 'r')) as ocds_file:
                contents = ocds_file.read()
                for original, replacement in bods_ocds_replacements:
                    contents = contents.replace(original, replacement)
                for original, replacement in tender_replacements:
                    contents = contents.replace(original, replacement)
            with(open(file, 'w')) as ocds_file:
                ocds_file.write(contents)

        with(open(os.path.join(flags_dir, 'flags.csv'), 'r')) as flags_file:
            contents = flags_file.read()
            for original, replacement in flag_replacements:
                contents = contents.replace(original, replacement)
        with(open(os.path.join(flags_dir, 'flags.csv'), 'w')) as flags_file:
            flags_file.write(contents)
