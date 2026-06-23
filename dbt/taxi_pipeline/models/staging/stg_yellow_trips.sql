with source as(
    select * from {{ source('raw', "yellow_trips") }}
),

cleaned as (
    select
        VENDORID                as vendor_id,
        TPEP_PICKUP_DATETIME    as pickup_datetime,
        TPEP_DROPOFF_DATETIME   as dropoff_datetime,
        PASSENGER_COUNT         as passenger_count,
        TRIP_DISTANCE           as trip_distance,
        RATECODEID              as rate_code_id,
        PULOCATIONID            as pickup_location_id,
        DOLOCATIONID            as dropoff_location_id,
        PAYMENT_TYPE            as payment_type,
        FARE_AMOUNT              as fare_amount,
        EXTRA                    as extra_charge,
        MTA_TAX                  as mta_tax,
        TIP_AMOUNT                as tip_amount,
        TOLLS_AMOUNT              as tolls_amount,
        TOTAL_AMOUNT               as total_amount,
        CONGESTION_SURCHARGE       as congestion_surcharge
    from source
    where TRIP_DISTANCE > 0 and  FARE_AMOUNT > 0 and  PASSENGER_COUNT > 0 

),

deduped as (
    select *,
        ROW_NUMBER() OVER (
            PARTITION BY pickup_datetime,
                         dropoff_datetime,
                         vendor_id,
                         pickup_location_id,
                         dropoff_location_id,
                         total_amount
            ORDER BY pickup_datetime
        ) as row_num
    from cleaned
)

select * exclude (row_num) from deduped
where row_num = 1