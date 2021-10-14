# 01 Working with Dates and Timestamps

> :bulb: This example will show how to use [built-in date and time functions](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/functions/systemFunctions.html#temporal-functions) to manipulate temporal fields.

The source table (`subscriptions`) is backed by the [`faker` connector](https://flink-packages.org/packages/flink-faker), which continuously generates rows in memory based on Java Faker expressions.

#### Date and Time Functions

Working with dates and timestamps is commonplace in SQL, but your input may come in different types, formats or even timezones. Flink SQL has multiple built-in functions that are useful to deal with this kind of situation and make it convenient to handle temporal fields.

Assume you have a table with service subscriptions and that you want to continuously [filter](../../foundations/04_where/04_where.md) these subscriptions to find the ones that have associated payment methods expiring in less than 30 days. The `start_date` and `end_date` are [Unix timestamps](https://en.wikipedia.org/wiki/Unix_time) (i.e. epochs) — which are not very human-readable and should be converted. Also, you want to parse the `payment_expiration` timestamp into its corresponding day, month and year parts. What are some functions that would be useful?

* `TO_TIMESTAMP(string[, format])`: converts a `STRING` value to a `TIMESTAMP` using the specified format (default: 'yyyy-MM-dd HH:mm:ss')

* `FROM_UNIXTIME(numeric[, string])`: converts an epoch to a formatted `STRING` (default: 'yyyy-MM-dd HH:mm:ss')

* `DATE_FORMAT(timestamp, string)`: converts a `TIMESTAMP` to a `STRING` using the specified format

* `EXTRACT(timeintervalunit FROM temporal)`: returns a `LONG` extracted from the specified date part of a temporal field (e.g. `DAY`,`MONTH`,`YEAR`)

* `TIMESTAMPDIFF(unit, timepoint1, timepoint2)`: returns the number of time units (`SECOND`, `MINUTE`, `HOUR`, `DAY`, `MONTH` or `YEAR`) between `timepoint1` and `timepoint2`

* `CURRENT_TIMESTAMP`: returns the current SQL timestamp (UTC)

For a complete list of built-in date and time functions, check the Flink [documentation](https://ci.apache.org/projects/flink/flink-docs-stable/docs/dev/table/functions/systemfunctions/#temporal-functions).

> As an exercise, you can try to reproduce the same filtering condition using `TIMESTAMPADD` instead.

## Script

```sql
CREATE TABLE subscriptions ( 
    id STRING,
    start_date INT,
    end_date INT,
    payment_expiration TIMESTAMP(3)
) WITH (
  'connector' = 'faker',
  'fields.id.expression' = '#{Internet.uuid}', 
  'fields.start_date.expression' = '#{number.numberBetween ''1576141834'',''1607764234''}',
  'fields.end_date.expression' = '#{number.numberBetween ''1609060234'',''1639300234''}',
  'fields.payment_expiration.expression' = '#{date.future ''365'',''DAYS''}'
);

SELECT 
  id,
  TO_TIMESTAMP(FROM_UNIXTIME(start_date)) AS start_date,
  TO_TIMESTAMP(FROM_UNIXTIME(end_date)) AS end_date,
  DATE_FORMAT(payment_expiration,'YYYYww') AS exp_yweek,
  EXTRACT(DAY FROM payment_expiration) AS exp_day,     --same as DAYOFMONTH(ts)
  EXTRACT(MONTH FROM payment_expiration) AS exp_month, --same as MONTH(ts)
  EXTRACT(YEAR FROM payment_expiration) AS exp_year    --same as YEAR(ts)
FROM subscriptions
WHERE 
  TIMESTAMPDIFF(DAY,CAST(CURRENT_TIMESTAMP AS TIMESTAMP(3)),payment_expiration) < 30;
```

## Example Output

![12_date_time](https://user-images.githubusercontent.com/23521087/101981480-811a0500-3c6d-11eb-9b28-5603d76ba0e6.png)