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
    Model to attach Flags to a person/company/ocid identifier
    """
    ocid = models.CharField(max_length=1024, null=True)
    identifier_schemeName = models.CharField(max_length=1024, null=True)
    identifier_scheme = models.CharField(max_length=1024, null=True)
    identifier_id = models.CharField(max_length=1024, null=True)
    flag_name = models.ForeignKey(Flag, on_delete=None)

    def __str__(self):
        return "%s %s %s" % (self.identifier_scheme, self.identifier_id, self.flag_name)

    class Meta:
        app_label = 'bluetail'
        db_table = 'bluetail_flag_attachment'
        unique_together = (("ocid", "identifier_schemeName", "identifier_scheme", "identifier_id", "flag_name"),)


class ExternalPerson(models.Model):
    """
    ExternalPerson stores information about an external person, along with the
    flag name that they apply to.
    """
    scheme = models.CharField(max_length=1024)
    name = models.CharField(max_length=1024)
    identifier = models.CharField(max_length=1024)
    date_of_birth = models.DateField(null=True)
    flag = models.ForeignKey(Flag, on_delete=None)

    def __str__(self):
        return "%s (%s)" % (self.name, self.flag)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'scheme', 'identifier', 'flag'], name='unique_person_flag')
        ]
