# 04 Filtering Data

> :bulb: This example will show how to filter server logs in real-time using a standard `WHERE` clause.

The table it uses, `server_logs`,  is backed by the [`faker` connector](https://flink-packages.org/packages/flink-faker) which continuously generates rows in memory based on Java Faker expressions and is convenient for testing queries. 
As such, it is an alternative to the built-in `datagen` connector used for example in [the first recipe](../01_create_table/01_create_table.md).

You can continuously filter these logs for those requests that experience authx issues with a simple `SELECT` statement with a `WHERE` clause filtering on the auth related HTTP status codes. 
In Ververica Platform you  will see the results printed to the UI in the query preview.

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

SELECT 
  log_time, 
  request_line,
  status_code 
FROM server_logs
WHERE
  status_code IN ('403', '401');
```

## Example Output

![04_where](https://user-images.githubusercontent.com/23521087/105504095-a6b41880-5cc7-11eb-9606-978e86add144.png)
