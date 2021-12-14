# 12 Lag

![Twitter Badge](https://img.shields.io/badge/Flink%20Version-1.13%2B-lightgrey)

> :bulb: This example will show how to retrieve the previous value and compute trends for a specific data partition.

The source table (`fake_stocks`) is backed by the [`faker` connector](https://flink-packages.org/packages/flink-faker), which continuously generates fake stock quotation in memory based on Java Faker expressions.

In this recipe we're using the [LAG](https://nightlies.apache.org/flink/flink-docs-master/docs/dev/table/functions/systemfunctions/#aggregate-functions) function to retrieve the previous value for a specific stock and then calculate its trend.

```sql
CREATE TABLE fake_stocks ( 
    stock_name STRING,
    stock_value double, 
    log_time AS PROCTIME()
) WITH (
  'connector' = 'faker', 
  'fields.stock_name.expression' = '#{regexify ''(Deja\ Brew|Jurassic\ Pork|Lawn\ \&\ Order|Pita\ Pan|Bread\ Pitt|Indiana\ Jeans|Thai\ Tanic){1}''}',
  'fields.stock_value.expression' =  '#{number.randomDouble ''2'',''10'',''20''}',
  'fields.log_time.expression' =  '#{date.past ''15'',''5'',''SECONDS''}',
  'rows-per-second' = '10'
);

WITH current_and_previous as (
    select 
        stock_name,
        log_time, 
        stock_value, 
        lag(stock_value, 1) over (partition by stock_name order by log_time) previous_value 
    from fake_stocks
)
select *, 
    case 
        when stock_value > previous_value then '▲'
        when stock_value < previous_value then '▼'
        else '=' 
    end as trend 
from current_and_previous;
```

## Example Output

![12_lag](12_lag.png)
