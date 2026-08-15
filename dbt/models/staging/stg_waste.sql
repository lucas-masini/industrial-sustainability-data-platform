select
    waste_id,
    site_id,
    waste_date,
    waste_type,
    waste_quantity_kg,
    recyclable

from {{ source('helios', 'waste') }}