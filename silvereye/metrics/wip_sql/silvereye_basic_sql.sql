select count (*) from public.bluetail_ocds_tender_view;

select buyer,
       count (*)
from public.bluetail_ocds_tender_view
group by buyer;

select buyer,
       count (*) filter (where release_date >= now()::DATE - INTERVAL '1 month') as count_last_month,
       count (*) filter (where release_date >= now()::DATE - INTERVAL '3 month') as count_last3_months,
       count (*) filter (where release_date >= now()::DATE - INTERVAL '12 month') as count_last12_months
from public.bluetail_ocds_tender_view
group by buyer
;

select buyer,
       count (*) filter (where release_date >= now()::DATE - INTERVAL '1 month') as count_last_month,
       count (*) filter (where release_date >= now()::DATE - INTERVAL '3 month') as count_last3_months,
       count (*) filter (where release_date >= now()::DATE - INTERVAL '12 month') as count_last12_months
from public.bluetail_ocds_tender_view
group by buyer
;




select
    buyer,
       count (distinct ocid) filter (where release_date >= now()::DATE - INTERVAL '1 month') as count_last_month,
       count (distinct ocid) filter (where release_date >= now()::DATE - INTERVAL '3 month') as count_last3_months,
       count (distinct ocid) filter (where release_date >= now()::DATE - INTERVAL '12 month') as count_last12_months
    --count (distinct ocid) as notice_count
from
    bluetail_ocds_tender_view rel
    LEFT JOIN bluetail_ocds_package_data_view pac ON (rel.package_data_id = pac.id)
    LEFT JOIN input_supplieddata sup on (pac.supplied_data_id = sup.id)
where rel.package_data_id notnull
group by rel.buyer
--          months
;


select
    buyer,
       count (distinct ocid) filter (where release_date >= now()::DATE - INTERVAL '13 month' and release_date < now()::DATE - INTERVAL '12 month') as count_last_month,
       count (distinct ocid) filter (where release_date >= now()::DATE - INTERVAL '15 month' and release_date < now()::DATE - INTERVAL '12 month') as count_last3_months,
       count (distinct ocid) filter (where release_date >= now()::DATE - INTERVAL '24 month' and release_date < now()::DATE - INTERVAL '12 month') as count_last12_months
    --count (distinct ocid) as notice_count
from
    bluetail_ocds_tender_view rel
    LEFT JOIN bluetail_ocds_package_data_view pac ON (rel.package_data_id = pac.id)
    LEFT JOIN input_supplieddata sup on (pac.supplied_data_id = sup.id)
where rel.package_data_id notnull
group by rel.buyer
--          months
;

select
    buyer,
       ((count (distinct ocid) filter (where release_date >= now()::DATE - INTERVAL '1 month'))::NUMERIC - (count (distinct ocid) filter (where release_date >= now()::DATE - INTERVAL '13 month' and release_date < now()::DATE - INTERVAL '12 month'))::NUMERIC) * 100 as difference_last_month,
       ((count (distinct ocid) filter (where release_date >= now()::DATE - INTERVAL '3 month'))::NUMERIC - (count (distinct ocid) filter (where release_date >= now()::DATE - INTERVAL '15 month' and release_date < now()::DATE - INTERVAL '12 month'))::NUMERIC) * 100 as difference_last3_months,
       ((count (distinct ocid) filter (where release_date >= now()::DATE - INTERVAL '12 month'))::NUMERIC - (count (distinct ocid) filter (where release_date >= now()::DATE - INTERVAL '24 month' and release_date < now()::DATE - INTERVAL '12 month'))::NUMERIC) * 100 as difference_last12_months
    --count (distinct ocid) as notice_count
from
    bluetail_ocds_tender_view rel
    LEFT JOIN bluetail_ocds_package_data_view pac ON (rel.package_data_id = pac.id)
    LEFT JOIN input_supplieddata sup on (pac.supplied_data_id = sup.id)
where rel.package_data_id notnull
group by rel.buyer
--          months
;




select
    buyer,
    to_char(release_date, 'YYYY-MM') as months,
    to_char(now() - INTERVAL '1 month', 'YYYY-MM') as months,
    to_char(now() - INTERVAL '3 month', 'YYYY-MM') as months,
    to_char(now() - INTERVAL '12 month', 'YYYY-MM') as months
    --count (distinct ocid) as notice_count
from
    bluetail_ocds_tender_view rel
    LEFT JOIN bluetail_ocds_package_data_view pac ON (rel.package_data_id = pac.id)
    LEFT JOIN input_supplieddata sup on (pac.supplied_data_id = sup.id)
where rel.package_data_id notnull
-- group by rel.buyer,
--          months
;

select buyer,
       avg(notice_count) filter (where months >= to_char(now() - INTERVAL '1 month', 'YYYY-MM')),
       avg(notice_count) filter (where months >= to_char(now() - INTERVAL '3 month', 'YYYY-MM')),
       avg(notice_count) filter (where months >= to_char(now() - INTERVAL '12 month', 'YYYY-MM'))
from (select
    buyer,
    to_char(release_date, 'YYYY-MM') as months,
    count (distinct ocid) as notice_count
from
    bluetail_ocds_tender_view rel
    LEFT JOIN bluetail_ocds_package_data_view pac ON (rel.package_data_id = pac.id)
    LEFT JOIN input_supplieddata sup on (pac.supplied_data_id = sup.id)
where rel.package_data_id notnull
group by rel.buyer,
         months) sub
group by buyer, months
;


