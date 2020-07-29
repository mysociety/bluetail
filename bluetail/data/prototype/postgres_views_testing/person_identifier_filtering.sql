select *
from
    bluetail_bods_personstatement_view per
  , LATERAL jsonb_array_elements(per.identifiers_json) identifiers

--     LEFT JOIN LATERAL ON per.identifiers_json
-- where identifiers_json ;

select *
from
    bluetail_bods_personstatement_view per

WHERE
    per.identifiers_json @> '[{"id": "HMCI17014140912423", "schemeName": "National ID"}]'
--     LEFT JOIN LATERAL ON per.identifiers_json
-- where identifiers_json ;

SELECT
    "bluetail_bods_personstatement_view"."statement_id",
    "bluetail_bods_personstatement_view"."statement_json",
    "bluetail_bods_personstatement_view"."identifiers_json",
    "bluetail_bods_personstatement_view"."fullName",
    "bluetail_bods_personstatement_view"."personType"
FROM
    "bluetail_bods_personstatement_view"
WHERE
    "bluetail_bods_personstatement_view"."identifiers_json" @> '[{"id": "HMCI17014140912423", "schemeName": "National ID"}]'

select *
from
    bluetail_bods_personstatement_view
where statement_id = '019a93f1-e470-42e9-957b-03554681b2e3';