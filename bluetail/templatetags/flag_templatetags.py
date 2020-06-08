from django import template

from bluetail.helpers import FlagHelperFunctions

register = template.Library()


@register.simple_tag()
def get_flags(schema, id):
    helper = FlagHelperFunctions()

    flags = helper.get_flags_for_schema_and_id(schema, id)

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
