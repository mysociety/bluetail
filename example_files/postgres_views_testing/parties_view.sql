CREATE OR REPLACE VIEW scrap.ocds_parties_view AS
(
SELECT
    t.json ->> 'ocid'                         AS ocid,
    parties -> 'identifier' ->> 'scheme'      as party_id_scheme,
    parties -> 'identifier' ->> 'id'          as party_id,
    parties -> 'identifier' ->> 'legalName'   as party_legalname,
    parties ->> 'name'                           party_name,
    parties -> 'address' ->> 'countryName'    as party_countryname,
    parties -> 'contactPoint' ->> 'name'      as contact_name,
    parties -> 'contactPoint' ->> 'email'     as contact_email,
    parties -> 'contactPoint' ->> 'telephone' as contact_fax,
    parties -> 'contactPoint' ->> 'url'       as contact_url,
    parties -> 'address' ->> 'streetAddress'  AS streetAddress,
    parties -> 'address' ->> 'locality'       AS locality,
    parties -> 'address' ->> 'region'         AS region,
    parties -> 'address' ->> 'postalCode'     AS postcode,
    role::text                                AS party_role
FROM
    scrap.ocds_json t,
    LATERAL jsonb_array_elements(t.json -> 'parties') parties,
    LATERAL jsonb_array_elements(parties -> 'roles') role
);


