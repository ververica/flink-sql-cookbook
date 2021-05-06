# 08 Writing Results into Multiple Tables

![Twitter Badge](https://img.shields.io/badge/Flink%20Version-1.13%2B-lightgrey)

> :bulb: In this recipe, you will learn how to use [Statement Sets](https://docs.ververica.com/user_guide/sql_development/sql_scripts.html#sql-statements) to run multiple `INSERT INTO` statements in a single, optimized Flink Job. 

Many product requirements involve outputting the results of a streaming application to two or more sinks, such as [Apache Kafka](https://docs.ververica.com/user_guide/sql_development/connectors.html#apache-kafka) for real-time use cases, or a [Filesystem](https://docs.ververica.com/user_guide/sql_development/connectors.html#file-system) for offline ones.
Other times, two queries are not the same but share some extensive intermediate operations.

When working with server logs, the support team would like to see the number of status codes per browser every 5 minutes to have real-time insights into a web pages' status.
Additionally, they would like the same information on an hourly basis made available as partitioned [Apache Parquet](https://docs.ververica.com/user_guide/sql_development/connectors.html#apache-parquet) files so they can perform historical analysis. 

We could quickly write two Flink SQL queries to solve both these requirements, but that would not be efficient. 
These queries have a lot of duplicated work, like reading the source logs Kafka topic and cleansing the data. 

Ververica Platform includes a feature called `STATEMENT SET`s, that allows for multiplexing `INSERT INTO` statements into a single query holistically optimized by Apache Flink and deployed as a single application. 

```sql
CREATE TEMPORARY TABLE server_logs ( 
    client_ip       STRING,
    client_identity STRING, 
    userid          STRING, 
    user_agent      STRING,
    log_time        TIMESTAMP(3),
    request_line    STRING, 
    status_code     STRING, 
    size            INT,
    WATERMARK FOR log_time AS log_time - INTERVAL '30' SECONDS
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

CREATE TEMPORARY TABLE realtime_aggregations (
  `browser`     STRING,
  `status_code` STRING,
  `end_time`    TIMESTAMP(3),
  `requests`    BIGINT NOT NULL
) WITH (
  'connector' = 'kafka',
  'topic' = 'browser-status-codes', 
  'properties.bootstrap.servers' = 'localhost:9092',
  'properties.group.id' = 'browser-countds',
  'format' = 'avro' 
);


CREATE TEMPORARY TABLE offline_datawarehouse (
    `browser`     STRING,
    `status_code` STRING,
    `dt`          STRING,
    `hour`        STRING,
    `requests`    BIGINT NOT NULL
) PARTITIONED BY (`dt`, `hour`) WITH (
  'connector' = 'filesystem',
  'path' = 's3://my-bucket/browser-into',
  'sink.partition-commit.trigger' = 'partition-time', 
  'format' = 'parquet' 
);

-- This is a shared view that will be used by both 
-- insert into statements
CREATE TEMPORARY VIEW browsers AS  
SELECT 
  REGEXP_EXTRACT(user_agent,'[^\/]+') AS browser,
  status_code,
  log_time
FROM server_logs;

BEGIN STATEMENT SET;
INSERT INTO realtime_aggregations
SELECT
    browser,
    status_code,
    TUMBLE_ROWTIME(log_time, INTERVAL '5' MINUTE) AS end_time,
    COUNT(*) requests
FROM browsers
GROUP BY 
    browser,
    status_code,
    TUMBLE(log_time, INTERVAL '5' MINUTE);
INSERT INTO offline_datawarehouse
SELECT
    browser,
    status_code,
    DATE_FORMAT(TUMBLE_ROWTIME(log_time, INTERVAL '1' HOUR), 'yyyy-MM-dd') AS `dt`,
    DATE_FORMAT(TUMBLE_ROWTIME(log_time, INTERVAL '1' HOUR), 'HH') AS `hour`,
    COUNT(*) requests
FROM browsers
GROUP BY 
    browser,
    status_code,
    TUMBLE(log_time, INTERVAL '1' HOUR);
END;
```

Looking at the deployed Job Graph, we can see Flink SQL only performs the shared computation once to achieve the most cost and resource-efficient execution of our query!

![08_jobgraph](https://user-images.githubusercontent.com/23521087/105504375-fb579380-5cc7-11eb-888e-12a1ce7d6f50.png)
