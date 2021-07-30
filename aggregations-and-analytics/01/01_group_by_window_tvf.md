# 01 Aggregating Time Series Data

![Twitter Badge](https://img.shields.io/badge/Flink%20Version-1.13%2B-lightgrey)

> :bulb: This example will show how to aggregate time series data in real-time using a `TUMBLE` window.

The source table (`server_logs`) is backed by the [`faker` connector](https://flink-packages.org/packages/flink-faker), which continuously generates rows in memory based on Java Faker expressions.

Many streaming applications work with time series data.
To count the number of `DISTINCT` IP addresses seen each minute, rows need to be grouped based on a [time attribute](https://docs.ververica.com/user_guide/sql_development/table_view.html#time-attributes).
Grouping based on time is special, because time always moves forward, which means Flink can generate final results after the minute is completed.

`TUMBLE` is a [built-in function](https://ci.apache.org/projects/flink/flink-docs-stable/docs/dev/table/sql/queries/window-agg/) for grouping timestamps into time intervals called windows. Windows split the stream into “buckets” of finite size, over which we can apply computations.
Unlike other aggregations such as `HOP` or `CUMULATE`, it will only produce a single final result for each key when the interval is completed.

If the logs do not have a timestamp, one can be generated using a [computed column](https://docs.ververica.com/user_guide/sql_development/table_view.html#computed-column).
`log_time AS PROCTIME()` will append a column to the table with the current system time.

## Script

```sql
CREATE TABLE server_logs ( 
    client_ip STRING,
    client_identity STRING, 
    userid STRING, 
    request_line STRING, 
    status_code STRING, 
    log_time AS PROCTIME()
) WITH (
  'connector' = 'faker', 
  'fields.client_ip.expression' = '#{Internet.publicIpV4Address}',
  'fields.client_identity.expression' =  '-',
  'fields.userid.expression' =  '-',
  'fields.log_time.expression' =  '#{date.past ''15'',''5'',''SECONDS''}',
  'fields.request_line.expression' = '#{regexify ''(GET|POST|PUT|PATCH){1}''} #{regexify ''(/search\.html|/login\.html|/prod\.html|cart\.html|/order\.html){1}''} #{regexify ''(HTTP/1\.1|HTTP/2|/HTTP/1\.0){1}''}',
  'fields.status_code.expression' = '#{regexify ''(200|201|204|400|401|403|301){1}''}'
);

SELECT window_start, window_end, COUNT(DISTINCT client_ip) AS ip_addresses
  FROM TABLE(
    TUMBLE(TABLE server_logs, DESCRIPTOR(log_time), INTERVAL '1' MINUTE))
  GROUP BY window_start, window_end;
```

## Example Output

![01_group_by_window](01_group_by_window_tvf_result.png)
