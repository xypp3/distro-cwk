import azure.functions as func
import datetime
import json
import logging
import random

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


@app.function_name(name="HttpExample")
@app.route(route="hello")
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    s_arr = init_sensor_array(10)
    str = s_arr.__str__() + "\n\n\n"
    for i in range(5):
        generate_data_sensor_array(s_arr)
        str += s_arr.__str__() + "\n\n\n"
    return func.HttpResponse(f"Hi me,\n\n{str}")
