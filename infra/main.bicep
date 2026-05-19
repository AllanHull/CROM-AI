// Bicep template for CROM Azure Web App
// Deploys an App Service Plan and Web App with Managed Identity for Azure Storage access

param location string = 'East US'
param appServicePlanName string = 'asp-crom'
param webAppName string = 'CROM'
param skuName string = 'B1'
param skuTier string = 'Basic'
param storageAccountName string = 'sacromblobstorage'
param logicAppEndpoint string = 'https://prod-15.eastus.logic.azure.com:443/workflows/1906dffc4adc4cdbae960cb5235ef7c3/triggers/When_an_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received%2Frun&sv=1.0&sig=5MxclMj9Q21lN8sMTV-S2HfQOzWqKcjWAD8GgiR84a0'

// Reference the existing storage account
resource existingStorageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' existing = {
  name: storageAccountName
}

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: skuName
    tier: skuTier
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

// Web App with System Assigned Managed Identity
resource webApp 'Microsoft.Web/sites@2023-12-01' = {
  name: webAppName
  location: location
  kind: 'app,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      numberOfWorkers: 1
      linuxFxVersion: 'PYTHON|3.11'
      appCommandLine: 'python -m pip install -r requirements.txt && gunicorn --bind 0.0.0.0 --timeout 600 app:app'
      alwaysOn: false
    }
    httpsOnly: true
  }
}

// App Settings
resource webAppSettings 'Microsoft.Web/sites/config@2023-12-01' = {
  parent: webApp
  name: 'appsettings'
  properties: {
    STORAGE_ACCOUNT_NAME: storageAccountName
    STORAGE_ACCOUNT_KEY: listKeys(existingStorageAccount.id, existingStorageAccount.apiVersion).keys[0].value
    LOGIC_APP_ENDPOINT: logicAppEndpoint
    FLASK_ENV: 'production'
    WEBSITES_ENABLE_APP_SERVICE_STORAGE: 'false'
    SCM_DO_BUILD_DURING_DEPLOYMENT: 'true'
    PYTHONPATH: '/home/site/wwwroot'
  }
}

// Web app config for startup command
resource webAppConfig 'Microsoft.Web/sites/config@2023-12-01' = {
  parent: webApp
  name: 'web'
  properties: {
    numberOfWorkers: 1
    linuxFxVersion: 'PYTHON|3.11'
    appCommandLine: 'python -m pip install -r requirements.txt && gunicorn --bind 0.0.0.0 --timeout 600 --workers 2 app:app'
    autoHealEnabled: false
  }
}

// Role Assignment: Grant the Web App's Managed Identity read access to the storage account
// This allows the app to read blobs from the storage account
resource blobReaderRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, webAppName, 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  scope: existingStorageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe') // Storage Blob Data Reader
    principalId: webApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Outputs
output webAppUrl string = 'https://${webApp.properties.defaultHostName}'
output webAppName string = webApp.name
output managedIdentityId string = webApp.identity.principalId
output storageAccountName string = storageAccountName
