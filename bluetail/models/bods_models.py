from django.contrib.postgres.fields import JSONField
from django.db import models

from django_pgviews import view as pgviews


class BODSStatementJSON(models.Model):
    statement_id = models.TextField(primary_key=True)
    statement_json = JSONField()

    class Meta:
        app_label = 'bluetail'
        db_table = 'bluetail_bods_statement_json'


class BODSPersonStatement(pgviews.View):
    """
    View to extract details from a BODSStatementJSON with statementType = personStatement
    http://standard.openownership.org/en/0.2.0/schema/schema-browser.html#person-statement
    """
    # dependencies = ['bluetail.OtherView',]
    statement_id = models.TextField(primary_key=True)
    statement_json = JSONField()

    identifiers_json = JSONField()
    fullName = models.TextField()
    personType = models.TextField()

    sql = """
        SELECT
            b.statement_id,
            b.statement_json,
            b.statement_json ->> 'statementType' AS statement_type,
            -- b.statement_json -> 'identifiers' AS identifiers_json,
            jsonb_agg(identifiers.value) as identifiers_json,
            
           -- Person specific fields
            b.statement_json -> 'names' -> 0 ->> 'fullName' AS "fullName",
            b.statement_json ->> 'personType' as "personType"
        FROM
            bluetail_bods_statement_json b
            -- This join filters out duplicate identifiers and Companies House identifiers < 8 digits
            LEFT JOIN LATERAL (
                select distinct identifier.value
                from jsonb_array_elements(b.statement_json -> 'identifiers') identifier(value)
                where
                    NOT (identifier ->> 'scheme' notnull AND identifier ->> 'scheme' = 'GB-COH' AND length(identifier ->> 'id') < 8)
            ) identifiers ON TRUE
        WHERE b.statement_json ->> 'statementType' = 'personStatement'
        group by statement_id
        """

    class Meta:
        managed = False
        app_label = 'bluetail'
        db_table = 'bluetail_bods_personstatement_view'


class BODSEntityStatement(pgviews.View):
    """
    View to extract details from a BODSStatementJSON with statementType = entityStatement
    http://standard.openownership.org/en/0.2.0/schema/schema-browser.html#entity-statement
    """
    statement_id = models.TextField(primary_key=True)
    statement_json = JSONField(null=True)

    statement_type = models.TextField()
    entity_name = models.TextField()
    entity_type = models.TextField()
    identifiers_json = JSONField()
    incorporatedInJurisdiction = models.TextField()

    sql = """
        SELECT
            b.statement_id,
            b.statement_json,
            b.statement_json ->> 'statementType' AS statement_type,
            -- b.statement_json -> 'identifiers' AS identifiers_json,
            jsonb_agg(identifiers.value) as identifiers_json,
            
            -- Entity specific fields
            b.statement_json ->> 'name' AS entity_name,
            b.statement_json ->> 'entityType' AS entity_type, 
            b.statement_json -> 'incorporatedInJurisdiction' -> 'code' AS "incorporatedInJurisdiction"
        FROM
             bluetail_bods_statement_json b
            -- This join filters out duplicate identifiers and Companies House identifiers < 8 digits
            LEFT JOIN LATERAL (
                select distinct identifier.value
                from jsonb_array_elements(b.statement_json -> 'identifiers') identifier(value)
                where
                    NOT (identifier ->> 'scheme' notnull AND identifier ->> 'scheme' = 'GB-COH' AND length(identifier ->> 'id') < 8)
            ) identifiers ON TRUE
        WHERE b.statement_json ->> 'statementType' = 'entityStatement'
        group by statement_id
        """

    class Meta:
        managed = False
        app_label = 'bluetail'
        db_table = 'bluetail_bods_entitystatement_view'


class BODSOwnershipStatement(pgviews.View):
    """
    View to extract details from a BODSStatementJSON with statementType = ownershipOrControlStatement
    http://standard.openownership.org/en/0.2.0/schema/schema-browser.html#ownership-or-control-statement
    """
    statement_id = models.TextField(primary_key=True)
    statement_json = JSONField()
    statement_type = models.TextField()

    subject_entity_statement = models.TextField()
    interested_person_statement_id = models.TextField()
    interested_entity_statement_id = models.TextField()

    sql = """
        SELECT
            b.statement_id,
            b.statement_json,
            b.statement_json ->> 'statementType' AS statement_type,
            b.statement_json -> 'identifiers' AS identifiers_json,
            
            -- Ownership specific fields
            b.statement_json -> 'subject' ->> 'describedByEntityStatement' AS subject_entity_statement,
            b.statement_json -> 'interestedParty' ->> 'describedByPersonStatement' AS interested_person_statement_id,
            b.statement_json -> 'interestedParty' ->> 'describedByEntityStatement' AS interested_entity_statement_id
        FROM bluetail_bods_statement_json b
        WHERE b.statement_json ->> 'statementType' = 'ownershipOrControlStatement'
        """

    class Meta:
        managed = False
        app_label = 'bluetail'
        db_table = 'bluetail_bods_ownershipstatement_view'
