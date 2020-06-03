
from bluetail.models import FlagAttachment, Flag


class FlagHelperFunctions():

    def get_flags_for_schema_and_id(self, identifier_schema, identifier_id):
        """
        Gets all flags associated with a schema/id of a person/company/etc.

        TODO Tidy flag field
        Appends the `field` attribute in a slightly hacky way until we decide better
        """

        flag_attachments = FlagAttachment.objects.filter(
            identifier_schema=identifier_schema,
            identifier_id=identifier_id,
        )

        flags = []

        for flag_attachment in flag_attachments:
            flag = Flag.objects.get(flag_name=flag_attachment.flag_name)

            flags.append(flag)

        return flags

