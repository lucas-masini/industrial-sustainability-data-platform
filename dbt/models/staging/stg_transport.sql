select
    transport_id,
    supplier_id,
    transport_company_id,
    site_id,
    transport_date,
    distance_km,
    co2_emissions_kg,
    transport_cost,
    transported_weight_kg

from {{ source('helios', 'transport') }}