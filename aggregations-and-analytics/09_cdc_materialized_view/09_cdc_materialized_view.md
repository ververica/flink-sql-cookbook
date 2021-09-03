# 09 Maintaining Materialized Views with Change Data Capture (CDC) and Debezium

![Twitter Badge](https://img.shields.io/badge/Flink%20Version-1.11%2B-lightgrey)

> :bulb: This example will show how you can use Flink SQL and Debezium to maintain a materialized view based on database changelog streams.

In the world of analytics, databases are still mostly seen as static sources of data — like a collection of business state(s) just sitting there, waiting to be queried. The reality is that most of the data stored in these databases is continuously produced and is continuously changing, so...why not _stream_ it? 

Change Data Capture (CDC) allows you to do just that: track and propagate changes in a database based on its changelog (e.g. the [Write-Ahead-Log](https://www.postgresql.org/docs/current/wal-intro.html) in Postgres) to downstream consumers. [Debezium](https://debezium.io/) is a popular tool for CDC that Flink supports through **1)** the [Kafka SQL Connector](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/connectors/formats/debezium.html) and **2)** a set of "standalone" [Flink CDC Connectors](https://github.com/ververica/flink-cdc-connectors#flink-cdc-connectors).

#### Let's get to it!

In this example, you'll monitor a table with insurance claim data related to animal attacks in Australia, and use Flink SQL to maintain an aggregated **materialized view** that is **incrementally updated** with the latest claim costs. You can find a different version of this example deploying Debezium, Kafka and Kafka Connect in [this repository](https://github.com/morsapaes/flink-sql-CDC).

## Pre-requisites

You'll need a running Postgres service to follow this example, so we bundled everything up in a `docker-compose` script to keep it self-contained. The only pre-requisite is to have [Docker](https://docs.docker.com/get-docker/) installed on your machine. :whale:

To get the setup up and running, run:

`docker-compose build`

`docker-compose up -d`

Once all the services are up, you can start the Flink SQL client:

`docker-compose exec sql-client ./sql-client.sh`

## How it works

The source table is backed by the [`Flink CDC Postgres` connector](https://github.com/ververica/flink-cdc-connectors/wiki/Postgres-CDC-Connector), which reads the transaction log of the `postgres` database to continuously produce change events. So, whenever there is an `INSERT`, `UPDATE` or `DELETE` operation in the `claims.accident_claims` table, it will be propagated to Flink.

```sql
CREATE TABLE accident_claims (
    claim_id INT,
    claim_total FLOAT,
    claim_total_receipt VARCHAR(50),
    claim_currency VARCHAR(3),
    member_id INT,
    accident_date VARCHAR(20),
    accident_type VARCHAR(20),
    accident_detail VARCHAR(20),
    claim_date VARCHAR(20),
    claim_status VARCHAR(10),
    ts_created VARCHAR(20),
    ts_updated VARCHAR(20)
) WITH (
  'connector' = 'postgres-cdc',
  'hostname' = 'postgres',
  'port' = '5432',
  'username' = 'postgres',
  'password' = 'postgres',
  'database-name' = 'postgres',
  'schema-name' = 'claims',
  'table-name' = 'accident_claims'
 );
```

After creating the changelog table, you can query it to find out the aggregated insurance costs of all cleared claims per animal type (`accident_detail`):

```sql
SELECT accident_detail,
       SUM(claim_total) AS agg_claim_costs
FROM accident_claims
WHERE claim_status <> 'DENIED'
GROUP BY accident_detail;
```

How can you check that the CDC functionality is _actually_ working? The `docker` directory also includes a data generator script with a series of `INSERT` operations with new insurance claims (`postgres_datagen.sql`); if you run it, you can see how the query results update in (near) real-time:

`cat ./postgres_datagen.sql | docker exec -i flink-cdc-postgres psql -U postgres -d postgres`

In contrast to what would happen in a non-streaming SQL engine, using Flink SQL in combination with CDC allows you to get a consistent and continuous view of the state of the world, instead of a snapshot up to a specific point in time (i.e. the query's execution time).

## Example Output

![09_cdc_materialized_view](https://user-images.githubusercontent.com/23521087/109818653-81ee8180-7c33-11eb-9a76-b1004de8fe23.gif)
