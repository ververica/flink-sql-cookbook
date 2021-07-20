# 05 Aggregating Data

> :bulb: This example will show how to aggregate server logs in real-time using the standard `GROUP BY` clause.

The source table (`server_logs`) is backed by the [`faker` connector](https://flink-packages.org/packages/flink-faker), which continuously generates rows in memory based on Java Faker expressions.

To count the number of logs received per browser for each status code _over time_, you can combine the `COUNT` aggregate function with a `GROUP BY` clause. Because the `user_agent` field contains a lot of information, you can extract the browser using the built-in [string function](https://ci.apache.org/projects/flink/flink-docs-stable/docs/dev/table/functions/systemfunctions/#string-functions) `REGEXP_EXTRACT`.

A `GROUP BY` on a streaming table produces an updating result, so you will see the aggregated count for each browser continuously changing as new rows flow in.

> As an exercise, you can play around with other standard SQL aggregate functions (e.g. `SUM`,`AVG`,`MIN`,`MAX`).

## Script

```sql
CREATE TABLE server_logs ( 
    client_ip STRING,
    client_identity STRING, 
    userid STRING, 
    user_agent STRING,
    log_time TIMESTAMP(3),
    request_line STRING, 
    status_code STRING, 
    size INT
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

-- Sample user_agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A
-- Regex pattern: '[^\/]+' (Match everything before '/')
SELECT 
  REGEXP_EXTRACT(user_agent,'[^\/]+') AS browser,
  status_code, 
  COUNT(*) AS cnt_status
FROM server_logs
GROUP BY 
  REGEXP_EXTRACT(user_agent,'[^\/]+'),
  status_code;
```

## Example Output

This example can be run in the [SQL Client](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/sqlClient.html), a command line tool to develop and execute Flink SQL queries that is bundled in Flink.

![03_group_by](https://user-images.githubusercontent.com/23521087/101014385-19293780-3566-11eb-9d81-9c99d6ffa7e4.gif)
