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

    # select * distinct sensor_id

    # for each sensor_id
    #   select MAX
    #   select MIN
    #   select AVG
    #   send batch requests

    conn.close()

    return func.HttpResponse("Hi me,\n\nSelected min, max, avg")
