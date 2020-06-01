from django.contrib.postgres.fields import JSONField
from django.db import models

from django_pgviews import view as pgviews


class OCDSReleaseJSON(models.Model):
    ocid = models.TextField(primary_key=True)
    release_id = models.TextField()
    release_json = JSONField(null=True)

    def __unicode__(self):
        return self.release_json

    class Meta:
        app_label = 'bluetail'
        db_table = 'bluetail_ocds_release_json'


class OCDSReleaseView(pgviews.View):
    # dependencies = ['bluetail.OtherView',]
    ocid = models.TextField(primary_key=True)
    release_id = models.TextField()
    release_json = JSONField(null=True)
    title = models.TextField()
    description = models.TextField()

    sql = """
        SELECT 
            t.ocid,
            t.release_id,
            t.release_json -> 'tender' ->> 'title' AS title,
            t.release_json -> 'tender' ->> 'description' AS description,
            t.release_json
        FROM bluetail_ocds_release_json t
        """

    class Meta:
        app_label = 'bluetail'
        db_table = 'bluetail_ocds_release_view'
        managed = False
