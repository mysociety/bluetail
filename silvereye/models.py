from django.db import models


class PublisherMetrics(models.Model):
    publisher_id = models.TextField(primary_key=True)
    publisher_name = models.TextField(null=True)
    count_lastmonth = models.IntegerField(null=True)
    count_last3months = models.IntegerField(null=True)
    count_last12months = models.IntegerField(null=True)
    average_lastmonth = models.IntegerField(null=True)
    average_last3months = models.IntegerField(null=True)
    average_last12months = models.IntegerField(null=True)

    class Meta:
        app_label = 'silvereye'
        db_table = 'silvereye_publisher_metrics'
