# 03 Temporal Table Join between a non-compacted and compacted Kafka Topic

> :bulb: In this recipe, you will see how to correctly enrich records from one Kafka topic with the corresponding records of another Kafka topic when the order of events matters.  

Temporal table joins take an arbitrary table (left input/probe site) and correlate each row to the corresponding row’s relevant version in a versioned table (right input/build side). 
Flink uses the SQL syntax of ``FOR SYSTEM_TIME AS OF`` to perform this operation. 

In this recipe, we want join each transaction (`transactions`) to its correct currency rate (`currency_rates`, a versioned table) **as of the time when the transaction happened**.
A similar example would be to join each order with the customer details as of the time when the order happened.
This is exactly what an event-time temporal table join does.
A temporal table join in Flink SQL provides correct, deterministic results in the presence of out-of-orderness and arbitrary time skew between the two tables. 

Both the `transactions` and `currency_rates` tables are backed by Kafka topics, but in the case of rates this topic is compacted (i.e. only the most recent messages for a given key are kept as updated rates flow in).
Records in `transactions` are interpreted as inserts only, and so the table is backed by the [standard Kafka connector](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/connectors/kafka.html) (`connector` = `kafka`); while the records in `currency_rates` need to be interpreted as upserts based on a primary key, which requires the [Upsert Kafka connector](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/connectors/upsert-kafka.html) (`connector` = `upsert-kafka`).

## Script

```sql
CREATE TEMPORARY TABLE currency_rates (
  `currency_code` STRING,
  `eur_rate` DECIMAL(6,4),
  `rate_time` TIMESTAMP(3),
  WATERMARK FOR `rate_time` AS rate_time - INTERVAL '15' SECONDS,
  PRIMARY KEY (currency_code) NOT ENFORCED
) WITH (
  'connector' = 'upsert-kafka',
  'topic' = 'currency_rates',
  'properties.bootstrap.servers' = 'localhost:9092',
  'key.format' = 'raw',
  'value.format' = 'json'
);

CREATE TEMPORARY TABLE transactions (
  `id` STRING,
  `currency_code` STRING,
  `total` DECIMAL(10,2),
  `transaction_time` TIMESTAMP(3),
  WATERMARK FOR `transaction_time` AS transaction_time - INTERVAL '30' SECONDS
) WITH (
  'connector' = 'kafka',
  'topic' = 'transactions',
  'properties.bootstrap.servers' = 'localhost:9092',
  'key.format' = 'raw',
  'key.fields' = 'id',
  'value.format' = 'json',
  'value.fields-include' = 'ALL'
);

SELECT 
  t.id,
  t.total * c.eur_rate AS total_eur,
  t.total, 
  c.currency_code,
  t.transaction_time
FROM transactions t
JOIN currency_rates FOR SYSTEM_TIME AS OF t.transaction_time AS c
ON t.currency_code = c.currency_code;
```

## Example Output

![kafka_join](https://user-images.githubusercontent.com/11538663/102418338-d2bfe800-3ffd-11eb-995a-13fa116b538f.gif)

## Data Generators

<details>
    <summary>Data Generators</summary>

The two topics are populated using a Flink SQL job, too. 
We use the  [`faker` connector](https://flink-packages.org/packages/flink-faker) to generate rows in memory based on Java Faker expressions and write those to the respective Kafka topics.  

### ``currency_rates`` Topic

### Script

```sql
CREATE TEMPORARY TABLE currency_rates_faker
WITH (
  'connector' = 'faker',
  'fields.currency_code.expression' = '#{Currency.code}',
  'fields.eur_rate.expression' = '#{Number.randomDouble ''4'',''0'',''10''}',
  'fields.rate_time.expression' = '#{date.past ''15'',''SECONDS''}', 
  'rows-per-second' = '100'
) LIKE currency_rates (EXCLUDING OPTIONS);

INSERT INTO currency_rates SELECT * FROM currency_rates_faker;
```
#### Kafka Topic

```shell script
➜  bin ./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic currency_rates --property print.key=true --property key.separator=" - "
HTG - {"currency_code":"HTG","eur_rate":0.0136,"rate_time":"2020-12-16 22:22:02"}
BZD - {"currency_code":"BZD","eur_rate":1.6545,"rate_time":"2020-12-16 22:22:03"}
BZD - {"currency_code":"BZD","eur_rate":3.616,"rate_time":"2020-12-16 22:22:10"}
BHD - {"currency_code":"BHD","eur_rate":4.5308,"rate_time":"2020-12-16 22:22:05"}
KHR - {"currency_code":"KHR","eur_rate":1.335,"rate_time":"2020-12-16 22:22:06"}
```

### ``transactions`` Topic

#### Script

```sql
CREATE TEMPORARY TABLE transactions_faker
WITH (
  'connector' = 'faker',
  'fields.id.expression' = '#{Internet.UUID}',
  'fields.currency_code.expression' = '#{Currency.code}',
  'fields.total.expression' = '#{Number.randomDouble ''2'',''10'',''1000''}',
  'fields.transaction_time.expression' = '#{date.past ''30'',''SECONDS''}',
  'rows-per-second' = '100'
) LIKE transactions (EXCLUDING OPTIONS);

INSERT INTO transactions SELECT * FROM transactions_faker;
```

#### Kafka Topic

```shell script
➜  bin ./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic transactions --property print.key=true --property key.separator=" - "
e102e91f-47b9-434e-86e1-34fb1196d91d - {"id":"e102e91f-47b9-434e-86e1-34fb1196d91d","currency_code":"SGD","total":494.07,"transaction_time":"2020-12-16 22:18:46"}
bf028363-5ee4-4a5a-9068-b08392d59f0b - {"id":"bf028363-5ee4-4a5a-9068-b08392d59f0b","currency_code":"EEK","total":906.8,"transaction_time":"2020-12-16 22:18:46"}
e22374b5-82da-4c6d-b4c6-f27a818a58ab - {"id":"e22374b5-82da-4c6d-b4c6-f27a818a58ab","currency_code":"GYD","total":80.66,"transaction_time":"2020-12-16 22:19:02"}
81b2ce89-26c2-4df3-b12a-8ca921902ac4 - {"id":"81b2ce89-26c2-4df3-b12a-8ca921902ac4","currency_code":"EGP","total":521.98,"transaction_time":"2020-12-16 22:18:57"}
53c4fd3f-af6e-41d3-a677-536f4c86e010 - {"id":"53c4fd3f-af6e-41d3-a677-536f4c86e010","currency_code":"UYU","total":936.26,"transaction_time":"2020-12-16 22:18:59"}
```

</details>
