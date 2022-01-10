# 03 Analyzing Sessions in Time Series Data

> :bulb: This example will show how to aggregate time-series data in real-time using a `SESSION` window.

The source table (`server_logs`) is backed by the [`faker` connector](https://flink-packages.org/packages/flink-faker), which continuously generates rows in memory based on Java Faker expressions.

#### What are Session Windows?

In a [previous recipe](../01_group_by_window/01_group_by_window.md), you learned about _tumbling windows_. Another way to group time-series data is using [_session windows_](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/sql/queries.html#group-windows), which aggregate records into _sessions_ that represent periods of activity followed by gaps of idleness. Think, for example, of user sessions on a website: a user will be active for a given period of time, then leave the website; and each user will be active at different times. To analyze user behaviour, it's useful to aggregate their actions on the website for each period of activity (i.e. _session_).

Unlike tumbling windows, session windows don't have a fixed duration and are tracked independenlty across keys (i.e. windows of different keys will have different durations).

#### Using Session Windows

To count the number of "Forbidden" (403) requests per user over the duration of a session, you can use the `SESSION` built-in group window function. In this example, a session is bounded by a gap of idleness of 10 seconds (`INTERVAL '10' SECOND`). This means that requests that occur within 10 seconds of the last seen request for each user will be merged into the same session window; and any request that occurs outside of this gap will trigger the creation of a new session window.

> Tip: You can use the `SESSION_START` and `SESSION_ROWTIME` [auxiliary functions](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/sql/queries.html#selecting-group-window-start-and-end-timestamps) to check the lower and upper bounds of session windows.


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

SELECT  
  userid,
  SESSION_START(log_time, INTERVAL '10' SECOND) AS session_beg,
  SESSION_ROWTIME(log_time, INTERVAL '10' SECOND) AS session_end,
  COUNT(request_line) AS request_cnt
FROM server_logs
WHERE status_code = '403'
GROUP BY 
  userid, 
  SESSION(log_time, INTERVAL '10' SECOND);
```

## Example Output

![03_session_windows](https://user-images.githubusercontent.com/23521087/101628701-7ae31900-3a20-11eb-89c2-231649b7d99f.png)
