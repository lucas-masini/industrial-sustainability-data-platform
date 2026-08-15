select
    energy_source_id,
    energy_source_code,
    energy_source_name,
    renewable

from {{ source('helios', 'energy_source') }}