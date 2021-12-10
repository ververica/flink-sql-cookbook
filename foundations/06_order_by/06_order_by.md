# 06 Sorting Tables 

> :bulb: This example will show how you can sort a table, particularly unbounded tables. 

Flink SQL supports `ORDER BY`. 
Bounded Tables can be sorted by any column, descending or ascending. 

To use `ORDER BY` on unbounded tables like `server_logs` the primary sorting key needs to be a [time attribute](https://docs.ververica.com/user_guide/sql_development/table_view.html#time-attributes) like `log_time`.

In first example below, we are sorting the `server_logs` by `log_time`. 
The second example is a bit more advanced: 
It sorts the number of logs per minute and browser by the `window_time` (a time attribute) and the `cnt_browser` (descending), so that the browser with the highest number of logs is at the top of each window.

## Script

```sql
CREATE TEMPORARY TABLE server_logs ( 
    client_ip STRING,
    client_identity STRING, 
    userid STRING, 
    user_agent STRING,
    log_time TIMESTAMP(3),
    request_line STRING, 
    status_code STRING, 
    size INT, 
    WATERMARK FOR log_time AS log_time - INTERVAL '15' SECONDS
) WITH (
  'connector' = 'faker', 
  'fields.client_ip.expression' = '#{Internet.publicIpV4Address}',
  'fields.client_identity.expression' =  '-',
  'fields.userid.expression' =  '-',
  'fields.user_agent.expression' = '#{Internet.userAgentAny}',
  'fields.log_time.expression' =  '#{date.past ''15'',''5'',''SECONDS''}',
  'fields.request_line.expression' = '#{regexify ''(GET|POST|PUT|PATCH){1}''} #{regexify ''(/search\.html|/login\.html|/prod\.html|cart\.html|/order\.html){1}''} #{regexify ''(HTTP/1\.1|HTTP/2|/HTTP/1\.0){1}''}',
  'fields.status_code.expression' = '#{regexify ''(200|201|204|400|401|403|301){1}''}',
  'fields.size.expression' = '#{number.numberBetween ''100'',''10000000''}'
);

SELECT * FROM server_logs 
ORDER BY log_time;
```

## Example Output

![06_order_by](https://user-images.githubusercontent.com/23521087/105504299-e24ee280-5cc7-11eb-8935-ed203e604f8d.png)

## Advanced Example

<details>
    <summary>Advanced Example </summary>

### Script

```sql
CREATE TEMPORARY TABLE server_logs ( 
    client_ip STRING,
    client_identity STRING, 
    userid STRING, 
    user_agent STRING,
    log_time TIMESTAMP(3),
    request_line STRING, 
    status_code STRING, 
    size INT, 
    WATERMARK FOR log_time AS log_time - INTERVAL '15' SECONDS
) WITH (
  'connector' = 'faker', 
  'fields.client_ip.expression' = '#{Internet.publicIpV4Address}',
  'fields.client_identity.expression' =  '-',
  'fields.userid.expression' =  '-',
  'fields.user_agent.expression' = '#{Internet.userAgentAny}',
  'fields.log_time.expression' =  '#{date.past ''15'',''5'',''SECONDS''}',
  'fields.request_line.expression' = '#{regexify ''(GET|POST|PUT|PATCH){1}''} #{regexify ''(/search\.html|/login\.html|/prod\.html|cart\.html|/order\.html){1}''} #{regexify ''(HTTP/1\.1|HTTP/2|/HTTP/1\.0){1}''}',
  'fields.status_code.expression' = '#{regexify ''(200|201|204|400|401|403|301){1}''}',
  'fields.size.expression' = '#{number.numberBetween ''100'',''10000000''}'
);

SELECT 
  TUMBLE_ROWTIME(log_time, INTERVAL '1' MINUTE) AS window_time,
  REGEXP_EXTRACT(user_agent,'[^\/]+') AS browser,
  COUNT(*) AS cnt_browser
FROM server_logs
GROUP BY 
  REGEXP_EXTRACT(user_agent,'[^\/]+'),
  TUMBLE(log_time, INTERVAL '1' MINUTE)
ORDER BY
  window_time,
  cnt_browser DESC;
```

### Example Output

![06_order_by_advanced](https://user-images.githubusercontent.com/23521087/105504249-d5ca8a00-5cc7-11eb-984a-e1eaf6622995.png)

</details>
