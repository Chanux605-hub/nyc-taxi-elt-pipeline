with zones as (
    select * from {{ ref('stg_taxi_zones') }}
),

final as (
    select
        location_id,
        borough,
        zone,
        service_zone
    from zones
)

select * from final