# 02 Building the Union of Multiple Streams

> :bulb: This example will show how you can use the set operation `UNION ALL` to combine several streams of data.

See [our documentation](https://ci.apache.org/projects/flink/flink-docs-stable/docs/dev/table/sql/queries/set-ops/)
for a full list of fantastic set operations Apache Flink supports.


## The Sources

The examples assumes you are building an application that is tracking visits :fox_face: on foreign planets :chestnut:. 
There are three sources of visits. The universe of Rick and Morty, the very real world of NASA and such, 
and the not so real world of Hitchhikers Guide To The Galaxy.

All three tables are `unbounded` and backed by the [`faker` connector](https://flink-packages.org/packages/flink-faker).

All sources of tracked visits have the `location` and `visit_time` in common. Some have `visitors`, some have
`spacecrafts` and one has both.

```sql
CREATE TEMPORARY TABLE rickandmorty_visits ( 
    visitor STRING,
    location STRING, 
    visit_time TIMESTAMP(3)
) WITH (
  'connector' = 'faker', 
  'fields.visitor.expression' = '#{RickAndMorty.character}',
  'fields.location.expression' =  '#{RickAndMorty.location}',
  'fields.visit_time.expression' =  '#{date.past ''15'',''5'',''SECONDS''}'
);

CREATE TEMPORARY TABLE spaceagency_visits ( 
    spacecraft STRING,
    location STRING, 
    visit_time TIMESTAMP(3)
) WITH (
  'connector' = 'faker', 
  'fields.spacecraft.expression' = '#{Space.nasaSpaceCraft}',
  'fields.location.expression' =  '#{Space.star}',
  'fields.visit_time.expression' =  '#{date.past ''15'',''5'',''SECONDS''}'
);

CREATE TEMPORARY TABLE hitchhiker_visits ( 
    visitor STRING,
    starship STRING,
    location STRING, 
    visit_time TIMESTAMP(3)
) WITH (
  'connector' = 'faker', 
  'fields.visitor.expression' = '#{HitchhikersGuideToTheGalaxy.character}',
  'fields.starship.expression' = '#{HitchhikersGuideToTheGalaxy.starship}',
  'fields.location.expression' =  '#{HitchhikersGuideToTheGalaxy.location}',
  'fields.visit_time.expression' =  '#{date.past ''15'',''5'',''SECONDS''}'
);

```

## The Query

We are using `UNION ALL` because it doesn't try to combine equivalent rows like 
`UNION` would do. That is also the reason why `UNION` can only be used with `bounded` streams.


```sql
SELECT visitor, '' AS spacecraft, location, visit_time FROM rickandmorty_visits
UNION ALL
SELECT '' AS visitor, spacecraft, location, visit_time FROM spaceagency_visits
UNION ALL
SELECT visitor, starship AS spacecraft, location, visit_time FROM hitchhiker_visits;
```

:alien: As we are using `CREATE TEMPORARY TABLE`, you need to run both the `CREATE TABLE` and the `SELECT` statements together.

## The Beauty in VVP

![screeny](https://user-images.githubusercontent.com/68620/108173907-081cab00-70ff-11eb-823a-8a245b390485.png)


The result is a combined stream of people visiting a location in one of those fantastic universes.
We are sure you'll understand why this is one of our favorite queries.

:bird: [Let us know](https://twitter.com/ververicadata) about your favorite streaming SQL Query.
