
DROP VIEW scrap.bods_person_view;
CREATE OR REPLACE VIEW scrap.bods_person_view AS
SELECT
       -- Multiple names will need to be split
        b.statement_json -> 'names' -> 0 ->> 'fullName' AS fullName,
        b.statement_json ->> 'personType' AS entity_type,
       -- Multiple ids will need to be split
        b.statement_json -> 'identifiers' -> 0 ->> 'id' AS entity_id,
        b.statement_json -> 'identifiers' -> 0 ->> 'schemeName' AS schemeName,
        b.statement_json ->> 'isComponent' AS is_component,
        b.statement_json ->> 'statementID' AS statement_id,
        b.statement_json ->> 'statementType' AS statement_type,
        NULLIF((b.statement_json ->> 'statementDate'::text), ''::text) AS statement_date,
        b.statement_json -> 'publicationDetails' -> 'publisher' ->> 'name' AS publisher_name,
        NULLIF(((b.statement_json -> 'publicationDetails'::text) ->> 'publicationDate'::text), ''::text) AS publication_date,
        b.statement_json -> 'publicationDetails' ->> 'bodsVersion' AS bods_version
       FROM
         scrap.bods_json b
WHERE b.statement_json -> 'statementType' = '"personStatement"'
;
