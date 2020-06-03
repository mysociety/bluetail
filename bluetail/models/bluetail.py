from django.contrib.postgres.fields import JSONField
from django.db import models

from django_pgviews import view as pgviews


class Flags(models.Model):
    """
    WIP model to store warnings and alerts
    """
    data_type = models.TextField()
    data_id = models.TextField()
    flag_type = models.TextField()
    flag_text = models.TextField()

    class Meta:
        app_label = 'bluetail'
        db_table = 'bluetail_flags'

