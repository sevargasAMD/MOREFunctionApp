import azure.functions as func
import logging
import json
import pymssql

from function_app import app  # Import the shared app instance

server = 'moreteam.database.windows.net'
database = 'MORE'
username = 'moreteam'
password = 'AntiDiversion1.0'

@app.route(route="editIncident", methods=["POST"])
def edit_case(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get request body
        req_body = req.get_json()
        inc_id = req_body.get('incID')
        edit_fields = req_body.get('editFields')

        # Validate required fields
        if not inc_id or not edit_fields:
            return func.HttpResponse(
                json.dumps({
                    "error": "Please provide incidentId and updateFields"
                }),
                status_code=400
            )

        conn = pymssql.connect(
            server=server,
            user=username,
            password=password,
            database=database
        )
        cursor = conn.cursor()

        # Build dynamic SQL query
        updates = ", ".join([f"{key} = ?" for key in edit_fields.keys()])
        query = f"UPDATE Incidents SET {updates} WHERE incID = ?"
        
        # Execute query with parameters
        params = list(edit_fields.values()) + [inc_id]
        cursor.execute(query, params)
        
        # Check if any rows were affected
        if cursor.rowcount == 0:
            return func.HttpResponse(
                json.dumps({
                    "error": f"No incident found with ID: {inc_id}"
                }),
                status_code=404
            )

        conn.commit()

        # Close connection
        conn.close()
        
        response =  func.HttpResponse(
            json.dumps({
                "message": "Incident updated successfully",
                "incidentId": inc_id
            }),
            status_code=200
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