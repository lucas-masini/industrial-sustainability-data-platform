select
    w.site_id,
    s.site_name,
    s.city,
    s.country,

    w.product_id,
    p.product_name,
    p.product_category,

    w.water_date,

    w.quantity_produced,
    w.total_quantity_produced,
    w.production_share,

    w.allocated_water_consumption_m3,
    w.allocated_water_cost

from {{ ref('int_water_allocated') }} w

inner join {{ ref('stg_site') }} s
    on w.site_id = s.site_id

inner join {{ ref('stg_product') }} p
    on w.product_id = p.product_id