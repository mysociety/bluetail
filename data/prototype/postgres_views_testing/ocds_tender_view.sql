CREATE OR REPLACE VIEW scrap.ocds_tender_view AS
SELECT
        t.json ->> 'ocid' AS ocid,
        t.json ->> 'language' AS language,
        t.json -> 'tender' ->> 'title' AS title,
        t.json -> 'tender' ->> 'description' AS description,
        t.json -> 'tender' -> 'value' ->> 'amount' AS value,
        t.json -> 'tender' -> 'value' ->> 'currency' AS currency,
        NULLIF((t.json ->> 'date'::text), ''::text) AS publish_date,
        NULLIF((((t.json -> 'tender'::text) -> 'tenderPeriod'::text) ->> 'startDate'::text), ''::text) AS tendering_startdate,
        NULLIF((((t.json -> 'tender'::text) -> 'tenderPeriod'::text) ->> 'endDate'::text), ''::text) AS closing_date,
        t.json -> 'buyer' ->> 'name' AS buyer,
        t.json -> 'buyer' ->> 'id' AS buyer_id
       FROM
         scrap.ocds_json t
;


