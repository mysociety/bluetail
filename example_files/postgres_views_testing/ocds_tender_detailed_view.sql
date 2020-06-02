CREATE OR REPLACE VIEW scrap.ocds_tender_detailed_view AS
SELECT
        t.json ->> 'ocid' AS ocid,
        t.json ->> 'id' AS id,
        NULLIF((t.json ->> 'date'::text), ''::text) AS release_date,
        t.json ->> 'language' AS language,
        t.json -> 'tender' ->> 'title' AS title,
        t.json -> 'tag' ->> 0 AS release_tag,
        t.json ->> 'initiationType' AS initiation_type,
        t.json -> 'tender' ->> 'description' AS description,
        t.json -> 'tender' -> 'value' ->> 'amount' AS value,
        t.json -> 'tender' -> 'value' ->> 'currency' AS currency,
        t.json -> 'tender' ->> 'id' AS tender_id,
        t.json -> 'tender' ->> 'title' AS tender_title,
        t.json -> 'tender' ->> 'description' AS tender_description,
        NULLIF((((t.json -> 'tender'::text) -> 'tenderPeriod'::text) ->> 'startDate'::text), ''::text) AS tendering_startdate,
        NULLIF((((t.json -> 'tender'::text) -> 'tenderPeriod'::text) ->> 'endDate'::text), ''::text) AS closing_date,
        NULLIF((((t.json -> 'tender'::text) -> 'contractPeriod'::text) ->> 'startDate'::text), ''::text) AS contract_start_date,
        NULLIF((((t.json -> 'tender'::text) -> 'contractPeriod'::text) ->> 'endDate'::text), ''::text) AS contract_end_date,
        t.json -> 'procuringEntity' ->> 'name' AS procuring_entity,
        t.json -> 'procuringEntity' ->> 'id' AS procuring_entity_id,
        t.json -> 'numberOfTenderers' AS number_of_tenderers,
        t.json -> 'buyer' ->> 'name' AS buyer,
        t.json -> 'buyer' ->> 'id' AS buyer_id,
        t.json -> 'buyer' -> 'address' ->> 'streetAddress' AS streetAddress,
        t.json -> 'buyer' -> 'address' ->> 'locality' AS locality,
        t.json -> 'buyer' -> 'address' ->> 'region' AS region,
        t.json -> 'buyer' -> 'address' ->> 'postalCode' AS postcode,
        t.json -> 'buyer' -> 'address' ->> 'countryName' AS countryname
       FROM
         scrap.ocds_json t
;


