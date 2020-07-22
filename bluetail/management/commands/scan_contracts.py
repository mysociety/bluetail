import logging
from collections import defaultdict

from django.core.management import BaseCommand

from bluetail import helpers
from bluetail.helpers import BodsHelperFunctions
from bluetail.models import Flag, FlagAttachment, OCDSTenderer, OCDSTender, ExternalPerson, BODSPersonStatement

logger = logging.getLogger('django')

bods_helper = BodsHelperFunctions()


class Command(BaseCommand):
    help = "Scans contracts and flags suspicious entities"

    def handle(self, *args, **kwargs):
        self.flag_within_contracts()
        self.flag_external_people()
        self.flag_tenders_linked_to_external_people()

    def flag_within_contracts(self):
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
            tenderers = OCDSTenderer.objects.filter(
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
                    logger.info("{}: {} is a beneficial owner of {}".format(
                        tender.ocid, person.fullName, [t.party_name for t in people_to_tenderers[person]]))
                    for identifier in person.identifiers_json:
                        self._create_flag_attachment(tender.ocid, identifier, person_in_multiple_applications_to_tender)

            if len(entities_with_multiple_parties) > 0:
                for entity in entities_with_multiple_parties:
                    logger.info("{}: {} is a beneficial owner of {}".format(
                        tender.ocid, entity.entity_name, [t.party_name for t in entities_to_tenderers[entity]]))
                    for identifier in entity.identifiers_json:
                        self._create_flag_attachment(tender.ocid, identifier, company_in_multiple_applications_to_tender)

    def flag_external_people(self):
        people = BODSPersonStatement.objects.all()
        for person in people:
            for identifier in person.identifiers_json:
                external_people = ExternalPerson.match(
                    scheme=identifier['schemeName'],
                    identifier=identifier['id']
                )
                if external_people:
                    for external_person in external_people:
                        fa, created = FlagAttachment.objects.get_or_create(
                            identifier_schemeName=external_person.scheme,
                            identifier_id=external_person.identifier,
                            flag_name=external_person.flag
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(
                                "{}:{} -> {}\n".format(
                                    fa.identifier_schemeName,
                                    fa.identifier_id,
                                    fa.flag_name
                                )
                            ))
                        else:
                            self.stdout.write(self.style.WARNING(
                                "Existing record found for {}:{}".format(
                                    external_person.scheme,
                                    external_person.identifier
                                )
                            ))

    def flag_tenders_linked_to_external_people(self):
        people = BODSPersonStatement.objects.all()
        for person in people:
            for identifier in person.identifiers_json:
                external_people = ExternalPerson.match(
                    scheme=identifier['schemeName'],
                    identifier=identifier['id']
                )
                if external_people:
                    related_ocids = helpers.BodsHelperFunctions().get_related_tender_ocids_for_bods_person(person)
                    for external_person in external_people:
                        for ocid in related_ocids:
                            fa, created = FlagAttachment.objects.get_or_create(
                                ocid=ocid,
                                identifier_schemeName=external_person.scheme,
                                identifier_id=external_person.identifier,
                                flag_name=external_person.flag
                            )
                            if created:
                                self.stdout.write(self.style.SUCCESS(
                                    "{}:{}:{} -> {}\n".format(
                                        ocid,
                                        fa.identifier_schemeName,
                                        fa.identifier_id,
                                        fa.flag_name
                                    )
                                ))
                            else:
                                self.stdout.write(self.style.WARNING(
                                    "Existing record found for {}:{}".format(
                                        external_person.scheme,
                                        external_person.identifier
                                    )
                                ))


    def _create_flag_attachment(self, ocid, identifier, flag):
        fa, created = FlagAttachment.objects.get_or_create(
            ocid=ocid,
            identifier_schemeName=identifier.get('schemeName'),
            identifier_scheme=identifier.get('scheme'),
            identifier_id=identifier.get('id'),
            flag_name=flag
        )
        if created:
            logger.info("successfully created flag for {}".format(identifier))
        else:
            logger.info("found existing flag for {}".format(identifier))
