select
    w.waste_id,

    w.site_id,
    s.site_name,
    s.city,
    s.country,

    w.waste_date,
    w.waste_type,

    w.waste_quantity_kg,
    w.recyclable,

    case
        when w.recyclable = 1
        then w.waste_quantity_kg
        else 0
    end as recyclable_quantity_kg

from {{ ref('stg_waste') }} w

inner join {{ ref('stg_site') }} s
    on w.site_id = s.site_id