
-- drop view ocds.ocds_awards_suppliers_new_view;
CREATE OR REPLACE VIEW contracts_finder.suppliers_view AS (
  SELECT
    awards.ocid::TEXT ||'_'|| awards.aw_id::TEXT ||'_S'|| aw_supplier_array_id as unique_supplier_id,
    awards.ocid,
    aw_id,
    awards.aw_supplier_array_id,
    supplier ->> 'name' AS aw_supplier_name,
    supplier ->> 'sme' AS sme,
    supplier ->> 'vco' AS vco,
    supplier -> 'address' ->> 'streetAddress' AS aw_supplier_streetAddress,
    supplier -> 'address' ->> 'region' AS aw_supplier_region,
    supplier -> 'address' ->> 'postalCode' AS aw_supplier_postalCode,
    supplier -> 'address' ->> 'countryName' AS aw_supplier_countryName,
    supplier -> 'identifier' ->> 'id' AS aw_supplier_identifier_id,
    supplier -> 'identifier' ->> 'uri' AS aw_supplier_identifier_uri,
    supplier -> 'identifier' ->> 'scheme' AS aw_supplier_identifier_scheme,
    supplier -> 'identifier' ->> 'legalName' AS aw_supplier_identifier_legalName,
    awards.supplier -> 'contactPoint' ->> 'name' AS aw_supplier_contact_name,
    awards.supplier -> 'contactPoint' ->> 'email' AS aw_supplier_contact_email,
    awards.supplier -> 'contactPoint' ->> 'faxNumber' AS aw_supplier_contact_faxNumber,
    awards.supplier -> 'contactPoint' ->> 'telephone' AS aw_supplier_telephone,
    awards.supplier -> 'contactPoint' ->> 'url' AS aw_supplier_url
  FROM (
         SELECT
           tenders.*,
           award ->> 'id'                            AS aw_id
         FROM (
              SELECT
                 t.*,
                 award,
                 supplier,
                 aw_supplier_array_id
               FROM
                 contracts_finder.cf_notices_cn_sample t,
                LATERAL jsonb_array_elements(t.json -> 'releases' :: TEXT -> 0 -> 'awards' :: TEXT) award(value),
                LATERAL jsonb_array_elements(award -> 'suppliers') WITH ORDINALITY AS a(supplier, aw_supplier_array_id)
               WHERE TRUE
                 AND award <> 'null'
              ) tenders
       ) awards
)
;


-- Shows that there can be multiple suppliers per award
SELECT
jsonb_array_length(award -> 'suppliers'),
        t.*
FROM
 contracts_finder.cf_notices_cn_sample t,
LATERAL jsonb_array_elements(t.json -> 'releases' :: TEXT -> 0 -> 'awards' :: TEXT) award(value)
-- LATERAL jsonb_array_elements(award -> 'suppliers') WITH ORDINALITY AS a(supplier, aw_supplier_array_id)
WHERE  jsonb_array_length(award -> 'suppliers') != 1
;


-- shows that they only have one award per notice
SELECT
 t.*,
jsonb_array_length(t.json -> 'releases'::TEXT -> 0 -> 'awards')
FROM
 contracts_finder.cf_notices_cn_sample t
WHERE  jsonb_array_length(t.json -> 'releases'::TEXT -> 0 -> 'awards') = 1
;