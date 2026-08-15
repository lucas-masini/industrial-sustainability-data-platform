select
    energy_id,
    site_id,
    energy_source_id,
    energy_date,
    energy_consumption_kwh,
    energy_cost

from {{ source('helios', 'energy') }}