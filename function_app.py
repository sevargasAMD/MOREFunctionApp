import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)  # Create a Function App instance

# Import API routes to register them with the app
import get_all_incid
import get_data_by_incid
import edit_case
import upload_case
