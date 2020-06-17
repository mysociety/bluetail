CREATE SCHEMA IF NOT EXISTS scrap;
CREATE TABLE scrap.cf_augmented_tenders
(
    json JSONB,
    ocid TEXT
);