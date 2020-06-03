from django.contrib.postgres.fields import JSONField
from django.db import models

from django_pgviews import view as pgviews


class Flag(models.Model):
    """
    Model to store flag definitions

    flag_name: internal id for referencing the flag
    flag_type: warning/error
    flag_text: Text to display to the user about the flag
    flag_field: Associated field the flag is displayed against
    """
    flag_name = models.CharField(primary_key=True, max_length=1024)
    flag_type = models.CharField(
        max_length=255,
        choices=[
           ("warning", "Warning"),
           ("error", "Error")
        ],
    )
    flag_text = models.TextField()
    flag_field = models.CharField(max_length=1024, null=True)

    def __str__(self):
        return self.flag_name

    class Meta:
        app_label = 'bluetail'
        db_table = 'bluetail_flag'


class FlagAttachment(models.Model):
    """
    Model to attach Flags to a person/company identifier
    """
    identifier_schema = models.CharField(max_length=1024)
    identifier_id = models.CharField(max_length=1024)
    flag_name = models.ForeignKey(Flag, on_delete=None)

    def __str__(self):
        return "%s %s %s" % (self.identifier_schema, self.identifier_id, self.flag_name)

    class Meta:
        app_label = 'bluetail'
        db_table = 'bluetail_flag_attachment'
        unique_together = (("identifier_schema", "identifier_id", "flag_name"),)
