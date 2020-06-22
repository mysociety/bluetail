from django import template

from bluetail.helpers import FlagHelperFunctions

register = template.Library()

helper = FlagHelperFunctions()


@register.simple_tag()
def get_flags_for_bods_entity_or_person(object):
    flags = helper.get_flags_for_bods_entity_or_person(object)
    flags_context = helper.build_flags_context(flags)
    return flags_context


@register.simple_tag()
def get_flags_for_ocds_party(object):
    flags = helper.get_flags_for_ocds_party(object)
    flags_context = helper.build_flags_context(flags)
    return flags_context
