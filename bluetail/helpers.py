import json
import logging
import os
from copy import deepcopy

from django.db.models import Q
from cove.input.models import SuppliedData
from ocdskit.combine import merge

from bluetail import models
from bluetail.models import FlagAttachment, Flag, BODSEntityStatement, BODSOwnershipStatement, BODSPersonStatement, OCDSReleaseJSON, OCDSPackageDataJSON, OCDSRecordJSON

logger = logging.getLogger('django')


class FlagHelperFunctions():
    def get_flags_for_ocds_party_identifier(self, identifier, ocid=None):
        """
        Gets all flags associated with a OCDS Party identifier using scheme/id
        """
        if ocid:
            flags = Flag.objects.filter(Q(
                flagattachment__identifier_scheme=identifier.get("scheme"),
                flagattachment__identifier_id=identifier.get("id"),
                flagattachment__ocid=ocid,
            ) | Q(
                flagattachment__identifier_scheme=identifier.get("scheme"),
                flagattachment__identifier_id=identifier.get("id"),
                flagattachment__ocid__isnull=True,
            ))
        else:
            flags = Flag.objects.filter(
                flagattachment__identifier_scheme=identifier.get("scheme"),
                flagattachment__identifier_id=identifier.get("id"),
            )
        return flags

    def get_flags_for_ocid(self, ocid):
        """
        Gets all flags associated with a OCID
        """
        flags = Flag.objects.filter(
            flagattachment__ocid=ocid,
        )
        return flags

    def get_flags_for_bods_identifier(self, identifier, ocid=None):
        """
        Gets all flags associated with a BODS identifier, using any combination of scheme/schemeName/id
        """
        if ocid:
            flags = Flag.objects.filter(Q(
                flagattachment__identifier_scheme=identifier.get("scheme"),
                flagattachment__identifier_id=identifier.get("id"),
                flagattachment__identifier_schemeName=identifier.get("schemeName"),
                flagattachment__ocid=ocid,
            ) | Q(
                flagattachment__identifier_scheme=identifier.get("scheme"),
                flagattachment__identifier_id=identifier.get("id"),
                flagattachment__identifier_schemeName=identifier.get("schemeName"),
                flagattachment__ocid__isnull=True,
            ))
        else:
            flags = Flag.objects.filter(
                flagattachment__identifier_scheme=identifier.get("scheme"),
                flagattachment__identifier_id=identifier.get("id"),
                flagattachment__identifier_schemeName=identifier.get("schemeName"),
                flagattachment__ocid__isnull=True,
            )
        return flags

    def get_flags_for_bods_entity_or_person(self, object, ocid=None):
        flags = []
        for identifier in object.identifiers_json:
            id_flags = self.get_flags_for_bods_identifier(identifier, ocid=ocid)
            flags.extend(id_flags)
        return list(set(flags))

    def get_flags_for_ocds_party(self, object):
        flags = []

        primary_identifier = object.party_json.get("identifier")
        flags.extend(self.get_flags_for_ocds_party_identifier(primary_identifier, ocid=object.ocid))

        for identifier in object.party_json.get("additionalIdentifiers", []):
            id_flags = self.get_flags_for_ocds_party_identifier(identifier, ocid=object.ocid)
            flags.extend(id_flags)
        return list(set(flags))

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
            person_flags = flags_helper.get_flags_for_bods_entity_or_person(person, ocid=tenderer.ocid)
            if person_flags:
                for flag in person_flags:
                    if flag.flag_type == "warning":
                        warnings.append(flag)
                    elif flag.flag_type == "error":
                        errors.append(flag)
        for entity in interested_parties["interested_entities"]:
            entity_flags = flags_helper.get_flags_for_bods_entity_or_person(entity, ocid=tenderer.ocid)
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
    def upload_record_package(self, package_json, supplied_data=None):
        """
        Upload a record package
            creates a SuppliedData object if not given
            creates a OCDSPackageDataJSON object
        """
        if not supplied_data:
            supplied_data = SuppliedData()
            supplied_data.current_app = "bluetail"
            supplied_data.save()
        package_data = deepcopy(package_json)
        records = package_data.pop("records")
        package, created = OCDSPackageDataJSON.objects.update_or_create(
            supplied_data=supplied_data,
            package_data=package_data
        )

        for record in records:
            ocid = record.get("ocid")
            record_json, created = OCDSRecordJSON.objects.update_or_create(
                ocid=ocid,
                defaults={
                    "record_json": record,
                    "package_data": package,

                }
            )

    def upsert_ocds_data(self, ocds_json_path_or_string):
        """
        Takes a path to an OCDS Package or a string containing OCDS JSON data
        Upserts all data to the Bluetail database
        """
        if os.path.exists(ocds_json_path_or_string):
            ocds_json = json.load(open(ocds_json_path_or_string))
        else:
            ocds_json = json.loads(ocds_json_path_or_string)

        if ocds_json.get("records"):
            # We have a record package
            self.upload_record_package(ocds_json)

        if ocds_json.get("releases"):
            # We have a release package
            # First we use OCDSkit merge to create a record package
            rp = merge([ocds_json], published_date=ocds_json.get("publishedDate"), return_package=True)
            # Then upload the package
            for r in rp:
                self.upload_record_package(r)

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
            logger.debug("Inserting statement: %s %s", statement_id, statement_type)

            models.BODSStatementJSON.objects.update_or_create(
                statement_id=statement_id,
                defaults={
                    "statement_json": statement,
                }
            )
