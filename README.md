# CROM - Azure Web App

A Flask-based Azure Web App that integrates with Azure Storage Blobs and Azure Logic Apps.

## Overview

CROM is a Python web application built with Flask that demonstrates:
- **Azure Storage Integration**: Read blobs from Azure Storage Account
- **Azure Logic App Integration**: Call a Logic App endpoint via HTTP
- **Web UI**: Interactive HTML interface for testing integrations
- **Logging**: Comprehensive logging of all HTTP requests and responses

## Features

### Core Features
- ✅ Welcome page displaying "Welcome to CROM" message
- ✅ Azure Storage Blob integration with stub functions for future blob access
- ✅ Logic App HTTP endpoint caller with response logging
- ✅ Interactive web interface with buttons to trigger Azure services
- ✅ JSON response display and error handling
- ✅ Health check endpoint for monitoring

### Azure Integration
- **Storage Account**: `sacromblobstorage`
- **Container**: `json`
- **Blobs**: 
  - `events_crom_ui.json`
  - `stores_crom_ui.json`
  - `trails_crom_ui.json`
- **Logic App**: `lg-crom-events-read-http-trigger`

## Project Structure

```
CROM-AI/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .env.example             # Environment variables template
├── templates/
│   └── index.html           # Welcome page HTML template
├── infra/
│   └── main.bicep           # Azure infrastructure as code
└── deploy.ps1               # Deployment script
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Azure Storage Account credentials
- Azure subscription

### Setup

1. **Clone/navigate to the project**
   ```bash
   cd CROM-AI
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the root directory:
   ```
   FLASK_ENV=development
   STORAGE_ACCOUNT_NAME=sacromblobstorage
   STORAGE_ACCOUNT_KEY=your_storage_account_key_here
   LOGIC_APP_ENDPOINT=https://prod-15.eastus.logic.azure.com:443/workflows/1906dffc4adc4cdbae960cb5235ef7c3/triggers/When_an_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received%2Frun&sv=1.0&sig=5MxclMj9Q21lN8sMTV-S2HfQOzWqKcjWAD8GgiR84a0
   PORT=5000
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

   The application will be available at `http://localhost:5000`

## API Endpoints

### GET `/`
Returns the welcome page with the UI for interacting with Azure services.

**Features**:
- Status dashboard showing application health
- Interactive buttons to call Logic App endpoints
- Real-time data display with formatted JSON responses
- Blob listing functionality
- Loading indicators and error handling

**Response**: HTML page with interactive components

### GET `/api/call-logic-app`
Calls the Azure Logic App endpoint and returns the response.

**Request**:
```json
GET /api/call-logic-app
```

**Response**:
```json
{
  "status": "success",
  "message": "Logic App call succeeded",
  "data": { ... }
}
```

### GET `/api/call-logic-app-json`
Route to call the Logic App endpoint and return JSON response. Sends GET request to the Logic App, logs the response, and returns JSON.

**Request**:
```json
GET /api/call-logic-app-json
```

**Response**:
```json
{
  "status": "success",
  "message": "Logic App call succeeded",
  "data": { ... }
}
```

### GET `/api/blobs`
Retrieves a list of available blobs from the `json` container in Azure Storage.

**Request**:
```
GET /api/blobs
```

**Response**:
```json
{
  "status": "success",
  "blobs": [
    { "name": "events_crom_ui.json", "size": 12345 },
    { "name": "stores_crom_ui.json", "size": 54321 },
    { "name": "trails_crom_ui.json", "size": 98765 }
  ]
}
```

### GET `/api/call-logic-app-html`
Calls the Azure Logic App endpoint and returns the response formatted as an HTML page with styled tables and data visualization.

**Request**:
```
GET /api/call-logic-app-html
```

**Response**: HTML page with formatted response data and styling.

### GET `/health`
Health check endpoint for monitoring and load balancer configuration.

**Response**:
```json
{
  "status": "healthy"
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment mode | `production` |
| `STORAGE_ACCOUNT_NAME` | Azure Storage Account name | `sacromblobstorage` |
| `STORAGE_ACCOUNT_KEY` | Azure Storage Account access key | `` |
| `LOGIC_APP_ENDPOINT` | Logic App HTTP trigger URL | (from Instructions.md) |
| `PORT` | Port to run the Flask app on | `5000` |

## Deployment to Azure

### Using Azure App Service

1. **Prepare for deployment**
   ```bash
   # Create Azure resources (update resource group and app name as needed)
   az group create --name rg-CROM-AI --location eastus
   az appservice plan create --name crom-plan --resource-group rg-CROM-AI --sku F1
   az webapp create --name CROM --resource-group rg-CROM-AI --plan crom-plan --runtime "PYTHON|3.11"
   ```

2. **Deploy using Git**
   ```bash
   az webapp deployment source config-zip --resource-group rg-CROM-AI --name CROM --src app.zip
   ```

3. **Configure application settings**
   ```bash
   az webapp config appsettings set --resource-group rg-CROM-AI --name CROM \
     --settings STORAGE_ACCOUNT_NAME=sacromblobstorage \
     STORAGE_ACCOUNT_KEY="your-storage-key" \
     FLASK_ENV=production
   ```

### Using Bicep Infrastructure as Code

See `infra/main.bicep` for infrastructure definition.

Deploy with:
```bash
az deployment group create \
  --resource-group rg-CROM-AI \
  --template-file infra/main.bicep
```

## Local Development

### Running with Debug Mode
```bash
FLASK_ENV=development python app.py
```

### Testing Endpoints
```bash
# Test home page
curl http://localhost:5000/

# Test health check
curl http://localhost:5000/health

# Test Logic App call
curl -X GET http://localhost:5000/api/call-logic-app

# Test Logic App JSON call
curl -X GET http://localhost:5000/api/call-logic-app-json

# Test Logic App HTML response
curl -X GET http://localhost:5000/api/call-logic-app-html

# Test blob listing
curl http://localhost:5000/api/blobs
```

## Logging

The application logs all requests and responses to the console and can be configured to log to a file.

Log levels:
- `INFO`: General application flow
- `WARNING`: Potential issues
- `ERROR`: Errors requiring attention

Example log output:
```
2024-05-15 10:30:45,123 - __main__ - INFO - Home route accessed
2024-05-15 10:30:50,456 - __main__ - INFO - Calling Logic App endpoint
2024-05-15 10:30:51,789 - __main__ - INFO - Logic App response status: 200
```

## Azure Storage Integration

### Stub Functions

The application includes stub functions for future blob access:

1. **`get_blob_service_client()`** - Initializes Azure Blob Service Client
2. **`list_blob_containers()`** - Lists all containers in the storage account
3. **`get_blob_data(container_name, blob_name)`** - Retrieves blob data

These functions can be extended to implement full blob access functionality.

### Usage Example
```python
# Get blob data
blob_data = get_blob_data('json', 'events_crom_ui.json')
if blob_data:
    import json
    events = json.loads(blob_data)
    # Process events...
```

## Logic App Integration

The application calls the Logic App endpoint to trigger workflows:

- **Endpoint**: `lg-crom-events-read-http-trigger`
- **Method**: HTTP GET
- **Response Type**: JSON

The response is logged and displayed in the web UI.

## Troubleshooting

### Storage Connection Issues
- Verify `STORAGE_ACCOUNT_KEY` is correct
- Check that the storage account exists in the correct resource group
- Ensure the container name is spelled correctly

### Logic App Call Failures
- Verify the Logic App endpoint URL is correct
- Check that the Logic App is enabled
- Verify network connectivity to the Logic App

### Port Already in Use
```bash
# Use a different port
PORT=5001 python app.py
```

## Security Considerations

- Store sensitive credentials (storage keys, endpoints) in environment variables
- Use Azure Managed Identity in production instead of storage account keys
- Configure CORS policies for API endpoints
- Enable HTTPS for production deployments
- Implement authentication/authorization as needed

## Dependencies

- **Flask**: Web framework
- **azure-storage-blob**: Azure Storage integration
- **azure-identity**: Azure authentication
- **requests**: HTTP requests library
- **python-dotenv**: Environment variable management
- **gunicorn**: Production WSGI server

See `requirements.txt` for versions.

## Contributing

When extending the application:
1. Add new routes in `app.py`
2. Update API endpoint documentation in this README
3. Add corresponding HTML UI elements in `templates/index.html`
4. Test endpoints locally before deploying
5. Add appropriate logging statements

## License

This project is provided as-is for demonstration and development purposes.

## Support

For issues or questions:
1. Check logs: `FLASK_ENV=development python app.py`
2. Verify environment variables are set correctly
3. Check Azure resource status in Azure Portal
4. Review Flask and Azure SDK documentation
