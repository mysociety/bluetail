-- Count of tenders by date, last year
INSERT INTO
    silvereye_publisher_metrics (publisher_name,
                                 publisher_id,
                                 count_lastmonth_yearago,
                                 count_last3months_yearago,
                                 count_last12months_yearago)
    (select
    buyer,
    buyer_id,
    count (*) filter (where created >= now()::DATE - INTERVAL '13 month' and created < now()::DATE - INTERVAL '12 month') as count_lastmonth_yearago,
    count (*) filter (where created >= now()::DATE - INTERVAL '15 month' and created < now()::DATE - INTERVAL '12 month') as count_last3months_yearago,
    count (*) filter (where created >= now()::DATE - INTERVAL '24 month' and created < now()::DATE - INTERVAL '12 month') as count_last12months_yearago
from
    bluetail_ocds_tender_view rel
    LEFT JOIN bluetail_ocds_package_data_view pac ON (rel.package_data_id = pac.id)
    LEFT JOIN input_supplieddata sup on (pac.supplied_data_id = sup.id)
where rel.package_data_id notnull
group by buyer,
         buyer_id
;)
ON CONFLICT (publisher_id)
DO UPDATE
  SET
    publisher_name = EXCLUDED.publisher_name,
    count_lastmonth_yearago = EXCLUDED.count_lastmonth_yearago,
    count_last3months_yearago = EXCLUDED.count_last3months_yearago,
    count_last12months_yearago = EXCLUDED.count_last12months_yearago
;