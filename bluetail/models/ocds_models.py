from django.contrib.postgres.fields import JSONField
from django.db import models

from django_pgviews import view as pgviews


class OCDSReleaseJSON(models.Model):
    """
    Model to store OCDS JSON releases.
    OCID must be unique so multiple releases for a single OCID should be compiled before insertion.
    """
    ocid = models.TextField(primary_key=True)
    release_id = models.TextField()
    release_json = JSONField()

    class Meta:
        app_label = 'bluetail'
        db_table = 'bluetail_ocds_release_json'


class OCDSTender(pgviews.View):
    """
    View for extracting Tender details from an OCDSReleaseJSON object
    Tender as from an OCDS version 1.1 release
    https://standard.open-contracting.org/latest/en/schema/reference/#tender
    """
    # projection = ['bluetail.OCDSReleaseJSON.*', ]
    # dependencies = ['bluetail.OtherView',]
    ocid = models.TextField(primary_key=True)
    release_id = models.TextField()
    release_json = JSONField(null=True)
    title = models.TextField()
    description = models.TextField()
    value = models.FloatField()
    currency = models.TextField()
    release_date = models.DateTimeField()
    tender_startdate = models.DateTimeField()
    tender_enddate = models.DateTimeField()
    buyer = models.TextField()
    buyer_id = models.TextField()

    sql = """
        SELECT
            ocds.ocid,
            ocds.release_id,
            ocds.release_json,
            ocds.release_json ->> 'language' AS language,
            ocds.release_json -> 'tender' ->> 'title' AS title,
            ocds.release_json -> 'tender' ->> 'description' AS description,
            ocds.release_json -> 'tender' -> 'value' ->> 'amount' AS value,
            ocds.release_json -> 'tender' -> 'value' ->> 'currency' AS currency,
            cast(NULLIF(ocds.release_json ->> 'date', '') AS TIMESTAMPTZ) AS release_date,
            cast(NULLIF(ocds.release_json -> 'tender' -> 'tenderPeriod' ->> 'startDate', '') AS TIMESTAMPTZ) AS tender_startdate,
            cast(NULLIF(ocds.release_json -> 'tender' -> 'tenderPeriod' ->> 'endDate', '') AS TIMESTAMPTZ) AS tender_enddate,
            ocds.release_json -> 'buyer' ->> 'name' AS buyer,
            ocds.release_json -> 'buyer' ->> 'id' AS buyer_id
        FROM bluetail_ocds_release_json ocds
        """

    class Meta:
        app_label = 'bluetail'
        db_table = 'bluetail_ocds_tender_view'
        managed = False


class OCDSParty(pgviews.View):
    """
    View for extracting Party details from an OCDSReleaseJSON object
    Parties as from an OCDS version 1.1 release in
    https://standard.open-contracting.org/latest/en/schema/reference/#parties
    """
    # dependencies = ['bluetail.OtherView',]
    # projection = ['bluetail.OCDSReleaseJSON.ocid', ]
    ocid = models.TextField(primary_key=True)
    release_json = JSONField()
    party_json = JSONField()
    party_id = models.TextField()
    party_role = models.TextField()
    party_identifier_scheme = models.TextField()
    party_identifier_id = models.TextField()
    party_legalname = models.TextField()
    party_name = models.TextField()
    party_countryname = models.TextField()
    contact_name = models.TextField()

    sql = """
        SELECT
            ocds.ocid,
            ocds.release_id,
            ocds.release_json,
            party                               as party_json,
            role                                AS party_role,
            party ->> 'id'                     as party_id,
            party -> 'identifier' ->> 'scheme'      as party_identifier_scheme,
            party -> 'identifier' ->> 'id'          as party_identifier_id,
            party -> 'identifier' ->> 'legalName'   as party_legalname,
            party -> 'address' ->> 'countryName'    as party_countryname,

            party ->> 'name'                           party_name,
            party -> 'contactPoint' ->> 'name'      as contact_name
        FROM
            bluetail_ocds_release_json ocds,
            LATERAL jsonb_array_elements(ocds.release_json -> 'parties') party,
            LATERAL jsonb_array_elements_text(party -> 'roles') role
        """

    class Meta:
        app_label = 'bluetail'
        db_table = 'bluetail_ocds_parties_view'
        managed = False
