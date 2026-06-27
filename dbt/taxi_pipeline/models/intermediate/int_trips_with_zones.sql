with trips as (
    select * from {{ ref('stg_yellow_trips') }}
),

pickup_zones as (
    select * from {{ ref('stg_taxi_zones') }}
),

dropoff_zones as (
    select * from {{ ref('stg_taxi_zones') }}
),


joined as (
    select
        t.vendor_id,
        t.pickup_datetime,
        t.dropoff_datetime,
        t.passenger_count,
        t.trip_distance,
        t.rate_code_id,
        t.payment_type,
        t.fare_amount,
        t.extra_charge,
        t.mta_tax,
        t.tip_amount,
        t.tolls_amount,
        t.total_amount,
        t.congestion_surcharge,

        t.pickup_location_id,
        COALESCE(p.borough, 'Unknown')      as pickup_borough,
        COALESCE(p.zone, 'Unknown')         as pickup_zone,
        COALESCE(p.service_zone, 'Unknown') as pickup_service_zone,

        t.dropoff_location_id,
        COALESCE(d.borough, 'Unknown')       as dropoff_borough,
        COALESCE(d.zone, 'Unknown')          as dropoff_zone,
        COALESCE(d.service_zone, 'Unknown')  as dropoff_service_zone

    from trips t
    left join pickup_zones p
        on t.pickup_location_id = p.location_id
    left join dropoff_zones d
        on t.dropoff_location_id = d.location_id
)

select * from joined