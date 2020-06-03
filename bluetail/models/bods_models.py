from django.contrib.postgres.fields import JSONField
from django.db import models

from django_pgviews import view as pgviews


class BODSPersonStatementJSON(models.Model):
    """
    Model to store BODS Person Statement JSON.
    http://standard.openownership.org/en/0.2.0/schema/schema-browser.html#person-statement
    """
    statement_id = models.TextField(primary_key=True)
    statement_json = JSONField(null=True)

    class Meta:
        app_label = 'bluetail'
        db_table = 'bluetail_bods_personstatement_json'


class BODSPersonStatement(pgviews.View):
    """
    View to extract Person Statement details from a BODSPersonStatementJSON object
    http://standard.openownership.org/en/0.2.0/schema/schema-browser.html#person-statement
    """
    # dependencies = ['bluetail.OtherView',]
    statement_id = models.TextField(primary_key=True)
    statement_json = JSONField(null=True)
    identifiers_json = JSONField(null=True)

    fullName = models.TextField()
    personType = models.TextField()
    identifiers_0_id = models.TextField()
    identifiers_0_schemaName = models.TextField()

    sql = """
        SELECT
            b.statement_id,
            b.statement_json,
            b.statement_json ->> 'statementType' AS statement_type,
           -- Multiple names will need to be split
            b.statement_json -> 'names' -> 0 ->> 'fullName' AS "fullName",
            b.statement_json ->> 'personType' as "personType",
           -- Multiple ids will need to be split
            b.statement_json -> 'identifiers' AS identifiers_json,
            b.statement_json -> 'identifiers' -> 0 ->> 'id' AS identifiers_0_id,
            b.statement_json -> 'identifiers' -> 0 ->> 'schemeName' AS "identifiers_0_schemaName"
        FROM
            bluetail_bods_personstatement_json b
        """

    class Meta:
        managed = False
        app_label = 'bluetail'
        db_table = 'bluetail_bods_personstatement_view'



class BODSEntityStatementJSON(models.Model):
    """
    Model to store BODS Entity Statement JSON.
    http://standard.openownership.org/en/0.2.0/schema/schema-browser.html#entity-statement
    """
    statement_id = models.TextField(primary_key=True)
    statement_json = JSONField(null=True)

    class Meta:
        app_label = 'bluetail'
        db_table = 'bluetail_bods_entitystatement_json'


class BODSEntityStatement(pgviews.View):
    """
    View to extract Entity Statement details from a BODSPersonStatementJSON object
    http://standard.openownership.org/en/0.2.0/schema/schema-browser.html#entity-statement
    """
    statement_id = models.TextField(primary_key=True)
    statement_json = JSONField(null=True)

    statement_type = models.TextField()
    entity_name = models.TextField()
    entity_type = models.TextField()
    entity_id_scheme = models.TextField()
    entity_id = models.TextField()
    incorporatedInJurisdiction = models.TextField()

    sql = """
        SELECT
                b.statement_id,
                b.statement_json,
                b.statement_json ->> 'statementType' AS statement_type,
                b.statement_json ->> 'name' AS entity_name,
                -- Multiple addresses will need to be separated
                b.statement_json ->> 'entityType' AS entity_type,
                b.statement_json -> 'identifiers' -> 0 ->> 'schemeName' AS entity_id_scheme,
                b.statement_json -> 'identifiers' -> 0 ->> 'id' AS entity_id,
                b.statement_json -> 'incorporatedInJurisdiction' -> 'code' AS "incorporatedInJurisdiction"
               FROM
                 bluetail_bods_entitystatement_json b
        WHERE b.statement_json ->> 'statementType' = 'entityStatement'
        """

    class Meta:
        managed = False
        app_label = 'bluetail'
        db_table = 'bluetail_bods_entitystatement_view'



class BODSOwnershipStatementJSON(models.Model):
    """
    Model to store BODS Ownership-or-control Statement JSON.
    http://standard.openownership.org/en/0.2.0/schema/schema-browser.html#ownership-or-control-statement
    """
    statement_id = models.TextField(primary_key=True)
    statement_json = JSONField(null=True)

    class Meta:
        app_label = 'bluetail'
        db_table = 'bluetail_bods_ownershipstatement_json'


class BODSOwnershipStatement(pgviews.View):
    """
    View to extract details from a from a BODSPersonStatementJSON object
    http://standard.openownership.org/en/0.2.0/schema/schema-browser.html#ownership-or-control-statement
    """
    statement_id = models.TextField(primary_key=True)
    statement_json = JSONField(null=True)
    statement_type = models.TextField()

    subject_entity_statement = models.TextField()
    interested_person_statement_id = models.TextField()
    interested_entity_statement_id = models.TextField()

    sql = """
        SELECT
            b.statement_id,
            b.statement_json,
            b.statement_json ->> 'statementType' AS statement_type,
            NULLIF((b.statement_json ->> 'statementDate'), '') AS statement_date,
            b.statement_json ->> 'isComponent' AS is_component,
            
            b.statement_json -> 'subject' ->> 'describedByEntityStatement' AS subject_entity_statement,
            -- This will need expanding for real datasets
            b.statement_json -> 'interests' -> 0 ->> 'type' AS interest_type,
            b.statement_json -> 'interests' -> 0 -> 'share' -> 'exact' AS exact_share,
            b.statement_json -> 'interests' -> 0 ->> 'startDate' AS interest_start_date,
            b.statement_json -> 'interests' -> 0 ->> 'interestLevel' AS interest_level,
            b.statement_json -> 'interests' -> 0 ->> 'beneficialOwnershipOrControl' AS beneficial_ownership_or_control,
            b.statement_json -> 'subject' ->> 'describedByEntityStatement' AS subjectentity_statement_id,
            b.statement_json -> 'interestedParty' ->> 'describedByPersonStatement' AS interested_person_statement_id,
            b.statement_json -> 'interestedParty' ->> 'describedByEntityStatement' AS interested_entity_statement_id
        FROM bluetail_bods_ownershipstatement_json b
        WHERE b.statement_json ->> 'statementType' = 'ownershipOrControlStatement'
        """

    class Meta:
        managed = False
        app_label = 'bluetail'
        db_table = 'bluetail_bods_ownershipstatement_view'


# Testing nested PG views to use a single BODS JSON store

# class BODSPersonStatementJSON_view(models.Model):
#     projection = ['bluetail.BODSPersonStatementJSON.*',]
#     statement_id = models.TextField(primary_key=True)
#     statement_json = JSONField(null=True)
#
#     sql = """
#         SELECT
#             statement_id,
#             statement_json
#         FROM bluetail_bods_personstatement_json b
#         WHERE b.statement_json ->> 'statementType' = 'personStatement'
#         """
#
#     class Meta:
#         app_label = 'bluetail'
#         db_table = 'bluetail_bods_personstatement_view'
