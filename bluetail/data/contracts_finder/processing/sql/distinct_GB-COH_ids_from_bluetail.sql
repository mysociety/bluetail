-- Distinct CH IDs to lookup in OpenOwnership data
select distinct
    party_identifier_scheme,
    party_identifier_id
from
    public.bluetail_ocds_parties_view
where
    party_identifier_scheme = 'GB-COH'
order by party_identifier_id
;