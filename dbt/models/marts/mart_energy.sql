select
    e.site_id,
    s.site_name,
    s.city,
    s.country,

    e.product_id,
    p.product_name,
    p.product_category,

    e.energy_source_id,
    es.energy_source_code,
    es.energy_source_name,

    e.energy_date,

    e.quantity_produced,
    e.total_quantity_produced,
    e.production_share,

    e.allocated_energy_consumption_kwh,
    e.allocated_energy_cost

from {{ ref('int_energy_allocated') }} e

inner join {{ ref('stg_site') }} s
    on e.site_id = s.site_id

inner join {{ ref('stg_product') }} p
    on e.product_id = p.product_id

inner join {{ ref('stg_energy_source') }} es
    on e.energy_source_id = es.energy_source_id