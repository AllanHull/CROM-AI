# CROM

# Instructions
Create Azure Web App that performs following requirements
- Build an Azure Web App named CROM
- Host it inside Azure Resource Group rg-CROM-AI
- When accessed, the Web App must display the message "Welcome to CROM"
- Use Azure App Services default unless otherwise specified.

# Axure Resources
Use or reference the following existing Azure resources:
- Resource Group: rg-CROM-AI
- Subscription: Azure subscription 1
- Web App Name: CROM
- Azure Region: East US
- Storage Account: sacromblobstorage

# Storage Inegration Requirements
The Web App must be structured so it can later:
- Read blobs from the storage account.
- List containers.
- Access the blobs: events_crom_ui.json, stores_crom_ui.json, trails_crom_ui.json (located in container json).
A stub function for future blob access must be included.

# Tools
Integrate the following Azure Logic App as a callable endpoint from the Web App:
lg-crom-events-read-http-trigger
https://prod-15.eastus.logic.azure.com:443/workflows/1906dffc4adc4cdbae960cb5235ef7c3/triggers/When_an_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received%2Frun&sv=1.0&sig=5MxclMj9Q21lN8sMTV-S2HfQOzWqKcjWAD8GgiR84a0

# Web App must include 
The Web App must include:
- A Python route/function that calls the Logic App endpoint.
- Logging of the HTTP response.
- Display of:
	◦ A confirmation message such as “Logic App call succeeded”, or
	◦ The JSON returned from the Logic App.

# Model Deliverables
Complete Python Web App Project
The generated project must include:
- app.py (Flask or FastAPI recommended)
- requirements.txt
- README.md
- Optional: deployment scripts or IaC

# Required Python Code
Required Python Code Features
The Web App must include:
- Root Route Displays: "Hello Web App CROM!" in an HTML page format
