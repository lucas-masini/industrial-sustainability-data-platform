select
    product_id,
    site_id,
    product_code,
    product_name,
    product_category

from {{ source('helios', 'product') }}