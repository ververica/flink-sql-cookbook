# 01 Regular Joins

> :bulb: This example will show how you can use joins to correlate rows across multiple tables.

Flink SQL supports complex and flexible join operations over continuous tables.
There are several different types of joins to account for the wide variety of semantics queries may require.

Regular joins are the most generic and flexible type of join.
These include the standard `INNER` and `[FULL|LEFT|RIGHT] OUTER` joins that are available in most modern databases. 

Suppose we have a [NOC list](https://en.wikipedia.org/wiki/Non-official_cover) of secret agents all over the world.
Your mission if you choose to accept it, is to join this table with another containin the agents real name.

In Flink SQL, this can be achieved using a simple `INNER JOIN`.
Flink will join the tables using an equi-join predicate on the `agent_id` and output a new row everytime there is a match.

However, there is something to be careful of. 
Flink must retain every input row as part of the join to potentially join it with the other table in the future. 
This means the queries resource requirements will grow indefinitely and will eventually fail.
While this type of join is useful in some scenarios, other joins are more powerful in a streaming context and significantly more space-efficient.

In this example, both tables are bounded to remain space efficient.

```sql
CREATE TABLE NOC (
  agent_id STRING,
  codename STRING
)
WITH (
  'connector' = 'faker',
  'fields.agent_id.expression' = '#{regexify ''(1|2|3|4|5){1}''}',
  'fields.codename.expression' = '#{superhero.name}',
  'number-of-rows' = '10'
);

CREATE TABLE RealNames (
  agent_id STRING,
  name     STRING
)
WITH (
  'connector' = 'faker',
  'fields.agent_id.expression' = '#{regexify ''(1|2|3|4|5){1}''}',
  'fields.name.expression' = '#{Name.full_name}',
  'number-of-rows' = '10'
);

SELECT
    name,
    codename
FROM NOC
INNER JOIN RealNames ON NOC.agent_id = RealNames.agent_id;
```

![01_regular_joins](https://user-images.githubusercontent.com/23521087/105504538-280bab00-5cc8-11eb-962d-6f36432e422b.png)
