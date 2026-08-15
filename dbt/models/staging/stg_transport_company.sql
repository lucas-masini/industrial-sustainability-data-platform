select
    transport_company_id,
    transport_company_code,
    transport_company_name,
    country,
    transport_type

from {{ source('helios', 'transport_company') }}