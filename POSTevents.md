# 📘 Instructions‑Events‑GET  
_Read Azure Logic App JSON Blob_

## 🔹 Logic App Name  
`lg-crom-events-update-http-trigger`

## 🔹 HTTP Trigger URL  
https://prod-18.eastus.logic.azure.com:443/workflows/c55da1573d2141e3841561d307c741d1/triggers/When_an_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received%2Frun&sv=1.0&sig=mf9uWRC__zfmnYflZn7VxRsz2P5UcUVPRWKlq0CMdJI

---

# 📝 Instructions  
Your task is to configure the Logic App to update a JSON blob from Azure Storage and return it in HTML format.

---

## 1️⃣ Connect to Azure Storage Blob  
The Logic App must retrieve the following blob:

- Storage Account: `sacromblobstorage`
- Container: `json`
- Blob: `events_crom_ui.json`

Use the Azure Blob Storage REST API to access the blob.

---

## 2️⃣ Use a REST GET action to read the JSON blob  
Add an HTTP action in the Logic App:

### Method
POST

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
  events_crom_ui.json