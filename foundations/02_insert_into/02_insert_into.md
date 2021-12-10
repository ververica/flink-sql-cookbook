# 02 Inserting Into Tables

> :bulb: This recipe shows how to insert rows into a table so that downstream applications can read them.

The source table (`server_logs`) is backed by the [`faker` connector](https://flink-packages.org/packages/flink-faker), which continuously generates rows in memory based on Java Faker expressions.

As outlined in [the first recipe](../01_create_table/01_create_table.md) Flink SQL operates on tables, that are stored in external systems.
To publish results of a query for consumption by downstream applications, you write the results of a query into a table. 
This table can be read by Flink SQL, or directly by connecting to the external system that is storing the data (e.g. an ElasticSearch index.)

This example takes the `server_logs` tables, filters for client errors, and writes these logs into another table called `client_errors`.
Any number of external systems could back the result table, including Apache Kafka, Apache Hive, ElasticSearch, JDBC, among many others. 
To keep this example self-contained, `client_errors` is of type `blackhole`: instead of actually writing the data to an external system, the table discards any rows written to it.

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

CREATE TABLE client_errors (
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

An INSERT INTO query that reads from an unbounded table (like `server_logs`) is a long-running application. 
When you run such a statement in Apache Flink's [SQL Client](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/sqlClient.html) a Flink Job will be submitted to the configured cluster. 
In Ververica Platform a so called Deployment will be created to manage the execution of the statement.

![Screenshot GIF](https://user-images.githubusercontent.com/11538663/101192280-22480080-365b-11eb-97e9-35f151027c6e.gif)
