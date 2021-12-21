# 03 Working with Temporary Tables

![Twitter Badge](https://img.shields.io/badge/Flink%20Version-1.11%2B-lightgrey)

> :bulb: This example will show how and why to create a temporary table using SQL DDL.

Non-temporary tables in Flink SQL are stored in a catalog, while temporary tables only live within the current session (Apache Flink CLI) or script (Ververica Platform). 
You can use a temporary table instead of a regular (catalog) table, if it is only meant to be used within the current session or script.

This example is exactly the same as [Inserting Into Tables](../02_insert_into/02_insert_into.md) except that both `server_logs` and `client_errors` are created as temporary tables.

### Why Temporary Tables?

For result tables like `client_errors` that no one can ever read from (because of its type `blackhole`) it makes a lot of sense to use a temporary table instead of publishing its metadata in a catalog. 

Furthermore, temporary tables allow you to create fully self-contained scripts, which is why we will mostly use those in the Flink SQL Cookbook.

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

CREATE TEMPORARY TABLE client_errors (
  log_time TIMESTAMP(3),
  request_line STRING,
  status_code STRING,
  size INT
)
WITH (
  'connector' = 'blackhole'
);

INSERT INTO client_errors
SELECT 
  log_time,
  request_line,
  status_code,
  size
FROM server_logs
WHERE 
  status_code SIMILAR TO '4[0-9][0-9]';
```

## Example Output

In comparison to [Inserting Into Tables](../02_insert_into/02_insert_into.md), you can see that the two temporary tables do not appear in the catalog browser on the left. 
The table definitions never make it into the catalog, but are just submitted as part of the script that contains the `INSERT INTO` statement.

![Screencast GIF](https://user-images.githubusercontent.com/11538663/101192652-aac6a100-365b-11eb-82a3-5b86522e772c.gif)
  