# 01 Extending SQL with Python UDFs

![Twitter Badge](https://img.shields.io/badge/Flink%20Version-1.11%2B-lightgrey)

> :bulb: This example will show how to extend Flink SQL with custom functions written in Python.

Flink SQL provides a wide range of [built-in functions](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/functions/systemFunctions.html) that cover most SQL day-to-day work. Sometimes, you need more flexibility to express custom business logic or transformations that aren't easily translatable to SQL: this can be achieved with [User-Defined Functions](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/functions/udfs.html) (UDFs).

In this example, you'll focus on [Python UDFs](https://ci.apache.org/projects/flink/flink-docs-stable/dev/python/table-api-users-guide/udfs/python_udfs.html) and implement a custom function (`to_fahr`) to convert temperature readings that are continuously generated for different EU and US cities. The Celsius->Fahrenheit conversion should only happen if the city associated with the reading is in the US.

## Scripts

#### Python UDF

The first step is to create a Python file with the UDF implementation (`python_udf.py`), using Flink's [Python Table API](https://ci.apache.org/projects/flink/flink-docs-stable/dev/python/table-api-users-guide/intro_to_table_api.html). If this is new to you, there are examples on how to write [general](https://ci.apache.org/projects/flink/flink-docs-stable/dev/python/table-api-users-guide/udfs/python_udfs.html) and [vectorized](https://ci.apache.org/projects/flink/flink-docs-stable/dev/python/table-api-users-guide/udfs/vectorized_python_udfs.html) Python UDFs in the Flink documentation.

```python
from pyflink.table import DataTypes
from pyflink.table.udf import udf

us_cities = {"Chicago","Portland","Seattle","New York"}

@udf(input_types=[DataTypes.STRING(), DataTypes.FLOAT()],
     result_type=DataTypes.FLOAT())
def to_fahr(city, temperature):

  if city in us_cities:

    fahr = ((temperature * 9.0 / 5.0) + 32.0)

    return fahr
  else:
    return temperature
```

For detailed instructions on how to then make the Python file available as a UDF in the SQL Client, please refer to [this documentation page](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/sqlClient.html#user-defined-functions).

#### SQL

The source table (`temperature_measurements`) is backed by the [`faker` connector](https://flink-packages.org/packages/flink-faker), which continuously generates rows in memory based on Java Faker expressions. 

```sql
--Register the Python UDF using the fully qualified 
--name of the function ([module name].[object name])
CREATE FUNCTION to_fahr AS 'python_udf.to_fahr' 
LANGUAGE PYTHON;


CREATE TABLE temperature_measurements (
  city STRING,
  temperature FLOAT,
  measurement_time TIMESTAMP(3),
  WATERMARK FOR measurement_time AS measurement_time - INTERVAL '15' SECONDS
)
WITH (
  'connector' = 'faker',
  'fields.temperature.expression' = '#{number.numberBetween ''0'',''42''}',
  'fields.measurement_time.expression' = '#{date.past ''15'',''SECONDS''}',
  'fields.city.expression' = '#{regexify ''(Copenhagen|Berlin|Chicago|Portland|Seattle|New York){1}''}'
);


--Use to_fahr() to convert temperatures in US cities from C to F
SELECT city,
       temperature AS tmp,
       to_fahr(city,temperature) AS tmp_conv,
       measurement_time
FROM temperature_measurements;
```

## Example Output

![01_python_udfs](https://user-images.githubusercontent.com/23521087/106733744-8ca4ff00-6612-11eb-9721-e4a74fb07329.gif)