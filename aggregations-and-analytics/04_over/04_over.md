# 04 Rolling Aggregations on Time Series Data

> :bulb: This example will show how to calculate an aggregate or cumulative value based on a group of rows using an `OVER` window. A typical use case are rolling aggregations.

The source table (`temperature_measurements`) is backed by the [`faker` connector](https://flink-packages.org/packages/flink-faker), which continuously generates rows in memory based on Java Faker expressions.

OVER window aggregates compute an aggregated value for every input row over a range of ordered rows. 
In contrast to GROUP BY aggregates, OVER aggregates do not reduce the number of result rows to a single row for every group. 
Instead, OVER aggregates produce an aggregated value for every input row.

The order needs to be defined by a [time attribute](https://docs.ververica.com/user_guide/sql_development/table_view.html#time-attributes). 
The range of rows can be defined by a number of rows or a time interval. 

In this example, we are trying to identify outliers in the `temperature_measurements` table. 
For this, we use an `OVER` window to calculate, for each measurement, the maximum (`MAX`), minimum (`MIN`) and average (`AVG`) temperature across all measurements, as well as the standard deviation (`STDDEV`), for the same city over the previous minute. 
> As an exercise, you can try to write another query to filter out any temperature measurement that are higher or lower than the average by more than four standard deviations.

## Script

```sql
CREATE TEMPORARY TABLE temperature_measurements (
  measurement_time TIMESTAMP(3),
  city STRING,
  temperature FLOAT, 
  WATERMARK FOR measurement_time AS measurement_time - INTERVAL '15' SECONDS
)
WITH (
  'connector' = 'faker',
  'fields.measurement_time.expression' = '#{date.past ''15'',''SECONDS''}',
  'fields.temperature.expression' = '#{number.numberBetween ''0'',''50''}',
  'fields.city.expression' = '#{regexify ''(Chicago|Munich|Berlin|Portland|Hangzhou|Seatle|Beijing|New York){1}''}'
);

SELECT 
  measurement_time,
  city, 
  temperature,
  AVG(CAST(temperature AS FLOAT)) OVER last_minute AS avg_temperature_minute,
  MAX(temperature) OVER last_minute AS min_temperature_minute,
  MIN(temperature) OVER last_minute AS max_temperature_minute,
  STDDEV(CAST(temperature AS FLOAT)) OVER last_minute AS stdev_temperature_minute
FROM temperature_measurements 
WINDOW last_minute AS (
  PARTITION BY city
  ORDER BY measurement_time
  RANGE BETWEEN INTERVAL '1' MINUTE PRECEDING AND CURRENT ROW 
);
```
## Example Output

![04_over](https://user-images.githubusercontent.com/23521087/105503670-2beafd80-5cc7-11eb-9e58-7a4ed71b1d7c.png)
