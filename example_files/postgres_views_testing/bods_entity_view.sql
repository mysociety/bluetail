CREATE OR REPLACE VIEW scrap.bods_entity_view AS
SELECT
        b.statement_json ->> 'name' AS entity_name,
        -- Multiple addresses will need to be separated
        b.statement_json -> 'addresses' -> 0 ->> 'country' AS country,
        b.statement_json ->> 'entityType' AS entity_type,
        b.statement_json -> 'identifiers' -> 0 ->> 'id' AS entity_id,
        b.statement_json -> 'identifiers' -> 0 ->> 'schemeName' AS entity_id_scheme,
        b.statement_json ->> 'isComponent' AS is_component,
        b.statement_json ->> 'statementID' AS statement_id,
        b.statement_json ->> 'statementType' AS statement_type,
        NULLIF((b.statement_json ->> 'statementDate'::text), ''::text) AS statement_date,
        b.statement_json -> 'publicationDetails' -> 'publisher' ->> 'name' AS publisher_name,
        NULLIF(((b.statement_json -> 'publicationDetails'::text) ->> 'publicationDate'::text), ''::text) AS publication_date,
        b.statement_json -> 'publicationDetails' ->> 'bodsVersion' AS bods_version,
        b.statement_json -> 'incorporatedInJurisdiction' ->> 'code' AS incorporatedInJurisdiction
       FROM
         scrap.bods_json b
WHERE b.statement_json -> 'statementType' = '"entityStatement"'
;


