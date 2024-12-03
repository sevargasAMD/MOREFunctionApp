import azure.functions as func
import logging
import json
import pymssql

from function_app import app  # Import the shared app instance

server = 'ATLCINVPRDV01\\INVDBSRV'
database = 'MORE'
username = 'AMD\\yashjain' 
password = 'MissionHacks1.0'

@app.route(route="createIncident", methods=["POST"])
def upload_case(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get request body
        req_body = req.get_json()
        
        # Extract required fields
        inc_id = req_body.get('incID')
        date_reported = req_body.get('dateReported')
        incident_type = req_body.get('incidentType')

        # Validate required fields
        required_fields = ['incID', 'dateReported', 'incidentType']
        missing_fields = [field for field in required_fields if not req_body.get(field)]
        
        if missing_fields:
            return func.HttpResponse(
                json.dumps({
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }),
                status_code=400
            )

        # Connect to database
        conn = pymssql.connect(
            server=server,
            user=username,
            password=password,
            database=database
        )
        cursor = conn.cursor()

        # Build insert query
        fields = list(req_body.keys())
        placeholders = ['?' for _ in fields]
        query = f"""
            INSERT INTO Incidents ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
        """

        # Execute query with parameters
        values = [req_body[field] for field in fields]
        cursor.execute(query, values)
        conn.commit()
        
        # Close connection
        conn.close()

        response =  func.HttpResponse(
            json.dumps({
                "message": "Incident created successfully",
                "incidentId": inc_id
            }),
            status_code=201
        )

        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"

        return response

    except Exception as e:
        logging.error(f'Database error: {str(e)}')
        response =  func.HttpResponse(
            json.dumps({
                "error": "Internal server error",
                "details": str(e)
            }),
            status_code=500
        )

        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"

        return response