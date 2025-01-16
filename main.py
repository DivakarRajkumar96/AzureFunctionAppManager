import json
import os
import base64
import re
from google.cloud import secretmanager
from azure.identity import CertificateCredential
from azure.mgmt.web import WebSiteManagementClient
from azure.core.exceptions import ResourceNotFoundError

# Hardcoded Azure values
tenant_id = "<tenant-id>"
client_id = "<client-id>"
# subscription_id will be obtained dynamically from resourceid

# Function to parse the resourceid and extract subscription_id, resource_group, and function_app_name
def parse_resourceid(resourceid):
    pattern = r'^/subscriptions/(?P<subscription_id>[0-9a-fA-F-]+)/resourceGroups/(?P<resource_group>[a-zA-Z0-9-_]+)/providers/Microsoft.Web/sites/(?P<function_app_name>.+)$'
    match = re.match(pattern, resourceid)

    if match:
        return match.group("subscription_id"), match.group("resource_group"), match.group("function_app_name")
    else:
        raise ValueError("Invalid resourceid format")

# Function to retrieve secrets from Google Secret Manager
def get_secret(secret_name):
    try:
        client = secretmanager.SecretManagerServiceClient()
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')  # Google Cloud Project ID
        secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        secret = client.access_secret_version(name=secret_path)
        return secret.payload.data.decode('UTF-8')
    except Exception as e:
        raise Exception(f"Error retrieving secret '{secret_name}': {str(e)}")

# Authenticate using the certificate for Azure SDK
def authenticate_with_certificate():
    try:
        certificate_data_base64 = get_secret("azure_access_certificate")
        cert_password = get_secret("azure_access_certificate_pass")

        certificate_data = base64.b64decode(certificate_data_base64)

        credential = CertificateCredential(tenant_id, client_id, certificate_data=certificate_data, password=cert_password)
        return credential
    except Exception as e:
        raise Exception(f"Error authenticating with certificate: {str(e)}")

# Initialize Azure WebSiteManagementClient
def get_web_client(subscription_id):
    try:
        credential = authenticate_with_certificate()
        web_client = WebSiteManagementClient(credential, subscription_id)  # Pass subscription_id here
        return web_client
    except Exception as e:
        raise Exception(f"Error getting web client: {str(e)}")

# Function to enable or disable the Azure Function App
def manage_function_app(resource_group, function_app_name, action, subscription_id):
    try:
        # Pass subscription_id to get_web_client
        web_client = get_web_client(subscription_id)

        if action == "enable":
            web_client.web_apps.start(resource_group, function_app_name)
            return f"Function App {function_app_name} is now enabled."
        
        elif action == "disable":
            web_client.web_apps.stop(resource_group, function_app_name)
            return f"Function App {function_app_name} is now disabled."

        else:
            return "Invalid action. Use 'enable' or 'disable'."
    
    except ResourceNotFoundError:
        return f"Function App {function_app_name} not found in resource group {resource_group}."
    
    except Exception as e:
        raise Exception(f"Error managing Function App: {str(e)}")

# Google Cloud Function entry point
def function_handler(request):
    try:
        # Parse the incoming JSON request
        data = request.get_json()
        
        # Extract resourceid from the request
        resourceid = data.get("resourceid")
        if not resourceid:
            return json.dumps({"error": "Missing required field 'resourceid'"}), 400
        
        # Extract subscription_id, resource_group, and function_app_name from the resourceid
        try:
            subscription_id, resource_group_name, function_app_name = parse_resourceid(resourceid)
        except ValueError as e:
            return json.dumps({"error": str(e)}), 400

        # Extract action from the request
        action = data.get("action")
        if not action:
            return json.dumps({"error": "Missing required field 'action'"}), 400

        # Call the Azure function app management logic based on action, passing subscription_id
        result = manage_function_app(resource_group_name, function_app_name, action, subscription_id)

        return json.dumps({"status": result}), 200
    
    except Exception as e:
        # Log detailed exception for debugging
        error_message = f"An error occurred: {str(e)}"
        print(error_message)  # Log to stdout for Cloud Functions logs
        return json.dumps({"error": error_message}), 500
