select
    water_id,
    site_id,
    water_date,
    water_consumption_m3,
    water_cost

from {{ source('helios', 'water') }}