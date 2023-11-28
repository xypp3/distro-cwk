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
def task_1(req: func.HttpRequest, db: func.Out[func.SqlRow]) -> func.HttpResponse:

    sensors_num = req.params.get('num')
    if sensors_num:
        sensors_num = int(sensors_num)
    else:
        sensors_num = 20

    s_arr = init_sensor_array(sensors_num)

    connection_string = os.environ["SqlConnectionString"]
    conn = pyodbc.connect(connection_string, autocommit=True)

    for s in s_arr:
        SQL_INSERT = "INSERT INTO [dbo].[SensorData] (sensor_id, temperature, wind_speed, relative_humidity, co2) VALUES (?, ?, ?, ?, ?);"
        conn.execute(SQL_INSERT, s)

    conn.close()

    return func.HttpResponse(f"Hi me,\n\nInserted {sensors_num} sensor data")


def getMinMaxAvg(conn: pyodbc.Connection, num_of_sensor, column_name):
    value = [[0, 0, 0]  for i in range(num_of_sensor)]

    for i in range(num_of_sensor):
        value[i][0] = conn.execute(f"SELECT MIN({column_name}) from [dbo].[SensorData] WHERE sensor_id={i}").fetchval()
        value[i][1] = conn.execute(f"SELECT MAX({column_name}) from [dbo].[SensorData] WHERE sensor_id={i}").fetchval()
        value[i][2] = conn.execute(f"SELECT AVG({column_name}) from [dbo].[SensorData] WHERE sensor_id={i}").fetchval()

    return value


def createHtmlTable(data, title, len):
    str = f"<h2>{title}</h2>"

    str += "<table>"
    str += "<tr><th>Sensor ID</th><th>Min</th><th>Max</th><th>Avg</th></tr>"
    for i in range(len):
        str += "<tr>"
        str += f"<td>{i}</td>"
        str += f"<td>{data[i][0]}</td>"
        str += f"<td>{data[i][1]}</td>"
        str += f"<td>{data[i][2]}</td>"
        str += "</tr>"
    str += "</table>"

    return str


@app.function_name(name="SensorStatistics")
@app.route(route="minMaxAvgData")
def task_2(req: func.HttpRequest) -> func.HttpResponse:

    connection_string = os.environ["SqlConnectionString"]
    conn = pyodbc.connect(connection_string, autocommit=True)

    num_of_sensors = conn.execute("SELECT COUNT(DISTINCT sensor_id) FROM [dbo].[SensorData]").fetchval()

    temp = getMinMaxAvg(conn, num_of_sensors, "temperature")
    wind = getMinMaxAvg(conn, num_of_sensors, "wind_speed")
    hum = getMinMaxAvg(conn, num_of_sensors, "relative_humidity")
    co2 = getMinMaxAvg(conn, num_of_sensors, "co2")

    html = "<html><body>"
    html += createHtmlTable(temp, "Temperature Data", num_of_sensors)
    html += createHtmlTable(wind, "Wind Speed Data", num_of_sensors)
    html += createHtmlTable(hum, "Relative Humidity Data", num_of_sensors)
    html += createHtmlTable(co2, "CO2 Data", num_of_sensors)
    html += "</body></html>"

    conn.close()

    return func.HttpResponse(html, mimetype="text/html")
