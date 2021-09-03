# 02 Watermarks

![Twitter Badge](https://img.shields.io/badge/Flink%20Version-1.10%2B-lightgrey)

> :bulb: This example will show how to use `WATERMARK`s to work with timestamps in records. 

The source table (`doctor_sightings`) is backed by the [`faker` connector](https://flink-packages.org/packages/flink-faker), which continuously generates rows in memory based on Java Faker expressions.

The [previous recipe](../01_group_by_window/01_group_by_window.md) showed how a `TUMBLE` group window makes it simple to aggregate time-series data.	 

[The Doctor](https://tardis.fandom.com/wiki/The_Doctor) is a renegade time lord who travels through space and time in a [TARDIS](https://tardis.fandom.com/wiki/The_Doctor%27s_TARDIS).
As different versions of the Doctor travel through time, various people log their sightings.
We want to track how many times each version of the Doctor is seen each minute. 	 
Unlike the previous recipe, these records have an embedded timestamp we need to use to perform our calculation. 	 

More often than not, most data will come with embedded timestamps that we want to use for our time series calculations.	We call this timestamp an [event-time attribute](https://ci.apache.org/projects/flink/flink-docs-stable/docs/learn-flink/streaming_analytics/#event-time-and-watermarks).	 
  
Event time represents when something actually happened in the real world.
And it is unique because it is quasi-monotonically increasing; we generally see things that happened earlier before seeing things that happen later. Of course, data will never be perfectly ordered (systems go down, networks are laggy, doctor sighting take time to postmark and mail), and there will be some out-of-orderness in our data. 	 

Flink can account for all these variabilities using a [WATERMARK](https://docs.ververica.com/user_guide/sql_development/table_view.html#event-time) attribute in the tables DDL. The watermark signifies a column as the table's event time attribute and tells Flink how out of order we expect our data. 	 
 
In the Doctor's case, we expect all records to arrive within 15 seconds when the sighting occurs.

## Script

```sql
CREATE TABLE doctor_sightings (
  doctor        STRING,
  sighting_time TIMESTAMP(3),
  WATERMARK FOR sighting_time AS sighting_time - INTERVAL '15' SECONDS
)
WITH (
  'connector' = 'faker', 
  'fields.doctor.expression' = '#{dr_who.the_doctors}',
  'fields.sighting_time.expression' = '#{date.past ''15'',''SECONDS''}'
);

SELECT 
    doctor,
    TUMBLE_ROWTIME(sighting_time, INTERVAL '1' MINUTE) AS sighting_time,
    COUNT(*) AS sightings
FROM doctor_sightings
GROUP BY 
    TUMBLE(sighting_time, INTERVAL '1' MINUTE),
    doctor;
```

## Example Output

![02_watermarks](https://user-images.githubusercontent.com/23521087/105503592-12e24c80-5cc7-11eb-9155-243cc9c314f0.png)
