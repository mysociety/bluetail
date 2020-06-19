import json

from django.core.management import BaseCommand

from bluetail.models import Flag, FlagAttachment


class Command(BaseCommand):
    help = "Create FlagAttachment objects from Popolo JSON"

    def add_arguments(self, parser):
        parser.add_argument('popolo_json_file', nargs=1, type=str)
        parser.add_argument('flag_name', nargs=1, type=str)

    def handle(self, *args, **kwargs):
        file_name = kwargs['popolo_json_file'][0]
        flag_name = kwargs['flag_name'][0]

        with open(file_name) as popolo_json:
            data = json.load(popolo_json)
            for person in data:
                identifiers = person.get('identifiers')
                if not identifiers:
                    continue

                for identifier in identifiers:
                    fa, created = FlagAttachment.objects.get_or_create(
                        identifier_scheme=identifier['scheme'],
                        identifier_id=identifier['identifier'],
                        flag_name=Flag.objects.get(flag_name=flag_name)
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(
                            "{}:{} -> {}\n".format(
                                fa.identifier_scheme,
                                fa.identifier_id,
                                flag_name
                            )
                        ))
                    else:
                        self.stdout.write(self.style.WARNING(
                            "Existing record found for {}:{}".format(
                                identifier['scheme'],
                                identifier['identifier']
                            )
                        ))
