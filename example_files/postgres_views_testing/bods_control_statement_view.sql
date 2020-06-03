-- drop view bods_control_statement_view;
CREATE OR REPLACE VIEW scrap.bods_control_statement_view AS
SELECT
        b.statement_json -> 'subject' ->> 'describedByEntityStatement' AS subject_entity_statement,
        -- This will need expanding for real datasets
        b.statement_json -> 'interests' -> 0 ->> 'type' AS interest_type,
        b.statement_json -> 'interests' -> 0 -> 'share' -> 'exact' AS exact_share,
        b.statement_json -> 'interests' -> 0 ->> 'startDate' AS interest_start_date,
        b.statement_json -> 'interests' -> 0 ->> 'interestLevel' AS interest_level,
        b.statement_json -> 'interests' -> 0 ->> 'beneficialOwnershipOrControl' AS beneficial_ownership_or_control,
        b.statement_json ->> 'isComponent' AS is_component,
        b.statement_json ->> 'statementID' AS statement_id,
        b.statement_json ->> 'statementType' AS statement_type,
        NULLIF((b.statement_json ->> 'statementDate'::text), ''::text) AS statement_date,
        b.statement_json -> 'subject' ->> 'describedByEntityStatement' AS subject_entity_statement_id,
        b.statement_json -> 'interestedParty' ->> 'describedByPersonStatement' AS interested_person_statement_id,
        b.statement_json -> 'interestedParty' ->> 'describedByEntityStatement' AS interested_entity_statement_id,
        b.statement_json -> 'publicationDetails' -> 'publisher' ->> 'name' AS publisher_name,
        NULLIF(((b.statement_json -> 'publicationDetails'::text) ->> 'publicationDate'::text), ''::text) AS publication_date,
        b.statement_json -> 'publicationDetails' ->> 'bodsVersion' AS bods_version
       FROM
         scrap.bods_json b
WHERE b.statement_json -> 'statementType' = '"ownershipOrControlStatement"'
;
