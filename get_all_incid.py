import azure.functions as func
import pymssql
import logging
import json

from function_app import app  # Import the shared app instance

@app.route(route="get_all_incid")
def get_all_incid(req: func.HttpRequest) -> func.HttpResponse:
    # Database connection details
    server = 'moreteam.database.windows.net'
    database = 'MORE'
    username = 'moreteam'
    password = 'AntiDiversion1.0'

    try:
        
        # Establish connection to SQL Server using pymssql
        conn = pymssql.connect(
            server=server,
            user=username,
            password=password,
            database=database
        )
        # conn = pyodbc.connect(connectionString)
        cursor = conn.cursor()

        # Execute query to fetch all IncID values
        query = "SELECT IncID FROM [dbo].[Master]"
        cursor.execute(query)
        
        # Fetch all rows and convert to list
        incident_ids = [row[0] for row in cursor.fetchall()]
        
        # Close connection
        conn.close()

        # Return results as JSON
        response =  func.HttpResponse(
            json.dumps({"incident_ids": incident_ids}),
            mimetype="application/json",
            status_code=200
        )

        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"

        return response

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )