# 05 Real Time Star Schema Denormalization (N-Way Join)

> :bulb: In this recipe, we will de-normalize a simple star schema with an n-way temporal table join. 	 
  
[Star schemas](https://en.wikipedia.org/wiki/Star_schema) are a popular way of normalizing data within a data warehouse. 
At the center of a star schema is a **fact table** whose rows contain metrics, measurements, and other facts about the world. 
Surrounding fact tables are one or more **dimension tables** which have metadata useful for enriching facts when computing queries.  
You are running a small data warehouse for a railroad company which consists of a fact table (`train_activity`) and three dimension tables (`stations`, `booking_channels`, and `passengers`). 
All inserts to the fact table, and all updates to the dimension tables, are mirrored to Apache Kafka. 
Records in the fact table are interpreted as inserts only, and so the table is backed by the [standard Kafka connector](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/connectors/kafka.html) (`connector` = `kafka`);. 
In contrast, the records in the dimensional tables are upserts based on a primary key, which requires the [Upsert Kafka connector](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/connectors/upsert-kafka.html) (`connector` = `upsert-kafka`).	 

With Flink SQL you can now easily join all dimensions to our fact table using a 5-way temporal table join. 	 
Temporal table joins take an arbitrary table (left input/probe site) and correlate each row to the corresponding row’s relevant version in a versioned table (right input/build side). 	 
Flink uses the SQL syntax of ``FOR SYSTEM_TIME AS OF`` to perform this operation.
Using a temporal table join leads to consistent, reproducible results when joining a fact table with more (slowly) changing dimensional tables.
Every event (row in the fact table) is joined to its corresponding value of each dimension based on when the event occurred in the real world. 

## Script

```sql
CREATE TEMPORARY TABLE passengers (
  passenger_key STRING, 
  first_name STRING, 
  last_name STRING,
  update_time TIMESTAMP(3),
  WATERMARK FOR update_time AS update_time - INTERVAL '10' SECONDS,
  PRIMARY KEY (passenger_key) NOT ENFORCED
) WITH (
  'connector' = 'upsert-kafka',
  'topic' = 'passengers',
  'properties.bootstrap.servers' = 'localhost:9092',
  'key.format' = 'raw',
  'value.format' = 'json'
);

CREATE TEMPORARY TABLE stations (
  station_key STRING, 
  update_time TIMESTAMP(3),
  city STRING,
  WATERMARK FOR update_time AS update_time - INTERVAL '10' SECONDS,
  PRIMARY KEY (station_key) NOT ENFORCED
) WITH (
  'connector' = 'upsert-kafka',
  'topic' = 'stations',
  'properties.bootstrap.servers' = 'localhost:9092',
  'key.format' = 'raw',
  'value.format' = 'json'
);

CREATE TEMPORARY TABLE booking_channels (
  booking_channel_key STRING, 
  update_time TIMESTAMP(3),
  channel STRING,
  WATERMARK FOR update_time AS update_time - INTERVAL '10' SECONDS,
  PRIMARY KEY (booking_channel_key) NOT ENFORCED
) WITH (
  'connector' = 'upsert-kafka',
  'topic' = 'booking_channels',
  'properties.bootstrap.servers' = 'localhost:9092',
  'key.format' = 'raw',
  'value.format' = 'json'
);

CREATE TEMPORARY TABLE train_activities (
  scheduled_departure_time TIMESTAMP(3),
  actual_departure_date TIMESTAMP(3),
  passenger_key STRING, 
  origin_station_key STRING, 
  destination_station_key STRING,
  booking_channel_key STRING,
  WATERMARK FOR actual_departure_date AS actual_departure_date - INTERVAL '10' SECONDS
) WITH (
  'connector' = 'kafka',
  'topic' = 'train_activities',
  'properties.bootstrap.servers' = 'localhost:9092',
  'value.format' = 'json',
  'value.fields-include' = 'ALL'
);

SELECT 
  t.actual_departure_date, 
  p.first_name,
  p.last_name,
  b.channel, 
  os.city AS origin_station,
  ds.city AS destination_station
FROM train_activities t
LEFT JOIN booking_channels FOR SYSTEM_TIME AS OF t.actual_departure_date AS b 
ON t.booking_channel_key = b.booking_channel_key;
LEFT JOIN passengers FOR SYSTEM_TIME AS OF t.actual_departure_date AS p
ON t.passenger_key = p.passenger_key
LEFT JOIN stations FOR SYSTEM_TIME AS OF t.actual_departure_date AS os
ON t.origin_station_key = os.station_key
LEFT JOIN stations FOR SYSTEM_TIME AS OF t.actual_departure_date AS ds
ON t.destination_station_key = ds.station_key;
```

## Example Output

### SQL Client

![05_output](https://user-images.githubusercontent.com/23521087/105504672-54272c00-5cc8-11eb-88da-901bb0006da1.png)

### JobGraph

![05_jobgraph](https://user-images.githubusercontent.com/23521087/105504615-440f4c80-5cc8-11eb-94f2-d07d0315dec5.png)

## Data Generators

<details>
    <summary>Data Generators</summary>

The four topics are populated with Flink SQL jobs, too.
We use the  [`faker` connector](https://flink-packages.org/packages/flink-faker) to generate rows in memory based on Java Faker expressions and write those to the respective Kafka topics.  

### ``train_activities`` Topic

### Script

```sql
CREATE TEMPORARY TABLE train_activities_faker
WITH (
  'connector' = 'faker', 
  'fields.scheduled_departure_time.expression' = '#{date.past ''10'',''0'',''SECONDS''}',
  'fields.actual_departure_date.expression' = '#{date.past ''10'',''5'',''SECONDS''}',
  'fields.passenger_key.expression' = '#{number.numberBetween ''0'',''10000000''}',
  'fields.origin_station_key.expression' = '#{number.numberBetween ''0'',''1000''}',
  'fields.destination_station_key.expression' = '#{number.numberBetween ''0'',''1000''}',
  'fields.booking_channel_key.expression' = '#{number.numberBetween ''0'',''7''}',
  'rows-per-second' = '1000'
) LIKE train_activities (EXCLUDING OPTIONS);

INSERT INTO train_activities SELECT * FROM train_activities_faker;
```
#### Kafka Topic

```shell script
➜  bin ./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic train_actitivies --property print.key=true --property key.separator=" - "
null - {"scheduled_departure_time":"2020-12-19 13:52:37","actual_departure_date":"2020-12-19 13:52:16","passenger_key":7014937,"origin_station_key":577,"destination_station_key":862,"booking_channel_key":2}
null - {"scheduled_departure_time":"2020-12-19 13:52:38","actual_departure_date":"2020-12-19 13:52:23","passenger_key":2244807,"origin_station_key":735,"destination_station_key":739,"booking_channel_key":2}
null - {"scheduled_departure_time":"2020-12-19 13:52:46","actual_departure_date":"2020-12-19 13:52:18","passenger_key":2605313,"origin_station_key":216,"destination_station_key":453,"booking_channel_key":3}
null - {"scheduled_departure_time":"2020-12-19 13:53:13","actual_departure_date":"2020-12-19 13:52:19","passenger_key":7111654,"origin_station_key":234,"destination_station_key":833,"booking_channel_key":5}
null - {"scheduled_departure_time":"2020-12-19 13:52:22","actual_departure_date":"2020-12-19 13:52:17","passenger_key":2847474,"origin_station_key":763,"destination_station_key":206,"booking_channel_key":3}
```

### ``passengers`` Topic

#### Script

```sql
CREATE TEMPORARY TABLE passengers_faker
WITH (
  'connector' = 'faker',
  'fields.passenger_key.expression' = '#{number.numberBetween ''0'',''10000000''}',
  'fields.update_time.expression' = '#{date.past ''10'',''5'',''SECONDS''}',
  'fields.first_name.expression' = '#{Name.firstName}',
  'fields.last_name.expression' = '#{Name.lastName}',
  'rows-per-second' = '1000'
) LIKE passengers (EXCLUDING OPTIONS);

INSERT INTO passengers SELECT * FROM passengers_faker;
```

#### Kafka Topic

```shell script
➜  bin ./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic passengers --property print.key=true --property key.separator=" - "
749049 - {"passenger_key":"749049","first_name":"Booker","last_name":"Hackett","update_time":"2020-12-19 14:02:32"}
7065702 - {"passenger_key":"7065702","first_name":"Jeramy","last_name":"Breitenberg","update_time":"2020-12-19 14:02:38"}
3690329 - {"passenger_key":"3690329","first_name":"Quiana","last_name":"Macejkovic","update_time":"2020-12-19 14:02:27"}
1212728 - {"passenger_key":"1212728","first_name":"Lawerence","last_name":"Simonis","update_time":"2020-12-19 14:02:27"}
6993699 - {"passenger_key":"6993699","first_name":"Ardelle","last_name":"Frami","update_time":"2020-12-19 14:02:19"}
```

### ``stations`` Topic

#### Script

```sql
CREATE TEMPORARY TABLE stations_faker
WITH (
  'connector' = 'faker',
  'fields.station_key.expression' = '#{number.numberBetween ''0'',''1000''}',
  'fields.city.expression' = '#{Address.city}',
  'fields.update_time.expression' = '#{date.past ''10'',''5'',''SECONDS''}',
  'rows-per-second' = '100'
) LIKE stations (EXCLUDING OPTIONS);

INSERT INTO stations SELECT * FROM stations_faker;
```

#### Kafka Topic

```shell script
➜  bin ./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic stations --property print.key=true --property key.separator=" - "
80 - {"station_key":"80","update_time":"2020-12-19 13:59:20","city":"Harlandport"}
33 - {"station_key":"33","update_time":"2020-12-19 13:59:12","city":"North Georgine"}
369 - {"station_key":"369","update_time":"2020-12-19 13:59:12","city":"Tillmanhaven"}
580 - {"station_key":"580","update_time":"2020-12-19 13:59:12","city":"West Marianabury"}
616 - {"station_key":"616","update_time":"2020-12-19 13:59:09","city":"West Sandytown"}
```

### ``booking_channels`` Topic

#### Script

```sql
CREATE TEMPORARY TABLE booking_channels_faker
WITH (
  'connector' = 'faker',
  'fields.booking_channel_key.expression' = '#{number.numberBetween ''0'',''7''}',
  'fields.channel.expression' = '#{regexify ''(bahn\.de|station|retailer|app|lidl|hotline|joyn){1}''}',
  'fields.update_time.expression' = '#{date.past ''10'',''5'',''SECONDS''}',
  'rows-per-second' = '100'
) LIKE booking_channels (EXCLUDING OPTIONS);

INSERT INTO booking_channels SELECT * FROM booking_channels_faker;
```

#### Kafka Topic

```shell script
➜  bin ./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic booking_channels --property print.key=true --property key.separator=" - "
1 - {"booking_channel_key":"1","update_time":"2020-12-19 13:57:05","channel":"joyn"}
0 - {"booking_channel_key":"0","update_time":"2020-12-19 13:57:17","channel":"station"}
4 - {"booking_channel_key":"4","update_time":"2020-12-19 13:57:15","channel":"joyn"}
2 - {"booking_channel_key":"2","update_time":"2020-12-19 13:57:02","channel":"app"}
1 - {"booking_channel_key":"1","update_time":"2020-12-19 13:57:06","channel":"retailer"}

```

</details>
