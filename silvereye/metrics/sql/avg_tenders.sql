-- avg no of tenders
INSERT INTO
    silvereye_publisher_metrics (publisher_name,
                                 publisher_id,
                                 avg_lastmonth,
                                 avg_last3months,
                                 avg_last12months)
    (select buyer,
            buyer_id,
       avg(notice_count) filter (where months >= to_char(now() - INTERVAL '1 month', 'YYYY-MM')) as avg_lastmonth,
       avg(notice_count) filter (where months >= to_char(now() - INTERVAL '3 month', 'YYYY-MM')) as avg_last3months,
       avg(notice_count) filter (where months >= to_char(now() - INTERVAL '12 month', 'YYYY-MM')) as avg_last12months
from (select
    buyer,
    buyer_id,
    to_char(created, 'YYYY-MM') as months,
    count (*) as notice_count
from
    bluetail_ocds_tender_view rel
    LEFT JOIN bluetail_ocds_package_data_view pac ON (rel.package_data_id = pac.id)
    LEFT JOIN input_supplieddata sup on (pac.supplied_data_id = sup.id)
where rel.package_data_id notnull
group by buyer,
         buyer_id,
         months) sub
group by buyer,
         buyer_id
;)
ON CONFLICT (publisher_id)
DO UPDATE
  SET
    publisher_name = EXCLUDED.publisher_name,
    avg_lastmonth = EXCLUDED.avg_lastmonth,
    avg_last3months = EXCLUDED.avg_last3months,
    avg_last12months = EXCLUDED.avg_last12months
;
