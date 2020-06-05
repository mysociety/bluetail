
from bluetail.models import FlagAttachment, Flag, BODSEntityStatement, BODSOwnershipStatement, BODSPersonStatement


class FlagHelperFunctions():

    def get_flags_for_schema_and_id(self, identifier_scheme, identifier_id):
        """
        Gets all flags associated with a schema/id of a person/company/etc.

        TODO Tidy flag field
        Appends the `field` attribute in a slightly hacky way until we decide better
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


class BodsHelperFunctions():

    def get_related_bods_data_for_tenderer(self, tenderer):

        interested_persons = []
        interested_entities = []

        entity_statments = BODSEntityStatement.objects.filter(
            # identifiers_0_scheme=tenderer.party_identifier_scheme,
            identifiers_0_id=tenderer.party_identifier_id
        )

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
        }

        warnings = []
        errors = []

        tenderer_flags = flags_helper.get_flags_for_schema_and_id(tenderer.party_identifier_scheme, tenderer.party_identifier_id)
        for flag in tenderer_flags:
            if flag.flag_type == "warning":
                warnings.append(flag)
            elif flag.flag_type == "error":
                errors.append(flag)

        interested_parties = bods_helper.get_related_bods_data_for_tenderer(tenderer)
        for person in interested_parties["interested_persons"]:
            person_flags = flags_helper.get_flags_for_schema_and_id(person.identifiers_0_scheme, person.identifiers_0_id)
            if person_flags:
                for flag in person_flags:
                    if flag.flag_type == "warning":
                        warnings.append(flag)
                    elif flag.flag_type == "error":
                        errors.append(flag)
        for entity in interested_parties["interested_entities"]:
            entity_flags = flags_helper.get_flags_for_schema_and_id(entity.identifiers_0_scheme, entity.identifiers_0_id)
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
