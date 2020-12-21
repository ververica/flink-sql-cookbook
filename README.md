# Apache Flink SQL Cookbook

 The [Apache Flink SQL](https://docs.ververica.com/user_guide/sql_development/index.html) Cookbook is a curated collection of examples, patterns, and use cases of Apache Flink SQL. 
 Many of the recipes are completely self-contained and can be run in [Ververica Platform](https://docs.ververica.com/index.html) as is.

The cookbook is a living document. 
The first twenty-four examples are being added as an advent calendar leading up to Christmas 2020.  

## Table of Contents

### Foundations

1. [Creating Tables](recipes/01/01_create_table.md)
2. [Inserting Into Tables](recipes/04/04_insert_into.md)
3. [Working with Temporary Tables](recipes/05/05_temporary_table.md)
4. [Filtering Data](recipes/02/02_where.md)
5. [Aggregating Data](recipes/03/03_group_by.md)
6. [Sorting Tables](recipes/08/08_order_by.md)
7. [Encapsulating Logic with (Temporary) Views](recipes/13/13_views.md)
8. [Writing Results into Multiple Tables](recipes/17/17_statement_sets.md)

### Aggregations and Analytics
1. [Aggregating Time Series Data](recipes/06/06_group_by_window.md)
2. [Watermarks](recipes/07/07_watermarks.md)
3. [Analyzing Sessions in Time Series Data](recipes/09/09_group_by_session_window.md)
4. [Rolling Aggregations on Time Series Data](recipes/10/10_over.md)
5. [Continuous Top-N](recipes/11/11_top_n.md)
6. [Deduplication](recipes/20/20_dedup.md)

### Other Built-in Functions
1. [Working with Dates and Timestamps](recipes/12/12_date_time.md)

### Joins

1. [Regular Joins](recipes/14/14_regular_joins.md)
2. [Interval Joins](recipes/15/15_interval_joins.md)
3. [Temporal Table Join between a non-compacted and compacted Kafka Topic](recipes/16/16_kafka_join.md)
4. [Lookup Joins](recipes/18/18_lookup_joins.md)
5. [Star Schema Denormalization (N-Way Join)](recipes/19/19_start_schema.md)
6. [Lateral Table Join](recipes/21/21_lateral_join.md)

## About Apache Flink

Apache Flink is an open source stream processing framework with powerful stream- and batch-processing capabilities.

Learn more about Flink at https://flink.apache.org/.

## License 

Copyright © 2020 Ververica GmbH

Distributed under Apache License, Version 2.0.
