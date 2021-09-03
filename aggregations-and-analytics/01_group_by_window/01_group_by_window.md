# 01 Aggregating Time Series Data

> :warning: This recipe is using a legacy function. We recommend following the [new recipe](01_group_by_window_tvf.md).

The source table (`server_logs`) is backed by the [`faker` connector](https://flink-packages.org/packages/flink-faker), which continuously generates rows in memory based on Java Faker expressions.

Many streaming applications work with time series data.
To count the number of `DISTINCT` IP addresses seen each minute, rows need to be grouped based on a [time attribute](https://docs.ververica.com/user_guide/sql_development/table_view.html#time-attributes).
Grouping based on time is special, because time always moves forward, which means Flink can generate final results after the minute is completed. 

`TUMBLE` is a built-in function for grouping timestamps into time intervals called windows.
Unlike other aggregations, it will only produce a single final result for each key when the interval is completed. 

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

SELECT  
  COUNT(DISTINCT client_ip) AS ip_addresses,
  TUMBLE_PROCTIME(log_time, INTERVAL '1' MINUTE) AS window_interval
FROM server_logs
GROUP BY 
  TUMBLE(log_time, INTERVAL '1' MINUTE);
```

## Example Output

![01_group_by_window](https://user-images.githubusercontent.com/23521087/105503522-fe05b900-5cc6-11eb-9c36-bd8dc2a8e9ce.png)
