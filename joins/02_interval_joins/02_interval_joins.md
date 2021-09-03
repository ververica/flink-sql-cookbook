# 02 Interval Joins

> :bulb: This example will show how you can perform joins between tables with events that are related in a temporal context.

## Why Interval Joins?

In a [previous recipe](../01_regular_joins/01_regular_joins.md), you learned about using _regular joins_ in Flink SQL. This kind of join works well for some scenarios, but for others a more efficient type of join is required to keep resource utilization from growing indefinitely.

One of the ways to optimize joining operations in Flink SQL is to use [_interval joins_](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/streaming/joins.html#interval-joins). An interval join is defined by a join predicate that checks if the time attributes of the input events are within certain time constraints (i.e. a time window).

## Using Interval Joins

Suppose you want to join events of two tables that correlate to each other in the [order fulfillment lifecycle](https://en.wikipedia.org/wiki/Order_fulfillment) (`orders` and `shipments`) and that are under a Service-level Aggreement (SLA) of **3 days**. To reduce the amount of input rows Flink has to retain and optimize the join operation, you can define a time constraint in the `WHERE` clause to bound the time on both sides to that specific interval using a `BETWEEN` predicate.

## Script

The source tables (`orders` and `shipments`) are backed by the built-in [`datagen` connector](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/connectors/datagen.html), which continuously generates rows in memory.

```sql
CREATE TABLE orders (
  id INT,
  order_time AS TIMESTAMPADD(DAY, CAST(FLOOR(RAND()*(1-5+1)+5)*(-1) AS INT), CURRENT_TIMESTAMP)
)
WITH (
  'connector' = 'datagen',
  'rows-per-second'='10',
  'fields.id.kind'='sequence',
  'fields.id.start'='1',
  'fields.id.end'='1000'
);


CREATE TABLE shipments (
  id INT,
  order_id INT,
  shipment_time AS TIMESTAMPADD(DAY, CAST(FLOOR(RAND()*(1-5+1)) AS INT), CURRENT_TIMESTAMP)
)
WITH (
  'connector' = 'datagen',
  'rows-per-second'='5',
  'fields.id.kind'='random',
  'fields.id.min'='0',
  'fields.order_id.kind'='sequence',
  'fields.order_id.start'='1',
  'fields.order_id.end'='1000'
);

SELECT
  o.id AS order_id,
  o.order_time,
  s.shipment_time,
  TIMESTAMPDIFF(DAY,o.order_time,s.shipment_time) AS day_diff
FROM orders o
JOIN shipments s ON o.id = s.order_id
WHERE 
    o.order_time BETWEEN s.shipment_time - INTERVAL '3' DAY AND s.shipment_time;
```

## Example Output

![15_interval_joins](https://user-images.githubusercontent.com/23521087/102237138-9ce30c80-3ef4-11eb-969f-8f157b249ebb.png)
