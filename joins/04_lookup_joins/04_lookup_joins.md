# 04 Lookup Joins

> :bulb: This example will show how you can enrich a stream with an external table of reference data (i.e. a _lookup_ table).

## Data Enrichment

Not all data changes frequently, even when working in real-time: in some cases, you might need to enrich streaming data with static — or _reference_ — data that is stored externally.
For example, `user` metadata may be stored in a relational database that Flink needs to join against directly.
Flink SQL allows you to look up reference data and join it with a stream using a _lookup join_. The join requires one table to have a [processing time attribute](https://docs.ververica.com/user_guide/sql_development/table_view.html#processing-time-attributes) and the other table to be backed by a [lookup source connector](https://docs.ververica.com/user_guide/sql_development/connectors.html#id1), like the JDBC connector.

## Using Lookup Joins

In this example, you will look up reference user data stored in MySQL to flag subscription events for users that are minors (`age < 18`). The `FOR SYSTEM_TIME AS OF` clause uses the processing time attribute to ensure that each row of the `subscriptions` table is joined with the `users` rows that match the join predicate at the point in time when the `subscriptions` row is processed by the join operator. The lookup join also requires an equality join predicate based on the `PRIMARY KEY` of the lookup table (`usub.user_id = u.user_id`). Here, the source does not have to read the entire table and can lazily fetch individual values from the external table when necessary.

## Script

The source table (`subscriptions`) is backed by the [`faker` connector](https://flink-packages.org/packages/flink-faker), which continuously generates rows in memory based on Java Faker expressions. The `users` table is backed by an existing MySQL reference table using the [JDBC connector](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/connectors/jdbc.html).

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
  'fields.end_date.expression' = '#{date.future ''365'',''DAYS''}',
  'fields.payment_expiration.expression' = '#{date.future ''365'',''DAYS''}'
);

CREATE TABLE users (
 user_id INT PRIMARY KEY,
 user_name VARCHAR(255) NOT NULL, 
 age INT NOT NULL
)
WITH (
  'connector' = 'jdbc', 
  'url' = 'jdbc:mysql://localhost:3306/mysql-database', 
  'table-name' = 'users', 
  'username' = 'mysql-user', 
  'password' = 'mysql-password'
);

SELECT 
  id AS subscription_id,
  type AS subscription_type,
  age AS user_age,
  CASE 
    WHEN age < 18 THEN 1
    ELSE 0
  END AS is_minor
FROM subscriptions usub
JOIN users FOR SYSTEM_TIME AS OF usub.proc_time AS u
  ON usub.user_id = u.user_id;
```

## Example Output

![18_lookup_joins](https://user-images.githubusercontent.com/23521087/102645588-fcdeea80-4162-11eb-8581-55a06ea82518.png)
