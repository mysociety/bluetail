-- Difference in count of tenders between a period and same period last year
INSERT INTO
    silvereye_publisher_metrics (publisher_name,
                                 publisher_id,
                                 difference_last_month,
                                 difference_last3_months,
                                 difference_last12_months)
    (select
    buyer,
    buyer_id,
    ((count (*) filter (where created >= now()::DATE - INTERVAL '1 month'))::NUMERIC - (count (*) filter (where created >= now()::DATE - INTERVAL '13 month' and created < now()::DATE - INTERVAL '12 month'))::NUMERIC) * 100 as difference_last_month,
    ((count (*) filter (where created >= now()::DATE - INTERVAL '3 month'))::NUMERIC - (count (*) filter (where created >= now()::DATE - INTERVAL '15 month' and created < now()::DATE - INTERVAL '12 month'))::NUMERIC) * 100 as difference_last3_months,
    ((count (*) filter (where created >= now()::DATE - INTERVAL '12 month'))::NUMERIC - (count (*) filter (where created >= now()::DATE - INTERVAL '24 month' and created < now()::DATE - INTERVAL '12 month'))::NUMERIC) * 100 as difference_last12_months
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
    difference_last_month = EXCLUDED.difference_last_month,
    difference_last3_months = EXCLUDED.difference_last3_months,
    difference_last12_months = EXCLUDED.difference_last12_months
;
