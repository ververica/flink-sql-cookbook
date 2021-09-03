# 06 Lateral Table Join

> :bulb: This example will show how you can correlate events using a `LATERAL` join.

A recent addition to the SQL standard is the `LATERAL` join, which allows you to combine 
the power of a correlated subquery with the expressiveness of a join. 

Given a table with people's addresses, you need to find the two most populous cities
for each state and continuously update those rankings as people move. The input table
of `People` contains a uid for each person and their address and when they moved there.

The first step is to calculate each city's population using a [continuous aggregation](../../foundations/05_group_by/05_group_by.md).
While this is simple enough, the real power of Flink SQL comes when people move. By using
[deduplication](../../aggregations-and-analytics/06_dedup/06_dedup.md) Flink will automatically issue a retraction for a persons old city when 
they move. So if John moves from New York to Los Angelos, the population for New York will 
automatically go down by 1. This gives us the power change-data-capture without having
to invest in the actual infrastructure of setting it up!

With this dynamic population table at hand, you are ready to solve the original problem using a `LATERAL` table join.
Unlike a normal join, lateral joins allow the subquery to correlate with columns from other arguments in the `FROM` clause. And unlike a regular subquery, as a join, the lateral can return multiple rows.
You can now have a sub-query correlated with every individual state, and for every state it ranks by population and returns the top 2 cities.

## Script

```sql
CREATE TABLE People (
    id           INT,
    city         STRING,
    state        STRING,
    arrival_time TIMESTAMP(3),
    WATERMARK FOR arrival_time AS arrival_time - INTERVAL '1' MINUTE 
) WITH (
    'connector' = 'faker',
    'fields.id.expression'    = '#{number.numberBetween ''1'',''100''}',
    'fields.city.expression'  = '#{regexify ''(Newmouth|Newburgh|Portport|Southfort|Springfield){1}''}',
    'fields.state.expression' = '#{regexify ''(New York|Illinois|California|Washington){1}''}',
    'fields.arrival_time.expression' = '#{date.past ''15'',''SECONDS''}',
    'rows-per-second'          = '10'
); 

CREATE TEMPORARY VIEW CurrentPopulation AS
SELECT 
    city,
    state,
    COUNT(*) as population
FROM (
    SELECT
        city,
        state,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY arrival_time DESC) AS rownum
    FROM People
)
WHERE rownum = 1
GROUP BY city, state;

SELECT
    state,
    city,
    population
FROM 
    (SELECT DISTINCT state FROM CurrentPopulation) States,
    LATERAL (
        SELECT city, population
        FROM CurrentPopulation
        WHERE state = States.state
        ORDER BY population DESC
        LIMIT 2
);
```

## Example Output

![lateral](https://user-images.githubusercontent.com/23521087/105504738-6bfeb000-5cc8-11eb-9517-1242dfa87bb4.gif)
