
-- DROP MATERIALIZED VIEW contracts_finder.notice_view;
-- drop view contracts_finder.notice_view;
CREATE OR REPLACE VIEW contracts_finder.notice_view AS (
  SELECT
    awards.source,
    awards.source_id,
    f_cast_isots(NULLIF(releases ->> 'date', ''::text)) as releasedate,
    awards.ocid,
    aw_id,
    awards.aw_supplier_array_id,
    releases ->> 'language' AS language,
    releases -> 'tender' ->> 'title' AS tender_title,
    releases -> 'tender' ->> 'description' AS tender_description,
    releases -> 'tender' -> 'value' ->> 'amount' AS tender_value,
    releases -> 'tender' -> 'value' ->> 'currency' AS tender_currency,
    f_cast_isots(NULLIF((((releases  -> 'tender'::text) -> 'tenderPeriod'::text) ->> 'startDate'::text), ''::text)) AS startdate,
    f_cast_isots(NULLIF((((releases  -> 'tender'::text) -> 'tenderPeriod'::text) ->> 'endDate'::text), ''::text)) AS enddate,
    releases -> 'buyer' ->> 'name' AS buyer,
    releases -> 'buyer' -> 'address' ->> 'streetAddress' AS streetAddress,
    releases -> 'buyer' -> 'address' ->> 'locality' AS locality,
    releases -> 'buyer' -> 'address' ->> 'region' AS region,
    releases -> 'buyer' -> 'address' ->> 'postalCode' AS postcode,
    releases -> 'buyer' -> 'address' ->> 'countryName' AS countryname,
    releases -> 'buyer' -> 'contactPoint' ->> 'name' AS contactName,
    releases -> 'buyer' -> 'contactPoint' ->> 'email' AS email,
    releases -> 'buyer' -> 'contactPoint' ->> 'telephone' AS telephone,
    releases -> 'buyer' -> 'contactPoint' ->> 'faxNumber' AS faxNumber,
    releases -> 'buyer' -> 'contactPoint' ->> 'url' AS contact_url,
    aw_date,
    coalesce(award_url, tender_url) as award_url,
    aw_title,
    aw_description,
    aw_value,
    aw_contractPeriod_startdate,
    aw_contractPeriod_enddate,
    aw_status,
    aw_total_suppliers,

--     supplier ->> 'name' AS aw_supplier_name,
--     supplier -> 'address' ->> 'streetAddress' AS aw_supplier_streetAddress,
--     awards.language,
--     awards.supplier -> 'contactPoint' ->> 'url' AS aw_supplier_url,
    awards.json as awards_json
  FROM (
         SELECT
           notices.*,
           award ->> 'id'                            AS aw_id,
           f_cast_isots(NULLIF(award ->> 'date', ''::text)) AS aw_date,
            releases -> 'tender' -> 'documents' -> 0 ->> 'url' AS tender_url,
           award -> 'documents' -> 0 ->> 'url' AS award_url,
           award ->> 'title'                         AS aw_title,
           award ->> 'description'                   AS aw_description,
           award -> 'value' ->> 'amount' :: TEXT     AS aw_value,
           f_cast_isots(NULLIF(award -> 'contractPeriod' ->> 'startDate', ''::text)) AS aw_contractPeriod_startdate,
           f_cast_isots(NULLIF(award -> 'contractPeriod' ->> 'endDate', ''::text)) AS aw_contractPeriod_enddate,

           award ->> 'status'                        AS aw_status,
           jsonb_array_length(award -> 'suppliers')  AS aw_total_suppliers
         FROM (
              SELECT
                 t.*,
                 award,
                 releases,
                 supplier,
                 aw_supplier_array_id
                FROM
                 contracts_finder.cf_notices_cn_sample t,
                    LATERAL jsonb_array_elements(t.json -> 'releases') releases,
                    LATERAL jsonb_array_elements(t.json -> 'releases' :: TEXT -> 0 -> 'awards' :: TEXT) award(value),
                    LATERAL jsonb_array_elements(award -> 'suppliers') WITH ORDINALITY AS a(supplier, aw_supplier_array_id)
               WHERE TRUE
                 AND award <> 'null'
              ) notices
       ) awards
)
;






SELECT
    *,
    coalesce(releasedate, startdate, date_created) AS pubdate
    FROM (
      SELECT
        t.id,
        t.source,
        t.source_id,
        t.json -> 'releases' -> 0 ->> 'ocid' AS ocid,
        t.json -> 'releases' -> 0 -> 'tag' AS release_tag,
        releases ->> 'language' AS language,
--         COALESCE(releases ->> 'language', l.predicted_language) AS language,
        releases -> 'tender' ->> 'title' AS title,
        releases -> 'tender' ->> 'description' AS description,
        releases -> 'tender' -> 'value' ->> 'amount' AS value,
        releases -> 'tender' -> 'value' ->> 'currency' AS currency,
        f_cast_isots(NULLIF((((t.json -> 'releases'::text) -> 0) ->> 'date'::text), ''::text)) AS releasedate,
        f_cast_isots(NULLIF((((((t.json -> 'releases'::text) -> 0) -> 'tender'::text) -> 'tenderPeriod'::text) ->> 'startDate'::text), ''::text)) AS startdate,
        f_cast_isots(NULLIF((((((t.json -> 'releases'::text) -> 0) -> 'tender'::text) -> 'tenderPeriod'::text) ->> 'endDate'::text), ''::text)) AS enddate,
        releases -> 'buyer' ->> 'name' AS buyer,
        releases -> 'buyer' -> 'address' ->> 'streetAddress' AS streetAddress,
        releases -> 'buyer' -> 'address' ->> 'locality' AS locality,
        releases -> 'buyer' -> 'address' ->> 'region' AS region,
        releases -> 'buyer' -> 'address' ->> 'postalCode' AS postcode,
        releases -> 'buyer' -> 'address' ->> 'countryName' AS countryname,
        releases -> 'buyer' -> 'contactPoint' ->> 'name' AS contactName,
        releases -> 'buyer' -> 'contactPoint' ->> 'email' AS email,
        releases -> 'buyer' -> 'contactPoint' ->> 'telephone' AS telephone,
        releases -> 'buyer' -> 'contactPoint' ->> 'faxNumber' AS faxNumber,
        releases -> 'buyer' -> 'contactPoint' ->> 'url' AS contact_url,
        url_doc.value ->> 'url' as tender_url,
        ARRAY(select array_to_string(regexp_matches(releases -> 'tender' #>> '{"items", 0}', '"(\d{8})+"', 'g'), '')) as cpvs,
--             ARRAY[p.proclass] as proclass,
--             ARRAY[NULL] as proclass,
        t.date_created,
        t.date_updated,
        t.json
       FROM
         ocds.ocds_tenders t,
--              LEFT JOIN ocds.lang_predictions l ON ((t.id = l.id))
--              LEFT JOIN classification.proclass_predictions p ON ((t.id = p.id)),
         LATERAL jsonb_array_elements(t.json -> 'releases') releases
         LEFT JOIN LATERAL jsonb_array_elements(releases -> 'tender' -> 'documents') url_doc(value) ON url_doc.value ->> 'id' = 'tender_url'
--          WHERE t.json -> 'releases' -> 0 -> 'tag' = '["tender"]'
    ) sub
WHERE
    jsonb_array_length(json -> 'releases') = 1
;




