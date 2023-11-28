#!/bin/bash

# az group create --name distro-cwk-rg --location uksouth
# az storage account create --name distrostore --location uksouth --resource-group distro-cwk-rg --sku Standard_LRS
az functionapp create --resource-group distro-cwk-rg --consumption-plan-location uksouth --runtime python --runtime-version 3.10 --functions-version 4 --name distro-sensor-stats --os-type linux --storage-account distrostore
az functionapp config appsettings set --name distro-sensor-gen --resource-group distro-cwk-rg --settings SqlConnectionString="Driver={ODBC Driver 17 for SQL Server};Server=tcp:distro-db-server.database.windows.net,1433;Database=distro-db;Uid=sc21pkm;Pwd=distroDB!;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
