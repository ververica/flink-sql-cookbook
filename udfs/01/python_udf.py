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