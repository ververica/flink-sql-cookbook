# 06 Deduplication

> :bulb: This example will show how you can identify and filter out duplicates in a stream of events.

There are different ways that duplicate events can end up in your data sources, from human error to application bugs. Regardless of the origin, unclean data can have a real impact in the quality (and correctness) of your results. Suppose that your order system occasionally generates duplicate events with the same `order_id`, and that you're only interested in keeping the most recent event for downstream processing.

As a first step, you can use a combination of the `COUNT` function and the `HAVING` clause to check if and which orders have more than one event; and then filter out these events using `ROW_NUMBER()`. In practice, deduplication is a special case of [Top-N aggregation](../05_top_n/05_top_n.md), where N is 1 (`rownum = 1`) and the ordering column is either the processing or event time of events.

## Script

The source table `orders` is backed by the built-in [`datagen` connector](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/connectors/datagen.html), which continuously generates rows in memory.

```sql
CREATE TABLE orders (
  id INT,
  order_time AS CURRENT_TIMESTAMP,
  WATERMARK FOR order_time AS order_time - INTERVAL '5' SECONDS
)
WITH (
  'connector' = 'datagen',
  'rows-per-second'='10',
  'fields.id.kind'='random',
  'fields.id.min'='1',
  'fields.id.max'='100'
);

--Check for duplicates in the `orders` table
SELECT id AS order_id,
       COUNT(*) AS order_cnt
FROM orders o
GROUP BY id
HAVING COUNT(*) > 1;

--Use deduplication to keep only the latest record for each `order_id`
SELECT
  order_id,
  order_time
FROM (
  SELECT id AS order_id,
         order_time,
         ROW_NUMBER() OVER (PARTITION BY id ORDER BY order_time) AS rownum
  FROM orders
     )
WHERE rownum = 1;
```

## Example Output

![20_dedup](https://user-images.githubusercontent.com/23521087/102718503-b87d5700-42e8-11eb-8b45-4f9908e8e14e.gif)
