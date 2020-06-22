import json
import logging
import os

from bluetail import models
from bluetail.models import FlagAttachment, Flag, BODSEntityStatement, BODSOwnershipStatement, BODSPersonStatement, OCDSReleaseJSON

logger = logging.getLogger(__name__)


class FlagHelperFunctions():
    def get_flags_for_scheme_and_id(self, identifier_scheme, identifier_id):
        """
        Gets all flags associated with a scheme/id of a person/company/etc.
        """
        flag_attachments = FlagAttachment.objects.filter(
            identifier_scheme=identifier_scheme,
            identifier_id=identifier_id,
        )
        flags = []
        for flag_attachment in flag_attachments:
            flag = Flag.objects.get(flag_name=flag_attachment.flag_name)
            flags.append(flag)
        return flags

    def get_flags_for_bods_entity_or_person(self, object):
        flags = []
        for identifier in object.identifiers_json:
            id_flags = self.get_flags_for_scheme_and_id(
                identifier.get("scheme"),
                identifier.get("id"),
            )
            flags.extend(id_flags)

        return flags

    def get_flags_for_ocds_party(self, object):
        flags = []

        flags.extend(self.get_flags_for_scheme_and_id(
            object.party_identifier_scheme,
            object.party_identifier_id,
        ))

        for identifier in object.party_json.get("additionalIdentifiers", []):
            id_flags = self.get_flags_for_scheme_and_id(
                identifier.get("scheme"),
                identifier.get("id"),
            )
            flags.extend(id_flags)

        return flags

    def build_flags_context(self, flags):

        company_id_flags = [flag for flag in flags if flag.flag_field == "company_id"]
        person_id_flags = [flag for flag in flags if flag.flag_field == "person_id"]
        jurisdiction_flags = [flag for flag in flags if flag.flag_field == "jurisdiction"]

        flags_dict = {
            "flags": flags,
            "total_errors": sum([1 for flag in flags if flag.flag_type == "error"]),
            "total_warnings": sum([1 for flag in flags if flag.flag_type == "warning"]),
            "company_id_flags": {
                "error": [flag for flag in company_id_flags if flag.flag_type == "error"],
                "warning": [flag for flag in company_id_flags if flag.flag_type == "warning"],
            },
            "person_id_flags": {
                "error": [flag for flag in person_id_flags if flag.flag_type == "error"],
                "warning": [flag for flag in person_id_flags if flag.flag_type == "warning"],
            },
            "jurisdiction_flags": {
                "error": [flag for flag in jurisdiction_flags if flag.flag_type == "error"],
                "warning": [flag for flag in jurisdiction_flags if flag.flag_type == "warning"],
            },
        }

        return flags_dict


class BodsHelperFunctions():

    def get_related_bods_data_for_tenderer(self, tenderer):

        interested_persons = []
        interested_entities = []

        entity_statments = BODSEntityStatement.objects.filter(identifiers_json__contains=[{'scheme': tenderer.party_identifier_scheme, 'id': tenderer.party_identifier_id}])

        if entity_statments:
            for entity_statment in entity_statments:
                ownership_statements = BODSOwnershipStatement.objects.filter(subject_entity_statement=entity_statment.statement_id)
                if ownership_statements:
                    for ownership_statement in ownership_statements:
                        interested_person_statement_id = ownership_statement.interested_person_statement_id
                        interested_entity_statement_id = ownership_statement.interested_entity_statement_id
                        if interested_person_statement_id:
                            interested_person = BODSPersonStatement.objects.get(statement_id=interested_person_statement_id)
                            interested_persons.append(interested_person)
                        if interested_entity_statement_id:
                            interested_entity = BODSEntityStatement.objects.get(statement_id=interested_entity_statement_id)
                            interested_entities.append(interested_entity)

        interested_parties = {
           "interested_persons": interested_persons,
           "interested_entities": interested_entities,
        }

        return interested_parties


class ContextHelperFunctions():

    def get_tenderer_context(self, tenderer):

        bods_helper = BodsHelperFunctions()
        flags_helper = FlagHelperFunctions()

        tenderer_context = {
            "ocid": tenderer.ocid,
            "party_id": tenderer.party_id,
            "party_name": tenderer.party_name,
            "object": tenderer,
        }

        warnings = []
        errors = []

        tenderer_flags = flags_helper.get_flags_for_ocds_party(tenderer)
        for flag in tenderer_flags:
            if flag.flag_type == "warning":
                warnings.append(flag)
            elif flag.flag_type == "error":
                errors.append(flag)

        interested_parties = bods_helper.get_related_bods_data_for_tenderer(tenderer)
        for person in interested_parties["interested_persons"]:
            person_flags = flags_helper.get_flags_for_bods_entity_or_person(person)
            if person_flags:
                for flag in person_flags:
                    if flag.flag_type == "warning":
                        warnings.append(flag)
                    elif flag.flag_type == "error":
                        errors.append(flag)
        for entity in interested_parties["interested_entities"]:
            entity_flags = flags_helper.get_flags_for_bods_entity_or_person(entity)
            if entity_flags:
                for flag in entity_flags:
                    if flag.flag_type == "warning":
                        warnings.append(flag)
                    elif flag.flag_type == "error":
                        errors.append(flag)

        tenderer_context["warnings"] = warnings
        tenderer_context["errors"] = errors

        tenderer_context["total_warnings"] = len(warnings)
        tenderer_context["total_errors"] = len(errors)

        return tenderer_context


class UpsertDataHelpers:

    def upsert_ocds_data(self, ocds_json_path_or_string):
        """
        Takes a path to an OCDS Package or a stringn containing OCDS JSON data
        Upserts all releases to the Bluetail database
        """
        if os.path.exists(ocds_json_path_or_string):
            ocds_json = json.load(open(ocds_json_path_or_string))
        else:
            ocds_json = json.loads(ocds_json_path_or_string)

        ocds_releases = []

        if ocds_json.get("records"):
            # We have a record package
            for record in ocds_json["records"]:
                compiledRelease = record["compiledRelease"]
                ocds_releases.append(compiledRelease)

        if ocds_json.get("releases"):
            # We have a release package
            for release in ocds_json["releases"]:
                ocds_releases.append(release)

        for release_json in ocds_releases:
            OCDSReleaseJSON.objects.update_or_create(
                ocid=release_json.get("ocid"),
                defaults={
                    "release_id": release_json.get("id"),
                    "release_json": release_json,
                }

            )

    def upsert_bods_data(self, bods_json_path_or_string):
        """
        Takes a path to an BODS JSON or a string containing BODS JSON statement array
        Upserts all statements to the Bluetail database
        """

        if os.path.exists(bods_json_path_or_string):
            bods_json = json.load(open(bods_json_path_or_string))
        else:
            bods_json = json.loads(bods_json_path_or_string)

        for statement in bods_json:
            statement_id = statement.get("statementID")
            statement_type = statement.get("statementType")
            logger.info("Inserting statement: %s %s", statement_id, statement_type)

            models.BODSStatementJSON.objects.update_or_create(
                statement_id=statement_id,
                defaults={
                    "statement_json": statement,
                }
            )
