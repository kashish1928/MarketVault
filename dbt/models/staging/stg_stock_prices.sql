with source as (
    select * from {{ source('public', 'raw_stock_data') }}
),

renamed as (
    select
        cast("date" as date) as stock_date,
        cast("ticker" as varchar(10)) as ticker,
        cast("open" as numeric(12, 4)) as open_price,
        cast("high" as numeric(12, 4)) as high_price,
        cast("low" as numeric(12, 4)) as low_price,
        cast("close" as numeric(12, 4)) as close_price,
        cast("volume" as bigint) as volume
    from source
    where "date" is not null and "ticker" is not null
)

select * from renamed
