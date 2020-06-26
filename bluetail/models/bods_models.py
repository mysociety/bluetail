from faker import Faker

from django.contrib.postgres.fields import JSONField
from django.db import models

from django_pgviews import view as pgviews


fake = Faker()


class BODSStatementJSON(models.Model):
    statement_id = models.TextField(primary_key=True)
    statement_json = JSONField()

    class Meta:
        app_label = 'bluetail'
        db_table = 'bluetail_bods_statement_json'


class BODSPersonStatement(pgviews.View):
    """
    View to extract Person Statement details from a BODSPersonStatementJSON object
    http://standard.openownership.org/en/0.2.0/schema/schema-browser.html#person-statement
    """
    # dependencies = ['bluetail.OtherView',]
    statement_id = models.TextField(primary_key=True)
    statement_json = JSONField()

    identifiers_json = JSONField()
    fullName = models.TextField()
    personType = models.TextField()

    def fullName(self):
        if not hasattr(self, 'fakeName'):
            self.fakeName = fake.name()
        return self.fakeName

    sql = """
        SELECT
            b.statement_id,
            b.statement_json,
            b.statement_json ->> 'statementType' AS statement_type,
            b.statement_json -> 'identifiers' AS identifiers_json,
            
           -- Person specific
            b.statement_json -> 'names' -> 0 ->> 'fullName' AS "fullName",
            b.statement_json ->> 'personType' as "personType"
        FROM
            bluetail_bods_statement_json b
        WHERE b.statement_json ->> 'statementType' = 'personStatement'
        """

    class Meta:
        managed = False
        app_label = 'bluetail'
        db_table = 'bluetail_bods_personstatement_view'


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
    identifiers_json = JSONField()
    incorporatedInJurisdiction = models.TextField()

    sql = """
        SELECT
            b.statement_id,
            b.statement_json,
            b.statement_json ->> 'statementType' AS statement_type,
            b.statement_json -> 'identifiers' AS identifiers_json,
           
            b.statement_json ->> 'name' AS entity_name,
            b.statement_json ->> 'entityType' AS entity_type, 
            b.statement_json -> 'incorporatedInJurisdiction' -> 'code' AS "incorporatedInJurisdiction"
        FROM
             bluetail_bods_statement_json b
        WHERE b.statement_json ->> 'statementType' = 'entityStatement'
        """

    class Meta:
        managed = False
        app_label = 'bluetail'
        db_table = 'bluetail_bods_entitystatement_view'


class BODSOwnershipStatement(pgviews.View):
    """
    View to extract details from a from a BODSPersonStatementJSON object
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
        FROM bluetail_bods_statement_json b
        WHERE b.statement_json ->> 'statementType' = 'ownershipOrControlStatement'
        """

    class Meta:
        managed = False
        app_label = 'bluetail'
        db_table = 'bluetail_bods_ownershipstatement_view'

