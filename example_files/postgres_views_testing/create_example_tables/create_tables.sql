create schema scrap;

create table scrap.bods_json
(
    statement_json jsonb,
    statement_type text,
    statement_id   text,
    application_id text
);


create table scrap.ocds_json
(
    json jsonb,
    ocid text
);
