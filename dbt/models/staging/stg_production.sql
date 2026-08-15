select
    production_id,
    site_id,
    product_id,
    production_date,
    quantity_produced,
    production_duration_minutes

from {{ source('helios', 'production') }}