with production_by_product as (

    select
        site_id,
        production_date,
        product_id,
        sum(quantity_produced) as quantity_produced

    from {{ ref('stg_production') }}

    group by
        site_id,
        production_date,
        product_id
),

production_with_total as (

    select
        site_id,
        production_date,
        product_id,
        quantity_produced,

        sum(quantity_produced) over (
            partition by site_id, production_date
        ) as total_quantity_produced

    from production_by_product
)

select
    site_id,
    production_date,
    product_id,
    quantity_produced,
    total_quantity_produced,

    quantity_produced / nullif(
        total_quantity_produced,
        0
    ) as production_share

from production_with_total