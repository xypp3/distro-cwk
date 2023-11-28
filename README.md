# distro-cwk
Distributed Systems Module Azure Serverless Coursework

## Common Issues

### function_app.py
**Local pyodbc not working**
- Did you install drivers in addition to the library

**Database connection error only when deployed**
- python v10 has ODBC v17 installed!!!
- for ODBC v18, use python v11
