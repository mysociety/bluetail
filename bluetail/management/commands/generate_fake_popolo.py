import json
import random

from django.core.management import BaseCommand

from bluetail.models import Flag, FlagAttachment, ExternalPerson, BODSPersonStatement


class Command(BaseCommand):
    help = "Uses existing BODS data to generate fake popolo data for testing"

    def handle(self, *args, **kwargs):
        people = BODSPersonStatement.objects.all()
        popolo_people = []
        for person in people:
            popolo_people.append({
                'full_name': person.fullName,
                'identifiers': [
                    {'scheme': identifier['schemeName'], 'identifier': identifier['id']} for identifier in person.identifiers_json
                ]
            })

        # Take 10 random people
        print(json.dumps(random.sample(popolo_people, 10), indent=4))
