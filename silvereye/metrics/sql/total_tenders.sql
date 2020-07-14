-- Count of tenders by date uploaded to cove-ocds (input_supplieddata.created)
INSERT INTO
    silvereye_publisher_metrics (publisher_name,
                                 publisher_id,
                                 count_lastmonth,
                                 count_last3months,
                                 count_last12months)
    (select
         buyer,
         buyer_id,
         count(*) filter (where created >= now()::DATE - INTERVAL '1 month')  as count_lastmonth,
         count(*) filter (where created >= now()::DATE - INTERVAL '3 month')  as count_last3months,
         count(*) filter (where created >= now()::DATE - INTERVAL '12 month') as count_last12months
     from
         bluetail_ocds_tender_view rel
             LEFT JOIN bluetail_ocds_package_data_view pac ON (rel.package_data_id = pac.id)
             LEFT JOIN input_supplieddata sup on (pac.supplied_data_id = sup.id)
     group by
         buyer, buyer_id)
ON CONFLICT (publisher_id)
DO UPDATE
  SET
    publisher_name = EXCLUDED.publisher_name,
    count_lastmonth = EXCLUDED.count_lastmonth,
    count_last3months = EXCLUDED.count_last3months,
    count_last12months = EXCLUDED.count_last12months
;
