with energy as (

    select
        site_id,
        energy_source_id,
        energy_date,
        energy_consumption_kwh,
        energy_cost

    from {{ ref('stg_energy') }}
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
    e.site_id,
    p.product_id,
    e.energy_source_id,
    e.energy_date,
    p.quantity_produced,
    p.total_quantity_produced,
    p.production_share,

    e.energy_consumption_kwh * p.production_share
        as allocated_energy_consumption_kwh,

    e.energy_cost * p.production_share
        as allocated_energy_cost

from energy e

inner join production_share p
    on e.site_id = p.site_id
    and e.energy_date = p.production_date