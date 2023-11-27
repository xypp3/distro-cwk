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
import random
import time
import os

minTemp = 8.0
maxTemp = 15.0
minWind = 15.0
maxWind = 25.0
minHum = 40.0
maxHum = 70.0
minCO2 = 500.0
maxCO2 = 1500.0


# const ID
def init_sensor(ID):
    return [
            ID,
            random.uniform(minTemp, maxTemp),
            random.uniform(minWind, maxWind),
            random.uniform(minHum, maxHum),
            random.uniform(minCO2, maxCO2),
            ]


# const num
def init_sensor_array(num):
    return [init_sensor(x) for x in range(num)]


# mut sensor
def generate_data(sensor):
    sensor[1] = max(minTemp, min(sensor[1] + random.randint(-1, 1) * 0.35, maxTemp))
    sensor[2] = max(minWind, min(sensor[2] + random.randint(-1, 1) * 0.5, maxWind))
    sensor[3] = max(minHum, min(sensor[3] + random.randint(-3, 3) * 0.5, maxHum))
    sensor[4] = max(minCO2, min(sensor[4] + random.randint(-50, 50), maxCO2))


# const list, mut sensor element
def generate_data_sensor_array(sensor_arr):
    for s in sensor_arr:
        generate_data(s)


app = func.FunctionApp()


@app.function_name(name="SensorGeneration")
@app.route(route="getData")
@app.generic_output_binding(arg_name="db", type="sql",
                            CommandText="dbo.SensorData",
                            ConnectionStringSetting="SqlConnectionString",
                            data_type=DataType.STRING)
def test_function(req: func.HttpRequest, db: func.Out[func.SqlRow]) -> func.HttpResponse:

    sensors_num = req.params.get('num')
    if sensors_num:
        sensors_num = int(sensors_num)
    else:
        sensors_num = 20

    s_arr = init_sensor_array(sensors_num)
    str = s_arr.__str__() + "\n\n\n"
    connection_string = os.environ["SqlConnectionString"]

    # connect to db
    conn = pyodbc.connect(connection_string, autocommit=True)

    # insert data to cursor
    times = 5
    for i in range(times):
        for s in s_arr:
            SQL_INSERT = "INSERT INTO [dbo].[SensorData] (sensor_id, temperature, wind_speed, relative_humidity, co2) VALUES (?, ?, ?, ?, ?);"
            conn.execute(SQL_INSERT, s)
        time.sleep(5)

    conn.close()

    # db.set(func.SqlRowList({"sensor_id": s[0],
    #                     "temperature": s[1],
    #                     "wind_speed": s[2],
    #                     "relative_humidity": s[3],
    #                     "co2": s[4]}))

    return func.HttpResponse(f"Hi me,\n\n{str}")
