# 08 Detecting patterns with MATCH_RECOGNIZE

> :bulb: This example will show how you can use Flink SQL to detect patterns in a stream of events with `MATCH_RECOGNIZE`.

A common (but historically complex) task in SQL day-to-day work is to identify meaningful sequences of events in a data set — also known as Complex Event Processing (CEP). This becomes even more relevant when dealing with streaming data, as you want to react quickly to known patterns or changing trends to deliver up-to-date business insights. In Flink SQL, you can easily perform this kind of tasks using the standard SQL clause [`MATCH_RECOGNIZE`](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/streaming/match_recognize.html).

## Breaking down MATCH_RECOGNIZE

In this example, you want to find users that downgraded their service subscription from one of the premium tiers (`type IN ('premium','platinum')`) to the basic tier. 

#### Input

The input argument of `MATCH_RECOGNIZE` will be a row pattern table based on `subscriptions`. As a first step, logical partitioning and ordering must be applied to the input row pattern table to ensure that event processing is correct and deterministic:

```sql
PARTITION BY user_id 
ORDER BY proc_time
```

#### Output

Row pattern columns are then defined in the `MEASURES` clause, which can be thought of as the `SELECT` of `MATCH_RECOGNIZE`. If you're interested in getting the type of premium subscription associated with the last event before the downgrade, you can fetch it using the [logical offset](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/streaming/match_recognize.html#logical-offsets) operator `LAST`. The downgrade date can be extrapolated from the `start_date` of the first basic subscription event following any existing premium one(s).

```sql
MEASURES
  LAST(PREMIUM.type) AS premium_type,
  AVG(TIMESTAMPDIFF(DAY,PREMIUM.start_date,PREMIUM.end_date)) AS premium_avg_duration,
  BASIC.start_date AS downgrade_date
AFTER MATCH SKIP PAST LAST ROW
```

#### Pattern Definition

Patterns are specified in the `PATTERN` clause using row-pattern variables (i.e. event types) and regular expressions. These variables must also be associated with the matching conditions that events must meet to be included in the pattern, using the `DEFINE` clause. Here, you are interested in matching one or more premium subscription events (`PREMIUM+`) followed by a basic subscription event (`BASIC`):

```sql
PATTERN (PREMIUM+ BASIC)
DEFINE PREMIUM AS PREMIUM.type IN ('premium','platinum'),
BASIC AS BASIC.type = 'basic');
```

## Script

The source table (`subscriptions`) is backed by the [`faker` connector](https://flink-packages.org/packages/flink-faker), which continuously generates rows in memory based on Java Faker expressions.

```sql
CREATE TABLE subscriptions ( 
    id STRING,
    user_id INT,
    type STRING,
    start_date TIMESTAMP(3),
    end_date TIMESTAMP(3),
    payment_expiration TIMESTAMP(3),
    proc_time AS PROCTIME()
) WITH (
  'connector' = 'faker',
  'fields.id.expression' = '#{Internet.uuid}', 
  'fields.user_id.expression' = '#{number.numberBetween ''1'',''50''}',
  'fields.type.expression'= '#{regexify ''(basic|premium|platinum){1}''}',
  'fields.start_date.expression' = '#{date.past ''30'',''DAYS''}',
  'fields.end_date.expression' = '#{date.future ''15'',''DAYS''}',
  'fields.payment_expiration.expression' = '#{date.future ''365'',''DAYS''}'
);

SELECT * 
FROM subscriptions
     MATCH_RECOGNIZE (PARTITION BY user_id 
                      ORDER BY proc_time
                      MEASURES
                        LAST(PREMIUM.type) AS premium_type,
                        AVG(TIMESTAMPDIFF(DAY,PREMIUM.start_date,PREMIUM.end_date)) AS premium_avg_duration,
                        BASIC.start_date AS downgrade_date
                      AFTER MATCH SKIP PAST LAST ROW
                      --Pattern: one or more 'premium' or 'platinum' subscription events (PREMIUM)
                      --followed by a 'basic' subscription event (BASIC) for the same `user_id`
                      PATTERN (PREMIUM+ BASIC)
                      DEFINE PREMIUM AS PREMIUM.type IN ('premium','platinum'),
                             BASIC AS BASIC.type = 'basic');
```

## Example Output

![23_match_recognize](https://user-images.githubusercontent.com/2392216/108039085-ee665f80-703b-11eb-93f9-f8e3b684f315.png)
