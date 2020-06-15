-- Get distinct CF JSON with >2 suppliers and at least 1 supplier linnked to orgs_lookup
SELECT DISTINCT
    t.json                               AS ocds_json,
    t.json -> 'releases' -> 0 ->> 'ocid' AS ocid,
    t.source_id                          AS source_id
FROM
    pipeline.cf_notices_ocds t,
    LATERAL jsonb_array_elements(t.json -> 'releases' :: TEXT -> 0 -> 'awards' :: TEXT) award(value),
    LATERAL jsonb_array_elements(award -> 'suppliers') WITH ORDINALITY AS a(supplier, aw_supplier_array_id)
        INNER JOIN ocds.orgs_lookup_distinct orgs_supplier ON (orgs_supplier.org_string = upper(supplier ->> 'name'))
WHERE
      TRUE
  AND jsonb_array_length(award -> 'suppliers') > 2
      -- AND jsonb_array_length(award -> 'suppliers') < 30
  AND award <> 'null'
  AND date_created > '2020-01-01'
  AND orgs_supplier.scheme = 'GB-COH'
limit 100
