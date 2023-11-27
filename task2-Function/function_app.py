"""
# TUTORIALS FOLLOWED:

## Azure Functions (commandline)
<https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-python?tabs=linux%2Cbash%2Cazure-cli&pivots=python-mode-decorators>

*includes setting additional setting variables*

## Azure Serverless SQL Database (commandline)
<https://learn.microsoft.com/en-us/azure/azure-functions/functions-add-output-binding-azure-sql-vs-code?pivots=programming-language-python&tabs=isolated-process%2Cv2>

*use different remote call DB provider*

## pyodbc with Azure
<https://learn.microsoft.com/en-us/sql/connect/python/pyodbc/step-1-configure-development-environment-for-pyodbc-python-development?view=sql-server-ver16&tabs=linux>

*Don't forget to install drivers*

## Others
- SQL tutorials n such
"""


import azure.functions as func
from azure.functions.decorators.core import DataType
import pyodbc
import os


def getMinMaxAvg(conn: pyodbc.Connection, num_of_sensor, column_name):
    value = [[0, 0, 0]  for i in range(num_of_sensor)]

    for i in range(num_of_sensor):
        value[i][0] = conn.execute(f"SELECT MIN({column_name}) from [dbo].[SensorData] WHERE sensor_id={i}").fetchval()
        value[i][1] = conn.execute(f"SELECT MAX({column_name}) from [dbo].[SensorData] WHERE sensor_id={i}").fetchval()
        value[i][2] = conn.execute(f"SELECT AVG({column_name}) from [dbo].[SensorData] WHERE sensor_id={i}").fetchval()

    return value


app = func.FunctionApp()


@app.function_name(name="SensorStatistics")
@app.route(route="minMaxAvgData")
@app.generic_output_binding(arg_name="db", type="sql",
                            CommandText="dbo.SensorData",
                            ConnectionStringSetting="SqlConnectionString",
                            data_type=DataType.STRING)
def test_function(req: func.HttpRequest, db: func.Out[func.SqlRow]) -> func.HttpResponse:

    connection_string = os.environ["SqlConnectionString"]
    conn = pyodbc.connect(connection_string, autocommit=True)

    num_of_sensors = conn.execute("SELECT COUNT(DISTINCT sensor_id) FROM [dbo].[SensorData]").fetchval()

    temp = getMinMaxAvg(conn, num_of_sensors, "temperature")
    wind = getMinMaxAvg(conn, num_of_sensors, "wind_speed")
    hum = getMinMaxAvg(conn, num_of_sensors, "relative_humidity")
    co2 = getMinMaxAvg(conn, num_of_sensors, "co2")

    conn.close()

    return func.HttpResponse(f"Hi me,\n\nSelected min, max, avg\n\n{temp}\n\n{wind}\n\n{hum}\n\n{co2}")
