# Apache Flink SQL Cookbook

 The [Apache Flink SQL](https://docs.ververica.com/user_guide/sql_development/index.html) Cookbook is a curated collection of examples, patterns, and use cases of Apache Flink SQL. 
 Many of the recipes are completely self-contained and can be run in [Ververica Platform](https://docs.ververica.com/index.html) as is.

The cookbook is a living document. :seedling: 

## Table of Contents

### Foundations

1. [Creating Tables](foundations/01_create_table/01_create_table.md)
2. [Inserting Into Tables](foundations/02_insert_into/02_insert_into.md)
3. [Working with Temporary Tables](foundations/03_temporary_table/03_temporary_table.md)
4. [Filtering Data](foundations/04_where/04_where.md)
5. [Aggregating Data](foundations/05_group_by/05_group_by.md)
6. [Sorting Tables](foundations/06_order_by/06_order_by.md)
7. [Encapsulating Logic with (Temporary) Views](foundations/07_views/07_views.md)
8. [Writing Results into Multiple Tables](foundations/08_statement_sets/08_statement_sets.md)
9. [Convert timestamps with timezones](foundations/09_convert_timezones/09_convert_timezones.md)

### Aggregations and Analytics
1. [Aggregating Time Series Data](aggregations-and-analytics/01_group_by_window/01_group_by_window_tvf.md)
2. [Watermarks](aggregations-and-analytics/02_watermarks/02_watermarks.md)
3. [Analyzing Sessions in Time Series Data](aggregations-and-analytics/03_group_by_session_window/03_group_by_session_window.md)
4. [Rolling Aggregations on Time Series Data](aggregations-and-analytics/04_over/04_over.md)
5. [Continuous Top-N](aggregations-and-analytics/05_top_n/05_top_n.md)
6. [Deduplication](aggregations-and-analytics/06_dedup/06_dedup.md)
7. [Chained (Event) Time Windows](aggregations-and-analytics/07_chained_windows/07_chained_windows.md)
8. [Detecting Patterns with MATCH_RECOGNIZE](aggregations-and-analytics/08_match_recognize/08_match_recognize.md)
9. [Maintaining Materialized Views with Change Data Capture (CDC) and Debezium](aggregations-and-analytics/09_cdc_materialized_view/09_cdc_materialized_view.md)
10. [Hopping Time Windows](aggregations-and-analytics/10_hopping_time_windows/10_hopping_time_windows.md)
11. [Window Top-N](aggregations-and-analytics/11_window_top_n/11_window_top_n.md)
12. [Retrieve previous row value without self-join](aggregations-and-analytics/12_lag/12_lag.md)

### Other Built-in Functions & Operators
1. [Working with Dates and Timestamps](other-builtin-functions/01_date_time/01_date_time.md)
2. [Building the Union of Multiple Streams](other-builtin-functions/02_union-all/02_union-all.md)
3. [Filtering out Late Data](other-builtin-functions/03_current_watermark/03_current_watermark.md)
4. [Overriding table options](other-builtin-functions/04_override_table_options/04_override_table_options.md)
5. [Expanding arrays into new rows](other-builtin-functions/05_expanding_arrays/05_expanding_arrays.md)
6. [Split strings into maps](other-builtin-functions/06_split_strings_into_maps/06_split_strings_into_maps.md)

### User-Defined Functions (UDFs)
1. [Extending SQL with Python UDFs](udfs/01_python_udfs/01_python_udfs.md)

### Joins

1. [Regular Joins](joins/01_regular_joins/01_regular_joins.md)
2. [Interval Joins](joins/02_interval_joins/02_interval_joins.md)
3. [Temporal Table Join between a non-compacted and compacted Kafka Topic](joins/03_kafka_join/03_kafka_join.md)
4. [Lookup Joins](joins/04_lookup_joins/04_lookup_joins.md)
5. [Star Schema Denormalization (N-Way Join)](joins/05_star_schema/05_star_schema.md)
6. [Lateral Table Join](joins/06_lateral_join/06_lateral_join.md)

### Former Recipes
1. [Aggregating Time Series Data (Before Flink 1.13)](aggregations-and-analytics/01_group_by_window/01_group_by_window.md)

## About Apache Flink

Apache Flink is an open source stream processing framework with powerful stream- and batch-processing capabilities.

Learn more about Flink at https://flink.apache.org/.

## License 

Copyright © 2020-2022 Ververica GmbH

Distributed under Apache License, Version 2.0.
