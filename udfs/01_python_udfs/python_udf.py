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
