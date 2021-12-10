# 07 Encapsulating Logic with (Temporary) Views

![Twitter Badge](https://img.shields.io/badge/Flink%20Version-1.11%2B-lightgrey)

> :bulb: This example will show how you can use (temporary) views to reuse code and to structure long queries and scripts. 

`CREATE (TEMPORARY) VIEW` defines a view from a query. 
**A view is not physically materialized.** 
Instead, the query is run every time the view is referenced in a query.

Temporary views are very useful to structure and decompose more complicated queries and to re-use queries within a longer script.
Non-temporary views - stored in a persistent [catalog](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/catalogs.html) - can also be used to share common queries within your organization, e.g. common filters or pre-processing steps.  

Here, we create a view on the `server_logs` that only contains successful requests. 
This view encapsulates the logic of filtering the logs based on certain `status_code`s. 
This logic can subsequently be used by any query or script that has access to the catalog.   

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

CREATE VIEW successful_requests AS 
SELECT * 
FROM server_logs
WHERE status_code SIMILAR TO '[2,3][0-9][0-9]';

SELECT * FROM successful_requests;
```

## Example Output

![views](https://user-images.githubusercontent.com/11538663/102009292-c5250c80-3d36-11eb-85b3-05b8faf8df5a.gif)

