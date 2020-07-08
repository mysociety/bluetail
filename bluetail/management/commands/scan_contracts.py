from collections import defaultdict

from django.core.management import BaseCommand

from bluetail.helpers import BodsHelperFunctions
from bluetail.models import Flag, FlagAttachment, OCDSParty, OCDSTender

bods_helper = BodsHelperFunctions()


class Command(BaseCommand):
    help = "Scans contracts and flags suspicious entities"

    def handle(self, *args, **kwargs):
        person_in_multiple_applications_to_tender = Flag.objects.get(
            flag_name='person_in_multiple_applications_to_tender')
        company_in_multiple_applications_to_tender = Flag.objects.get(
            flag_name='company_in_multiple_applications_to_tender')
        # Get tender
        for tender in OCDSTender.objects.all():
            # Scan this tender for people that are interested persons at multiple companies.
            people_to_tenderers = defaultdict(lambda: [])
            entities_to_tenderers = defaultdict(lambda: [])

            # Get all tenderers
            tenderers = OCDSParty.objects.filter(
                ocid=tender.ocid, party_role="tenderer")

            for tenderer in tenderers:
                interested_parties = bods_helper.get_related_bods_data_for_tenderer(
                    tenderer)
                for person in interested_parties['interested_persons']:
                    people_to_tenderers[person].append(tenderer)
                for entity in interested_parties['interested_entities']:
                    entities_to_tenderers[entity].append(tenderer)


            people_with_multiple_parties = [
                person for person, parties in people_to_tenderers.items() if len(parties) > 1]

            entities_with_multiple_parties = [
                entity for entity, parties in entities_to_tenderers.items() if len(parties) > 1]

            if len(people_with_multiple_parties) > 0:
                for person in people_with_multiple_parties:
                    self.stdout.write("{}: {} is a beneficial owner of {}\n".format(
                        tender.ocid, person.fullName, [t.party_name for t in people_to_tenderers[person]]))
                    for identifier in person.identifiers_json:
                        self.create_flag_attachment(tender.ocid, identifier, person_in_multiple_applications_to_tender)

            if len(entities_with_multiple_parties) > 0:
                for entity in entities_with_multiple_parties:
                    self.stdout.write("{}: {} is a beneficial owner of {}\n".format(
                        tender.ocid, entity.entity_name, [t.party_name for t in entities_to_tenderers[entity]]))
                    for identifier in entity.identifiers_json:
                        self.create_flag_attachment(tender.ocid, identifier, company_in_multiple_applications_to_tender)

    def create_flag_attachment(self, ocid, identifier, flag):
        fa, created = FlagAttachment.objects.get_or_create(
            ocid=ocid,
            identifier_schemeName=identifier.get('schemeName'),
            identifier_scheme=identifier.get('scheme'),
            identifier_id=identifier.get('id'),
            flag_name=flag
        )
        if created:
            self.stdout.write(
                "successfully created flag for {}\n".format(identifier))
        else:
            self.stdout.write(
                "found existing flag for {}\n".format(identifier))
