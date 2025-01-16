# Azure Function App Management Script

## Overview

This script allows you to manage Azure Function Apps by enabling or disabling them. The script uses Azure SDK for Python, Google Cloud Secret Manager, and certificate-based authentication for Azure. It can be triggered via a Google Cloud Function and expects a JSON payload with specific details.

### Key Features:

- Enable or disable Azure Function Apps
- Azure authentication using client certificate
- Secure secret management with Google Cloud Secret Manager

## Prerequisites

Before running this script, make sure you have the following prerequisites:

### Google Cloud Requirements:

1. **Google Cloud Project**: Ensure you have a Google Cloud Project with `Secret Manager` API enabled.
2. **Google Cloud Secret Manager Access**: 
   - The script uses Google Secret Manager to retrieve secrets for authentication. Ensure that the `azure_access_certificate` and `azure_access_certificate_pass` are stored as secrets in Google Cloud Secret Manager.
   
3. **Google Cloud Function**: 
   - Ensure you have set up a Google Cloud Function to deploy this script.

4. **Service Account Permissions**:
   - The service account running the Google Cloud Function should have permission to access secrets from Google Secret Manager.

### Azure Requirements:

1. **Azure Subscription**: The script interacts with Azure resources using a `client_id` and `tenant_id` associated with your Azure AD Application.
   
2. **Azure Active Directory (AD) Application**:
   - **Client Certificate**: The script uses certificate-based authentication for accessing Azure resources. You need a valid certificate to authenticate the Azure client. Store the certificate and its password as secrets in Google Cloud Secret Manager (`azure_access_certificate` and `azure_access_certificate_pass`).

3. **Azure Permissions**:
   - **WebSiteManagementClient**: The Azure AD Application used for authentication should have permissions to manage Azure Web Apps (Function Apps) via `WebSiteManagementClient`.
   - Ensure that the application has sufficient permissions to start/stop Azure Function Apps within the specified resource group and subscription.

### Azure Role Permissions:

Ensure that your Azure AD Application (identified by `client_id`) has the following roles:

- **Contributor** or higher for the target **resource group** in Azure.
- **Reader** and **Contributor** roles on the **Web Apps** to manage function apps.

### Dependencies:

1. **Python 3.x** (preferably Python 3.7 or higher)
2. **Google Cloud SDK**: To interact with Google Cloud Secret Manager.
3. **Azure SDK for Python**: To interact with Azure resources (Web Apps, Function Apps).
   - Install required Python libraries by running:
   
   ```bash
   pip install google-cloud-secret-manager azure-identity azure-mgmt-web azure-core
   ```
4. **Base64**: Used for decoding the certificate data from Google Cloud Secret Manager.

## Usage

1. Clone this repository to your local machine or cloud environment.
```bash
git clone https://github.com/your-repository/azure-function-app-management.git
cd azure-function-app-management
```

2. Set up Google Cloud credentials:

Ensure you have access to your Google Cloud project and that you have the appropriate credentials set up to access Secret Manager.

3. Set up Azure credentials:

Upload the Azure client certificate and its password to Google Secret Manager as azure_access_certificate and azure_access_certificate_pass, respectively.

4. Deploy the script to Google Cloud Function:

You can deploy this script to a Google Cloud Function that will handle HTTP requests.

5. Trigger the Function:

Send a POST request to the deployed Cloud Function with the following JSON payload:

## JSON Payload Structure:

```json
{
  "resourceid": "/subscriptions/955b7080-d19b-4193-b818-4aa8dafdac77/resourceGroups/functionappentest/providers/Microsoft.Web/sites/FunctionAppEnTest1",
  "action": "<action>"
}
```

Where:

"resourceid": The full resource ID of the Azure Function App.
"action": Specify either "enable" or "disable" to manage the Azure Function App state.

## Example Request

You can test the function from Google Cloud Shell by sending a POST request:

```bash
curl -X POST https://your-cloud-function-url \
  -H "Content-Type: application/json" \
  -d '{
    "resourceid": "/subscriptions/955b7080-d19b-4193-b818-4aa8dafdac77/resourceGroups/functionappentest/providers/Microsoft.Web/sites/FunctionAppEnTest1",
    "action": "enable"
  }'
```

Alternatively, you can use Python's requests library or any HTTP client to make the request.

### Testing Method in Google Cloud Shell
## Cloud Shell Testing:
To test the function directly from Google Cloud Shell, ensure you have set up the necessary credentials in your environment. Follow these steps:

1. Set up environment variables for Google Cloud Project (replace your-project-id with your actual Google Cloud project ID):
```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
```

2. Set up environment variables for Azure (replace your-tenant-id, your-client-id with your Azure credentials):
```bash
export AZURE_TENANT_ID=your-tenant-id
export AZURE_CLIENT_ID=your-client-id
```

3. Send the test payload using curl (adjust the Cloud Function URL as needed):
```bash
curl -X POST https://your-cloud-function-url \
  -H "Content-Type: application/json" \
  -d '{
    "resourceid": "/subscriptions/955b7080-d19b-4193-b818-4aa8dafdac77/resourceGroups/functionappentest/providers/Microsoft.Web/sites/FunctionAppEnTest1",
    "action": "enable"
  }'
```
The response will indicate whether the function app was successfully enabled or disabled.

### Example Output

Success Response:
```json
{
  "status": "Function App FunctionAppEnTest1 is now enabled."
}
```

Error Response:
```json
{
  "error": "Function App FunctionAppEnTest1 not found in resource group functionappentest."
}
```

## Conclusion
This script provides a straightforward way to manage Azure Function Apps (enable/disable) using Google Cloud Function and certificate-based Azure authentication. Ensure you have the necessary Azure permissions and that the required secrets are stored securely in Google Cloud Secret Manager before running the script.
