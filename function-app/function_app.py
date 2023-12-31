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

## sql trigger with python v2
<https://github.com/Azure/azure-functions-sql-extension/blob/main/samples/samples-python-v2/function_app.py>

## Others
- SQL tutorials n such
"""

import azure.functions as func
import pyodbc
import random
import os
import logging
import datetime
from azure.functions.decorators.core import DataType

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
def task_1(req: func.HttpRequest) -> func.HttpResponse:

    sensors_num = req.params.get('num')
    if sensors_num:
        sensors_num = int(sensors_num)
    else:
        sensors_num = 20

    s_arr = init_sensor_array(sensors_num)

    connection_string = os.environ["SqlDriver"] + os.environ["SqlConnectionString"]
    conn = pyodbc.connect(connection_string, autocommit=True)

    for s in s_arr:
        SQL_INSERT = "INSERT INTO [dbo].[SensorData] (sensor_id, temperature, wind_speed, relative_humidity, co2) VALUES (?, ?, ?, ?, ?);"
        conn.execute(SQL_INSERT, s)

    conn.close()

    return func.HttpResponse(f"Hi me,\n\nInserted {sensors_num} sensor data")


def createHtmlTable(data, title, len, data_index):
    str = f"<h2>{title}</h2>"

    str += "<table>"
    str += "<tr><th>Sensor ID</th><th>Min</th><th>Max</th><th>Avg</th></tr>"
    for i in range(len):
        str += "<tr>"
        str += f"<td>{i}</td>"
        str += f"<td>{data[i][0 + 3*data_index]}</td>"
        str += f"<td>{data[i][1 + 3*data_index]}</td>"
        str += f"<td>{data[i][2 + 3*data_index]}</td>"
        str += "</tr>"
    str += "</table>"

    return str


@app.function_name(name="SensorStatistics")
@app.route(route="minMaxAvgData")
def task_2(req: func.HttpRequest) -> func.HttpResponse:

    connection_string = os.environ["SqlDriver"] + os.environ["SqlConnectionString"]
    conn = pyodbc.connect(connection_string, autocommit=True)

    num_of_sensors = conn.execute("SELECT COUNT(DISTINCT sensor_id) FROM [dbo].[SensorData]").fetchval()

    temp = "temperature"
    wind = "wind_speed"
    hum = "relative_humidity"
    co2 = "co2"

    QUERY = f"""
        SELECT
         MIN({temp}), MAX({temp}), AVG({temp}),
         MIN({wind}), MAX({wind}), AVG({wind}),
         MIN({hum}), MAX({hum}), AVG({hum}),
         MIN({co2}), MAX({co2}), AVG({co2})
         FROM [dbo].[SensorData]
         GROUP BY sensor_id;
        """
    data = conn.execute(QUERY).fetchall()

    html = "<html><body>"
    html += createHtmlTable(data, "Temperature Data", num_of_sensors, 0)
    html += createHtmlTable(data, "Wind Speed Data", num_of_sensors, 1)
    html += createHtmlTable(data, "Relative Humidity Data", num_of_sensors, 2)
    html += createHtmlTable(data, "CO2 Data", num_of_sensors, 3)
    html += "</body></html>"

    conn.close()

    return func.HttpResponse(html, mimetype="text/html")


@app.function_name(name="TimerSensorGeneration")
@app.schedule(schedule="*/5 * * * * *",
              arg_name="mytimer",
              run_on_startup=True)
def task_3_gen(mytimer) -> None:
    s_arr = init_sensor_array(20)

    connection_string = os.environ["SqlDriver"] + os.environ["SqlConnectionString"]
    conn = pyodbc.connect(connection_string, autocommit=True)

    for s in s_arr:
        SQL_INSERT = "INSERT INTO [dbo].[SensorData] (sensor_id, temperature, wind_speed, relative_humidity, co2) VALUES (?, ?, ?, ?, ?);"
        conn.execute(SQL_INSERT, s)

    conn.close()

    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    logging.info(f"At {utc_timestamp}")


""" Issues/ Changes for function below

## Connection string must exclude driver
- Split connection string into SqlDriver + SqlConnectionString

## Azure DB
ALTER DATABASE [distro-db]
SET CHANGE_TRACKING = ON
(CHANGE_RETENTION = 2 DAYS, AUTO_CLEANUP = ON);

ALTER TABLE [dbo].[SensorData]
ENABLE CHANGE_TRACKING;

"""


@app.function_name(name="DBTriggerSensorStatistics")
# @app.route(route="sqlTrigger")
@app.generic_trigger(arg_name="data", type="sqlTrigger",
                     TableName="SensorData",
                     ConnectionStringSetting="SqlConnectionString",
                     data_type=DataType.STRING)
def task_3_sql_trigger(data) -> None:
    connection_string = os.environ["SqlDriver"] + os.environ["SqlConnectionString"]
    conn = pyodbc.connect(connection_string, autocommit=True)

    num_of_sensors = conn.execute("SELECT COUNT(DISTINCT sensor_id) FROM [dbo].[SensorData]").fetchval()

    temp = "temperature"
    wind = "wind_speed"
    hum = "relative_humidity"
    co2 = "co2"

    QUERY = f"""
        SELECT
         MIN({temp}), MAX({temp}), AVG({temp}),
         MIN({wind}), MAX({wind}), AVG({wind}),
         MIN({hum}), MAX({hum}), AVG({hum}),
         MIN({co2}), MAX({co2}), AVG({co2})
         FROM [dbo].[SensorData]
         GROUP BY sensor_id;
        """
    table = conn.execute(QUERY).fetchall()

    conn.execute("TRUNCATE TABLE [dbo].[liveStats]")
    for i in range(num_of_sensors):
        conn.execute("INSERT INTO [dbo].[liveStats] (min_temperature, max_temperature, avg_temperature, min_wind_speed, max_wind_speed, avg_wind_speed, min_relative_humidity, max_relative_humidity, avg_relative_humidity, min_co2, max_co2, avg_co2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                     table[i],
                     )

    conn.close()
