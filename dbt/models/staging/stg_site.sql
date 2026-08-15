select
    site_id,
    site_name,
    city,
    country,
    surface_m2,
    employees_count

from {{ source('helios', 'site') }}