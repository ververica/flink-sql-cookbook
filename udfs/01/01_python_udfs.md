# 01 Extending SQL with Python UDFs

:bulb: This example will show how to extend Flink SQL with custom functions written in Python.

Flink SQL provides a wide range of [built-in functions](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/functions/systemFunctions.html) that cover most SQL day-to-day work. Sometimes, you need more flexibility to express custom business logic or transformations that aren't easily translatable to SQL: this can be achieved with [User-Defined Functions](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/functions/udfs.html) (UDFs).

In this example, you'll focus on [Python UDFs](https://ci.apache.org/projects/flink/flink-docs-stable/dev/python/table-api-users-guide/udfs/python_udfs.html) and use them to deal with spotty temperature readings that are continuously generated. How would you interpolate the values for missed readings (i.e. `NULL`) to increase the accuracy of your results? One way to solve this is to write a Python function that uses [`pandas`](https://pandas.pydata.org/) to handle the interpolation.

## Scripts

#### Python UDF

The first step is to create a Python file with the UDF implementation (`python_udf.py`), using Flink's [Python Table API](https://ci.apache.org/projects/flink/flink-docs-stable/dev/python/table-api-users-guide/intro_to_table_api.html). If this is new to you, there are examples on how to write [general](https://ci.apache.org/projects/flink/flink-docs-stable/dev/python/table-api-users-guide/udfs/python_udfs.html) and [vectorized](https://ci.apache.org/projects/flink/flink-docs-stable/dev/python/table-api-users-guide/udfs/vectorized_python_udfs.html) Python UDFs in the Flink documentation.

```python
from pyflink.table import DataTypes
from pyflink.table.udf import udf

import pandas as pd

@udf(input_types=[DataTypes.STRING(), DataTypes.FLOAT()],
     result_type=DataTypes.FLOAT(), func_type='pandas')
def interpolate(id, temperature):
    # takes id: pandas.Series and temperature: pandas.Series as input
    df = pd.DataFrame({'id': id, 'temperature': temperature})

    # use interpolate() to interpolate the missing temperature
    interpolated_df = df.groupby('id').apply(
        lambda group: group.interpolate(limit_direction='both'))

    # output temperature: pandas.Series
    return interpolated_df['temperature']
```

For detailed instructions on how to then make the Python file available as a UDF in the SQL Client, please refer to [this documentation page](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/sqlClient.html#user-defined-functions).

#### SQL

The source table (`temperature_measurements`) is backed by the [`faker` connector](https://github.com/knaufk/flink-faker), which continuously generates rows in memory based on Java Faker expressions. 

```sql
--Register the Python UDF using the fully qualified 
--name of the function ([module name].[object name])
CREATE FUNCTION interpolate AS 'python_udf.interpolate' 
LANGUAGE PYTHON;


CREATE TABLE temperature_measurements (
  city STRING,
  temperature FLOAT,
  --Workaround to force NULLs
  tmp AS NULLIF(temperature,35.0),
  measurement_time AS PROCTIME()
)
WITH (
  'connector' = 'faker',
  'fields.temperature.expression' = '#{number.numberBetween ''0'',''42''}',
  'fields.city.expression' = '#{regexify ''(Chicago|Munich|Berlin|Portland|Seattle|New York){1}''}'
);


--Use interpolate() to fill in missing temperature values
SELECT city,
       tmp,
       interpolate(city,tmp) tmp_interpolated,
       measurement_time
FROM temperature_measurements
WHERE city = 'Berlin';
```

## Example Output

![01_python_udfs](https://user-images.githubusercontent.com/23521087/106631710-4d789e80-657d-11eb-86b9-e49c823ec8bb.gif)