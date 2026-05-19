# 📘 Instructions‑Events‑GET  
_Read Azure Logic App JSON Blob_

## 🔹 Logic App Name  
`lg-crom-events-read-http-trigger`

## 🔹 HTTP Trigger URL  
https://prod-73.eastus.logic.azure.com:443/workflows/edb28f944da841b88fa8d0d923184675/triggers/When_an_HTTP_request_is_received_for_Stores_JSON_Blob/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received_for_Stores_JSON_Blob%2Frun&sv=1.0&sig=i_6b1gJASPMJWeW4FhZzlkzXe8zraSJfhZVTQzqHj6E

---

# 📝 Instructions  
Your task is to configure the Logic App to read a JSON blob from Azure Storage and return it in HTML format.

---

## 1️⃣ Connect to Azure Storage Blob  
The Logic App must retrieve the following blob:

- Storage Account: `sacromblobstorage`
- Container: `json`
- Blob: `stores_crom_ui.json`

Use the Azure Blob Storage REST API to access the blob.

---

## 2️⃣ Use a REST GET action to read the JSON blob  
Add an HTTP action in the Logic App:

### Method
GET

### URI
https://tstblobstorage.blob.core.windows.net/json/events_crom_ui.json

### Headers
x-ms-version: 2021-08-06  
Content-Type: application/json

### Authentication
Use one of the following:
- Managed Identity (recommended)
- Access Key
- SAS Token

---

## 3️⃣ Convert the JSON blob into HTML  
Wrap the JSON output in HTML so it renders cleanly in a browser.

Example HTML template:

<html>
  <body>
    <h2>Events JSON</h2>
    <pre>@{string(body('HTTP_GET_Blob'))}</pre>
  </body>
</html>

---

## 4️⃣ Return HTML to the caller  
Use a Response action:

- Status Code: 200
- Headers:
  Content-Type: text/html
- Body:
  Output of the HTML compose step

  # Write Output to file
  Write output to file stores_crom_ui.json