# 03 Aggregating Data

:bulb: This example will show how to aggregate server logs in real-time using the standard `GROUP BY` clause.

The source table (`server_logs`) is backed by the [`faker` connector](https://github.com/knaufk/flink-faker), which continuously generates rows in memory based on Java Faker expressions.

To count the number of logs received for each status code _over time_, you can combine the `COUNT` aggregate function with a `GROUP BY` clause. A `GROUP BY` on a streaming table produces an updating result, so you will see the aggregated count for each status code continuously changing as new rows flow in.

> As an exercise, you can play around with other standard SQL aggregate functions (e.g. `SUM`,`AVG`,`MIN`,`MAX`).

## Script

```sql
CREATE TABLE server_logs ( 
    client_ip STRING,
    client_identity STRING, 
    userid STRING, 
    log_time TIMESTAMP(3),
    request_line STRING, 
    status_code STRING, 
    size INT
) WITH (
  'connector' = 'faker', 
  'fields.client_ip.expression' = '#{Internet.publicIpV4Address}',
  'fields.client_identity.expression' =  '-',
  'fields.userid.expression' =  '-',
  'fields.log_time.expression' =  '#{date.past ''15'',''5'',''SECONDS''}',
  'fields.request_line.expression' = '#{regexify ''(GET|POST|PUT|PATCH){1}''} #{regexify ''(/search\.html|/login\.html|/prod\.html|cart\.html|/order\.html){1}''} #{regexify ''(HTTP/1\.1|HTTP/2|/HTTP/1\.0){1}''}',
  'fields.status_code.expression' = '#{regexify ''(200|201|204|400|401|403|301){1}''}',
  'fields.size.expression' = '#{number.numberBetween ''100'',''10000000''}'
);

SELECT status_code, 
       COUNT(*) AS cnt_status
FROM server_logs
GROUP BY status_code;
```

## Example Output

This example can be run in the [SQL Client](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/sqlClient.html), a command line tool to develop and execute Flink SQL queries that is bundled in Flink.

![03_groupby](https://user-images.githubusercontent.com/23521087/100947812-b3f22980-3506-11eb-995b-0df204155524.gif)
