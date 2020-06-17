SELECT *
FROM
    scrap.bods_control_statement_view
WHERE
    subject_entity_statement = '1dc0e987-5c57-4a1c-b3ad-61353b66a9b7'
;

select
    name,
    entity_id,
    statement_id,
    statement_type
from
    scrap.bods_person_view
WHERE
        statement_id in
        (SELECT
             interested_person_statement_id
         FROM
             scrap.bods_control_statement_view
         WHERE
             subject_entity_statement = '1dc0e987-5c57-4a1c-b3ad-61353b66a9b7')
;

select
    entity_name,
    country,
    statement_id,
    statement_type
from
    scrap.bods_entity_view
WHERE
        statement_id in
        (SELECT
             interested_entity_statement_id
         FROM
             scrap.bods_control_statement_view
         WHERE
             subject_entity_statement = '1dc0e987-5c57-4a1c-b3ad-61353b66a9b7')
;



SELECT DISTINCT
    subject_entity_statement
FROM
    scrap.bods_control_statement_view
;

select
    name,
    entity_id,
    statement_id,
    statement_type
from
    scrap.bods_person_view
WHERE
        statement_id in
        (SELECT
             interested_person_statement_id
         FROM
             scrap.bods_control_statement_view
         WHERE
             subject_entity_statement = '1dc0e987-5c57-4a1c-b3ad-61353b66a9b7')
;

select
    entity_name,
    country,
    statement_id,
    statement_type
from
    scrap.bods_entity_view
WHERE
        statement_id in
        (SELECT
             interested_entity_statement_id
         FROM
             scrap.bods_control_statement_view
         WHERE
             subject_entity_statement = '1dc0e987-5c57-4a1c-b3ad-61353b66a9b7')
;
