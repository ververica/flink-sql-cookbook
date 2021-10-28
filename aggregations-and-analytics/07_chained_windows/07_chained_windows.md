# 07 Chained (Event) Time Windows

> :bulb: This example will show how to efficiently aggregate time series data on two different levels of granularity.

The source table (`server_logs`) is backed by the [`faker` connector](https://flink-packages.org/packages/flink-faker), which continuously generates rows in memory based on Java Faker expressions.

Based on our `server_logs` table we would like to compute the average request size over one minute **as well as five minute (event) windows.** 
For this, you could run two queries, similar to the one in [Aggregating Time Series Data](../01_group_by_window/01_group_by_window.md). 
At the end of the page is the script and resulting JobGraph from this approach. 

In the main part, we will follow a slightly more efficient approach that chains the two aggregations: the one-minute aggregation output serves as the five-minute aggregation input.

We then use a [Statements Set](../../foundations/08_statement_sets/08_statement_sets.md) to write out the two result tables. 
To keep this example self-contained, we use two tables of type `blackhole` instead of `kafka`, `filesystem`, or any other [connectors](https://ci.apache.org/projects/flink/flink-docs-stable/docs/connectors/table/overview/). 

## Script

```sql
CREATE TEMPORARY TABLE server_logs ( 
    log_time TIMESTAMP(3),
    client_ip STRING,
    client_identity STRING, 
    userid STRING, 
    request_line STRING, 
    status_code STRING, 
    size INT, 
    WATERMARK FOR log_time AS log_time - INTERVAL '15' SECONDS
) WITH (
  'connector' = 'faker', 
  'fields.log_time.expression' =  '#{date.past ''15'',''5'',''SECONDS''}',
  'fields.client_ip.expression' = '#{Internet.publicIpV4Address}',
  'fields.client_identity.expression' =  '-',
  'fields.userid.expression' =  '-',
  'fields.request_line.expression' = '#{regexify ''(GET|POST|PUT|PATCH){1}''} #{regexify ''(/search\.html|/login\.html|/prod\.html|cart\.html|/order\.html){1}''} #{regexify ''(HTTP/1\.1|HTTP/2|/HTTP/1\.0){1}''}',
  'fields.status_code.expression' = '#{regexify ''(200|201|204|400|401|403|301){1}''}',
  'fields.size.expression' = '#{number.numberBetween ''100'',''10000000''}'
);

CREATE TEMPORARY TABLE avg_request_size_1m (
  window_start TIMESTAMP(3),
  window_end TIMESTAMP(3),
  avg_size BIGINT
)
WITH (
  'connector' = 'blackhole'
);

CREATE TEMPORARY TABLE avg_request_size_5m (
  window_start TIMESTAMP(3),
  window_end TIMESTAMP(3),
  avg_size BIGINT
)
WITH (
  'connector' = 'blackhole'
);

CREATE TEMPORARY VIEW server_logs_window_1m AS 
SELECT  
  TUMBLE_START(log_time, INTERVAL '1' MINUTE) AS window_start,
  TUMBLE_ROWTIME(log_time, INTERVAL '1' MINUTE) AS window_end,
  SUM(size) AS total_size,
  COUNT(*) AS num_requests
FROM server_logs
GROUP BY 
  TUMBLE(log_time, INTERVAL '1' MINUTE);


CREATE TEMPORARY VIEW server_logs_window_5m AS 
SELECT 
  TUMBLE_START(window_end, INTERVAL '5' MINUTE) AS window_start,
  TUMBLE_ROWTIME(window_end, INTERVAL '5' MINUTE) AS window_end,
  SUM(total_size) AS total_size,
  SUM(num_requests) AS num_requests
FROM server_logs_window_1m
GROUP BY 
  TUMBLE(window_end, INTERVAL '5' MINUTE);

BEGIN STATEMENT SET;

INSERT INTO avg_request_size_1m SELECT
  window_start,
  window_end, 
  total_size/num_requests AS avg_size
FROM server_logs_window_1m;

INSERT INTO avg_request_size_5m SELECT
  window_start,
  window_end, 
  total_size/num_requests AS avg_size
FROM server_logs_window_5m;

END;
```

## Example Output

### JobGraph

![jobgraph_chained](https://user-images.githubusercontent.com/23521087/105503848-5e94f600-5cc7-11eb-9a7f-2944dd4e1faf.png)

### Result 1 Minute Aggregations

![results_1m](https://user-images.githubusercontent.com/23521087/105503896-6c4a7b80-5cc7-11eb-958d-05d48c9921cf.png)

## Non-Chained Windows

<details>
    <summary>Non-Chained Windows</summary>

### Script

```shell script
CREATE TEMPORARY TABLE server_logs ( 
    log_time TIMESTAMP(3),
    client_ip STRING,
    client_identity STRING, 
    userid STRING, 
    request_line STRING, 
    status_code STRING, 
    size INT, 
    WATERMARK FOR log_time AS log_time - INTERVAL '15' SECONDS
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

CREATE TEMPORARY TABLE avg_request_size_1m (
  window_start TIMESTAMP(3),
  window_end TIMESTAMP(3),
  avg_size BIGINT
)
WITH (
  'connector' = 'blackhole'
);

CREATE TEMPORARY TABLE avg_request_size_5m (
  window_start TIMESTAMP(3),
  window_end TIMESTAMP(3),
  avg_size BIGINT
)
WITH (
  'connector' = 'blackhole'
);

CREATE TEMPORARY VIEW server_logs_window_1m AS 
SELECT  
  TUMBLE_START(log_time, INTERVAL '1' MINUTE) AS window_start,
  TUMBLE_ROWTIME(log_time, INTERVAL '1' MINUTE) AS window_end,
  SUM(size) AS total_size,
  COUNT(*) AS num_requests
FROM server_logs
GROUP BY 
  TUMBLE(log_time, INTERVAL '1' MINUTE);


CREATE TEMPORARY VIEW server_logs_window_5m AS 
SELECT 
  TUMBLE_START(log_time, INTERVAL '5' MINUTE) AS window_start,
  TUMBLE_ROWTIME(log_time, INTERVAL '5' MINUTE) AS window_end,
  SUM(size) AS total_size,
  COUNT(*) AS num_requests
FROM server_logs
GROUP BY 
  TUMBLE(log_time, INTERVAL '5' MINUTE);

BEGIN STATEMENT SET;

INSERT INTO avg_request_size_1m SELECT
  window_start,
  window_end, 
  total_size/num_requests AS avg_size
FROM server_logs_window_1m;

INSERT INTO avg_request_size_5m SELECT
  window_start,
  window_end, 
  total_size/num_requests AS avg_size
FROM server_logs_window_5m;

END;
```

### Example Output

#### JobGraph

![jobgraph_non_chained](https://user-images.githubusercontent.com/23521087/105503946-79676a80-5cc7-11eb-9e8e-15d39482fee9.png)

</details>
