import azure.functions as func
import pymssql
import jsonify

from function_app import app  # Import the shared app instance

# Database connection details
server = 'moreteam.database.windows.net'
database = 'MORE'
username = 'moreteam'
password = 'AntiDiversion1.0'
 
def get_incident_data_from_table(table_name, columns, incident_id):
    """
    Fetch data from a specific table based on the IncID.
    """
    conn = pymssql.connect(server=server, user=username, password=password, database=database)
    cursor = conn.cursor()
   
    # Create a SQL query dynamically based on columns
    columns_str = ", ".join(columns)
    query = f"SELECT {columns_str} FROM [{table_name}] WHERE IncID = %s"
    cursor.execute(query, (incident_id,))
    rows = cursor.fetchall()
    conn.close()
   
    return rows
 
 
@app.route(route='get-incident', methods=['POST'])
def get_incident(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get incident data from specified tables and columns.
    Accepts a JSON payload with the structure:
    {
        "incidentID": "123",
        "tables": {
            "Master": ["Col1", "Col2"],
            "AnotherTable": ["ColA", "ColB"]
        }
    }
    """
   
    # Parse the JSON payload
    payload = req.get_json()
    #print(payload)
    if not payload:
        return jsonify({"error": "Request payload is missing"}), 400
 
 
    incident_id = payload.get("incidentID")
    tables = payload.get("tables")
 
 
    if not incident_id:
        return jsonify({"error": "incidentID is required"}), 400
    if not tables:
        return jsonify({"error": "tables and columns are required"}), 400
 
 
    # Prepare the final result
    column_data = {}
 
 
    # Initialize keys for all requested columns with empty lists
    for table, columns in tables.items():
        for column in columns:
            if column not in column_data:
                column_data[column] = []
 
 
    # Fetch data for each table
    for table, columns in tables.items():
        data = get_incident_data_from_table(table, columns, incident_id)
 
 
        # Append values to respective column lists
        for row in data:
            for col_index, column in enumerate(columns):
                column_data[column].append(row[col_index])
 
    if any(column_data.values()):
        return jsonify(column_data)
    else:
        return jsonify({"message": "No data found for the given incidentID"}), 404
 
def get_incident_data(incident_id):
    # Establish connection to SQL Server
    conn = pymssql.connect(server=server, user=username, password=password, database=database)
    cursor = conn.cursor()
 
    # Execute query with parameterized input
    query = "SELECT * FROM [dbo].[Master] WHERE IncID = %s"
    cursor.execute(query, (incident_id,))
    rows = cursor.fetchall()
 
    # Close the connection
    conn.close()
    return rows
 
# Define a route for the endpoint
@app.route(route='get-metadata', methods=['GET'])
def get_metadata(req: func.HttpRequest) -> func.HttpResponse:
    # Get 'incidentID' from the request arguments
    incident_id = req.params.get('incidentID')
    if not incident_id:
        return jsonify({"error": "incidentID is required"}), 400
 
    # Fetch data from the database
    data = get_incident_data(incident_id)
    # Column names
    col_names = [
    "IncID",
    "Date_Reported",
    "Incident_Type",
    "Total_QTY_of_Parts",
    "Region",
    "Country",
    "State_Province",
    "CAR_ID",
    "Customs_Port_Agency",
    "Country_of_Origin",
    "Destination_Country",
    "Location_Recovered",
    "Seizure_Date",
    "Bond_Amount",
    "Customs_IPR_Infringement_Type",
    "Subpoena",
    "Subpoena_Open_Closed",
    "C_D",
    "C_D_Open_Closed",
    "Due_Diligence",
    "Enhanced_Due_Diligence",
    "Image",
    "Notes"
    ]
    print(data[0])
    print("data above!!!!!")
# Map each column name to corresponding data entry  
    mapped_data = dict(zip(col_names, data[0]))
 
# Display the mapped data
    print(mapped_data)
 
    if data:
        return jsonify(mapped_data)
    else:
        return jsonify({"message": "No data found for the given incidentID"}), 404
 
 
TABLES_AND_COLUMNS = {
    "Master": [
        "IncID", "Date_Reported", "Incident_Type", "Total_QTY_of_Parts", "Region",
        "Country", "State_Province", "CAR_ID", "Customs_Port_Agency", "Country_of_Origin",
        "Destination_Country", "Location_Recovered", "Seizure_Date", "Bond_Amount",
        "Customs_IPR_Infringement_Type", "Subpoena", "Subpoena_Open_Closed", "C_D",
        "C_D_Open_Closed", "Due_Diligence", "Enhanced_Due_Diligence", "Image", "Notes"
    ],
    "Entities": [
        "EntID",
        "IncID",
        "Entity_Type",
        "Company_Name",
        "Web_Address",
        "Physical_Address",
        "State_Province",
        "Country",
        "Region",
        "Individual_Owner",
        "US_Entity_Listed_Y_N",
        "Context",
        "Blocked_on_AMD_S4_GTS_ERP_Y_N",
        "Date_Blocked"
    ],
    "Product Analysis": [
        "ProdID",
        "IncID",
        "CAR_ID",
        "Trace_Request_ID",
        "Media_NGO_Source",
        "Product_Family",
        "Part_Number",
        "Date_Code",
        "Serial_No",
        "_2D_Barcode",
        "QTY",
        "Type",
        "Ship_To_Name",
        "Ship_To_Address",
        "Ship_Date",
        "Qty_Shipped",
        "Test_Buy_Y_N",
        "US_ECCN",
        "Subpoena_Y_N",
        "Details"
    ]
}
 
@app.route(route='get-columns', methods=['GET'])
def get_columns(req: func.HttpRequest) -> func.HttpResponse:
    """
    Fetches the list of columns for a given table name.
    """
    table_name = req.params.get('table')
   
    if not table_name:
        return jsonify({"error": "Table name is required"}), 400
 
    # Check if the table exists in the dictionary
    if table_name in TABLES_AND_COLUMNS:
        return jsonify({
            "table": table_name,
            "columns": TABLES_AND_COLUMNS[table_name]
        })
    else:
        return jsonify({"error": f"Table '{table_name}' not found"}), 404
 
 