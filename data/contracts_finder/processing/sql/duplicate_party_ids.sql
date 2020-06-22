select *
from
    public.bluetail_ocds_parties_view
where
      ocid = 'ocds-b5fd17-0ac9f3a6-83f4-4f8a-874c-f927b48d445c'
  AND party_role = 'tenderer'
;

SELECT
    ocds.ocid,
    ocds.release_id,
    ocds.release_json,
    party                                 as party_json,
    role                                  AS party_role,
    party ->> 'id'                        as party_id,
    party -> 'identifier' ->> 'scheme'    as party_identifier_scheme,
    party -> 'identifier' ->> 'id'        as party_identifier_id,
    party -> 'identifier' ->> 'legalName' as party_legalname,
    party -> 'address' ->> 'countryName'  as party_countryname,

    party ->> 'name'                         party_name,
    party -> 'contactPoint' ->> 'name'    as contact_name
FROM
    bluetail_ocds_release_json ocds,
    LATERAL jsonb_array_elements(ocds.release_json -> 'parties') party,
    LATERAL jsonb_array_elements_text(party -> 'roles') role
WHERE
      role = 'tenderer'
  and ocid = 'ocds-b5fd17-0ac9f3a6-83f4-4f8a-874c-f927b48d445c'
