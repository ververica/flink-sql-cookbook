# Apache Flink SQL Cookbook

 The [Apache Flink SQL](https://docs.ververica.com/user_guide/sql_development/index.html) Cookbook is a curated collection of examples, patterns, and use cases of Apache Flink SQL. 
 Many of the recipes are completely self-contained and can be run in [Ververica Platform](https://docs.ververica.com/index.html) as is.

The cookbook is a living document. :seedling: 

## Table of Contents

### Foundations

1. [Creating Tables](foundations/01/01_create_table.md)
2. [Inserting Into Tables](foundations/02/02_insert_into.md)
3. [Working with Temporary Tables](foundations/03/03_temporary_table.md)
4. [Filtering Data](foundations/04/04_where.md)
5. [Aggregating Data](foundations/05/05_group_by.md)
6. [Sorting Tables](foundations/06/06_order_by.md)
7. [Encapsulating Logic with (Temporary) Views](foundations/07/07_views.md)
8. [Writing Results into Multiple Tables](foundations/08/08_statement_sets.md)

### Aggregations and Analytics
1. [Aggregating Time Series Data](aggregations-and-analytics/01/01_group_by_window.md)
2. [Watermarks](aggregations-and-analytics/02/02_watermarks.md)
3. [Analyzing Sessions in Time Series Data](aggregations-and-analytics/03/03_group_by_session_window.md)
4. [Rolling Aggregations on Time Series Data](aggregations-and-analytics/04/04_over.md)
5. [Continuous Top-N](aggregations-and-analytics/05/05_top_n.md)
6. [Deduplication](aggregations-and-analytics/06/06_dedup.md)
7. [Chained (Event) Time Windows](aggregations-and-analytics/07/07_chained_windows.md)
8. [Detecting Patterns with MATCH_RECOGNIZE](aggregations-and-analytics/08/08_match_recognize.md)
9. [Maintaining Materialized Views with Change Data Capture (CDC) and Debezium](aggregations-and-analytics/09/09_cdc_materialized_view.md)

### Other Built-in Functions & Operators
1. [Working with Dates and Timestamps](other-builtin-functions/01/01_date_time.md)
2. [Building the Union of Multiple Streams](other-builtin-functions/02/02_union-all.md)

### User-Defined Functions (UDFs)
1. [Extending SQL with Python UDFs](udfs/01/01_python_udfs.md)

### Joins

1. [Regular Joins](joins/01/01_regular_joins.md)
2. [Interval Joins](joins/02/02_interval_joins.md)
3. [Temporal Table Join between a non-compacted and compacted Kafka Topic](joins/03/03_kafka_join.md)
4. [Lookup Joins](joins/04/04_lookup_joins.md)
5. [Star Schema Denormalization (N-Way Join)](joins/05/05_star_schema.md)
6. [Lateral Table Join](joins/06/06_lateral_join.md)

## About Apache Flink

Apache Flink is an open source stream processing framework with powerful stream- and batch-processing capabilities.

Learn more about Flink at https://flink.apache.org/.

## License 

Copyright © 2020-2021 Ververica GmbH

Distributed under Apache License, Version 2.0.
