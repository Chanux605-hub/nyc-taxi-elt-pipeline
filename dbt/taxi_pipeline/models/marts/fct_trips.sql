with trips as (
    select * from {{ ref('int_trips_with_zones') }}
),

final as (
    select {{ dbt_utils.generate_surrogate_key(['vendor_id', 'pickup_datetime', 'dropoff_datetime', 'pickup_location_id', 'dropoff_location_id', 'total_amount']) }}
        as trip_id,
        vendor_id,
        pickup_datetime,
        dropoff_datetime,
        datediff('minute', pickup_datetime, dropoff_datetime)
                                as trip_duration_minutes,
        trip_distance,
        passenger_count,
        rate_code_id,
        payment_type,
        fare_amount,
        extra_charge,
        mta_tax,
        tip_amount,
        tolls_amount,
        congestion_surcharge,
        total_amount,
        pickup_location_id,
        pickup_borough,
        pickup_zone,
        pickup_service_zone,
        dropoff_location_id,
        dropoff_borough,
        dropoff_zone,
        dropoff_service_zone
    from trips
)

select * from final
