select
    *
from
    bluetail_ocds_tender_view rel
    LEFT JOIN bluetail_ocds_package_data_view pac ON (rel.package_data_id = pac.id)
    LEFT JOIN input_supplieddata sup on (pac.supplied_data_id = sup.id)
where rel.package_data_id notnull
;