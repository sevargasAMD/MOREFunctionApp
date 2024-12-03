
import azure.functions as func
import pymssql
import logging
import json
from azure.functions import HttpRequest, HttpResponse

# Database connection details
server = 'ATLCINVPRDV01\\INVDBSRV'  # Server name
database = 'MORE'                   # Database name
username = 'AMD\\yashjain'          # Username with domain
password = 'MissionHacks1.0'        # Password

from function_app import app  # Import the shared app instance


def get_incident_data(incident_id):
    """
    Fetch incident data from the database based on the incident ID.
    """
    try:
        # Establish connection to SQL Server
        conn = pymssql.connect(
            server=server, 
            user=username, 
            password=password, 
            database=database)
        cursor = conn.cursor()

        cursor = conn.cursor(as_dict=True)

        # Execute query with parameterized input
        logging.info(incident_id)

        query = "SELECT * FROM [dbo].[Master Data] WHERE IncID = %s"
        cursor.execute(query, (incident_id,))
        rows = cursor.fetchall()

        # Close the connection
        conn.close()
        return rows

    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return None


@app.route(route="get_data_by_incid")
def get_data_by_incid(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main function for the Azure Function.
    Handles HTTP GET requests to fetch incident data.
    """
    logging.info('Processing a request for /get-incident.')

    # Get 'incidentID' from the query parameters
    incident_id = req.params.get('incidentID')
    
    if not incident_id:
        return HttpResponse(
            json.dumps({"error": "incidentID is required"}),
            status_code=400,
            mimetype="application/json"
        )

    # Fetch data from the database
    data = get_incident_data(incident_id)

    if data:
        response =  HttpResponse(
            json.dumps(data, default=str),
            status_code=200,
            mimetype="application/json"
        )

        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"

        return response

    else:
        response = HttpResponse(
            json.dumps({"message": "No data found for the given incidentID"}),
            status_code=404,
            mimetype="application/json"
        )
    
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"

        return response
    