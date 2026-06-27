-- getting raw data
with source as(
    select * from {{ source('raw', 'taxi_zones') }}
),

-- cleaning data
cleaned as (
    select
        LOCATIONID                                    as location_id,
        COALESCE(BOROUGH, 'Unknown')                  as borough,
        ZONE                                          as zone,
        COALESCE(SERVICE_ZONE, 'Unknown')             as service_zone
    from source
)

select * from cleaned