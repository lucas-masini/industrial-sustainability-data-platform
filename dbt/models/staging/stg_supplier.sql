select
    supplier_id,
    supplier_code,
    supplier_name,
    country,
    supplier_type,
    iso14001_certified,
    sustainability_score

from {{ source('helios', 'supplier') }}