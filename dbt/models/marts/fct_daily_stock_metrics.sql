with stg_prices as (
    select * from {{ ref('stg_stock_prices') }}
),

metrics as (
    select
        stock_date,
        ticker,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        (high_price - low_price) as daily_price_spread,
        round(
            cast(
                ((close_price - lag(close_price) over (partition by ticker order by stock_date)) / 
                nullif(lag(close_price) over (partition by ticker order by stock_date), 0)) * 100 
            as numeric), 4
        ) as daily_return_pct,
        round(
            cast(avg(close_price) over (
                partition by ticker 
                order by stock_date 
                rows between 6 preceding and current row
            ) as numeric), 4
        ) as moving_avg_7d,
        round(
            cast(avg(close_price) over (
                partition by ticker 
                order by stock_date 
                rows between 29 preceding and current row
            ) as numeric), 4
        ) as moving_avg_30d,
        round(
            cast(stddev(close_price) over (
                partition by ticker 
                order by stock_date 
                rows between 6 preceding and current row
            ) as numeric), 4
        ) as volatility_7d
    from stg_prices
)

select * from metrics
