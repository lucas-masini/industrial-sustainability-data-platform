select
    supplier_id,
    supplier_code,
    supplier_name,
    country,
    supplier_type,
    iso14001_certified,
    sustainability_score,

    case
        when iso14001_certified = 1
        then 'Certifié'
        else 'Non certifié'
    end as iso14001_status

from {{ ref('stg_supplier') }}