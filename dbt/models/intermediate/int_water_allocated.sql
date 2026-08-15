with water as (

    select
        site_id,
        water_date,
        water_consumption_m3,
        water_cost

    from {{ ref('stg_water') }}
),

production_share as (

    select
        site_id,
        production_date,
        product_id,
        quantity_produced,
        total_quantity_produced,
        production_share

    from {{ ref('int_production_product_share') }}
)

select
    w.site_id,
    p.product_id,
    w.water_date,

    p.quantity_produced,
    p.total_quantity_produced,
    p.production_share,

    w.water_consumption_m3 * p.production_share
        as allocated_water_consumption_m3,

    w.water_cost * p.production_share
        as allocated_water_cost

from water w

inner join production_share p
    on w.site_id = p.site_id
    and w.water_date = p.production_date