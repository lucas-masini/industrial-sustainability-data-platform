select
    p.production_id,

    p.site_id,
    s.site_name,
    s.city,
    s.country,

    p.product_id,
    pr.product_code,
    pr.product_name,
    pr.product_category,

    p.production_date,

    p.quantity_produced,
    p.production_duration_minutes,

    case
        when p.production_duration_minutes > 0
        then p.quantity_produced / p.production_duration_minutes
        else null
    end as production_per_minute

from {{ ref('stg_production') }} p

inner join {{ ref('stg_site') }} s
    on p.site_id = s.site_id

inner join {{ ref('stg_product') }} pr
    on p.product_id = pr.product_id