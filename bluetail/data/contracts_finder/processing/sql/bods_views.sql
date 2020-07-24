-- SQL used to aid in debugging and fixing the duplicate and malformed Companies House IDs
SELECT
    b.statement_id,
    b.statement_json -> 'identifiers'                          AS identifiers_json,
                jsonb_agg(identifiers.value) identifiers_json
FROM
    bluetail_bods_statement_json b
        LEFT JOIN LATERAL (
            select distinct on (identifier)
                identifier.value
            from jsonb_array_elements(b.statement_json -> 'identifiers') identifier(value)
            where
                NOT (identifier ->> 'scheme' notnull AND identifier ->> 'scheme' = 'GB-COH' AND length(identifier ->> 'id') < 8)
        ) identifiers ON TRUE
WHERE TRUE
--            AND b.statement_json ->> 'statementType' = 'entityStatement'
  AND statement_id = 'openownership-register-5867724539491802071'
--   AND statement_id = 'openownership-register-6008205498718995750'
--     and ch_id notnull
group by statement_id
;


-- Show BODS statements that have Companies House number less than 8 digits only and NOT one EQUAL to 8 digits
SELECT
    b.statement_id
  , *
FROM
    bluetail_bods_entitystatement_view b
    LEFT JOIN LATERAL jsonb_array_elements(b.statement_json -> 'identifiers') ch_id(value) ON (ch_id.value ->> 'scheme' = 'GB-COH')
WHERE
    b.statement_id in (
        SELECT
            b.statement_id
        FROM
            bluetail_bods_entitystatement_view b
                LEFT JOIN LATERAL jsonb_array_elements(b.statement_json -> 'identifiers') ch_id(value) ON (ch_id.value ->> 'scheme' = 'GB-COH')
        WHERE
              TRUE
          AND length(ch_id ->> 'id') < 8
    )
    AND NOT b.statement_id in (
        SELECT
            b.statement_id
        FROM
            bluetail_bods_entitystatement_view b
                LEFT JOIN LATERAL jsonb_array_elements(b.statement_json -> 'identifiers') ch_id(value) ON (ch_id.value ->> 'scheme' = 'GB-COH')
        WHERE
              TRUE
          AND length(ch_id ->> 'id') = 8
    )
--           AND b.statement_json ->> 'statementType' = 'entityStatement'
--           AND statement_id = 'openownership-register-5867724539491802071'
;
