select
    t.transport_id,

    t.site_id,
    s.site_name,
    s.city,
    s.country,

    t.supplier_id,
    sup.supplier_code,
    sup.supplier_name,
    sup.sustainability_score,

    t.transport_company_id,
    tc.transport_company_code,
    tc.transport_company_name,
    tc.transport_type,

    t.transport_date,

    t.distance_km,
    t.transported_weight_kg,
    t.co2_emissions_kg,
    t.transport_cost,

    case
        when t.transported_weight_kg > 0
        then t.co2_emissions_kg / t.transported_weight_kg
        else null
    end as co2_per_kg_transported

from {{ ref('stg_transport') }} t

inner join {{ ref('stg_site') }} s
    on t.site_id = s.site_id

inner join {{ ref('stg_supplier') }} sup
    on t.supplier_id = sup.supplier_id

inner join {{ ref('stg_transport_company') }} tc
    on t.transport_company_id = tc.transport_company_id