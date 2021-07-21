# 10 Windowing table-valued functions

![Twitter Badge](https://img.shields.io/badge/Flink%20Version-1.13%2B-lightgrey)

> :bulb: This example will show how to apply computations on data in a temporal window using Windows table-valued functions `TUMBLE`, `HOP` and `CUMULATE`.

The source table (`server_logs`) is backed by the [`faker` connector](https://flink-packages.org/packages/flink-faker), which continuously generates rows in memory based on Java Faker expressions.

#### What are Windowing Table-valued functions (TVFs)?

Windows split the stream into “buckets” of finite size, over which we can apply computations.
[Windowing TVFs](https://ci.apache.org/projects/flink/flink-docs-stable/docs/dev/table/sql/queries/window-tvf/) are Flink defined Polymorphic Table Functions (abbreviated PTF). PTF are a powerful feature to change the shape of a table.
Previous recipes ([1](../01/01_group_by_window.md)) ([2](../02/02_watermarks.md)) ([3](../03/03_group_by_session_window.md)) are all so-called Grouped Window Functions which are considered legacy. 

#### Using Windowing Table-valued functions (TVFs)

There are three examples to count the number of "Forbidden" (403) requests using different Windows TVFs.

* Using `TUMBLE` to provide the amount of 403 errors every 5 seconds. This means that all 403 errors that occur within 5 seconds of the last seen request will be merged in the same window; and any request that occurs outside of this gap will trigger the creation of a new session window. 
* Using `HOP` to provide every 5 seconds the count of 403 errors over the last 10 seconds. This means that all 403 errors that occurred within 5 seconds of the last seen request will be merged in the same window, which will be displayed every 10 seconds. 
* Using `CUMULATE` to provide the total number of 403 errors that happened every 10 seconds, with the start of the window changing every 1 minute. This means that a continous aggregrations of the amount of 403 happens every 1 minute, but the results will be displayed every 10 seconds. 

## Script

```sql
CREATE TABLE server_logs ( 
    client_ip STRING,
    client_identity STRING, 
    userid STRING, 
    log_time TIMESTAMP(3),
    request_line STRING, 
    status_code STRING, 
    WATERMARK FOR log_time AS log_time - INTERVAL '5' SECONDS
) WITH (
  'connector' = 'faker', 
  'rows-per-second' = '5',
  'fields.client_ip.expression' = '#{Internet.publicIpV4Address}',
  'fields.client_identity.expression' =  '-',
  'fields.userid.expression' =  '#{regexify ''(morsapaes|knauf|sjwiesman){1}''}',
  'fields.log_time.expression' =  '#{date.past ''5'',''SECONDS''}',
  'fields.request_line.expression' = '#{regexify ''(GET|POST|PUT|PATCH){1}''} #{regexify ''(/search\.html|/login\.html|/prod\.html|cart\.html|/order\.html){1}''} #{regexify ''(HTTP/1\.1|HTTP/2|/HTTP/1\.0){1}''}',
  'fields.status_code.expression' = '#{regexify ''(200|201|204|400|401|403|301){1}''}'
);

SELECT window_start, window_end, COUNT(status_code) AS TotalErrors
  FROM TABLE(
    TUMBLE(TABLE server_logs, DESCRIPTOR(log_time), INTERVAL '5' SECONDS))
  WHERE status_code = '403'
  GROUP BY window_start, window_end;

SELECT window_start, window_end, COUNT(status_code) AS TotalErrors
  FROM TABLE(
    HOP(TABLE server_logs, DESCRIPTOR(log_time), INTERVAL '5' SECONDS, INTERVAL '10' SECONDS))
  GROUP BY window_start, window_end;

SELECT window_start, window_end, COUNT(status_code) AS TotalErrors
  FROM TABLE(
    CUMULATE(TABLE server_logs, DESCRIPTOR(log_time), INTERVAL '10' SECONDS, INTERVAL '60' SECONDS))
  GROUP BY window_start, window_end;
```

## Example Output

[comment]: <> (![01_group_by_window]&#40;https://user-images.githubusercontent.com/23521087/105503522-fe05b900-5cc6-11eb-9c36-bd8dc2a8e9ce.png&#41;)
