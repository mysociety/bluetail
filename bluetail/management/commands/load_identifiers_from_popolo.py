import json

from django.core.management import BaseCommand

from bluetail.models import Flag, ExternalPerson


class Command(BaseCommand):
    help = "Create ExternalPerson objects from Popolo JSON"

    def add_arguments(self, parser):
        parser.add_argument('popolo_json_file', nargs=1, type=str)
        parser.add_argument('flag_name', nargs=1, type=str)

    def handle(self, *args, **kwargs):
        file_name = kwargs['popolo_json_file'][0]
        flag_name = kwargs['flag_name'][0]
        try:
            flag = Flag.objects.get(flag_name=flag_name)
        except Flag.DoesNotExist:
            self.stderr.write(
                "Couldn't find flag with flag_name={}".format(flag_name))
            return

        with open(file_name) as popolo_json:
            data = json.load(popolo_json)
            for person in data:
                identifiers = person.get('identifiers')
                if not identifiers:
                    continue

                for identifier in identifiers:
                    external_person, created = ExternalPerson.objects.get_or_create(
                        name=person['full_name'],
                        scheme=identifier['scheme'],
                        identifier=identifier['identifier'],
                        flag=flag
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(
                            "{}:{} -> {}\n".format(
                                external_person.scheme,
                                external_person.identifier,
                                external_person.flag.flag_name
                            )
                        ))
                    else:
                        self.stdout.write(self.style.WARNING(
                            "Existing record found for {}:{}".format(
                                identifier['scheme'],
                                identifier['identifier']
                            )
                        ))
