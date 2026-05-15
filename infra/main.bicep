// Bicep template for CROM Azure Web App
// Deploys an App Service Plan and Web App with Managed Identity for Azure Storage access

param location string = 'East US'
param appServicePlanName string = 'asp-crom'
param webAppName string = 'CROM'
param skuName string = 'B1'
param skuTier string = 'Basic'
param storageAccountName string = 'sacromblobstorage'

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
      defaultDocuments: [
        'index.html'
        'index.htm'
      ]
      linuxFxVersion: 'STATICSITE|1.0'
    }
  }

  // Configure the web app to host a simple HTML page
  resource config 'config@2023-12-01' = {
    name: 'web'
    properties: {
      numberOfWorkers: 1
      defaultDocuments: [
        'index.html'
        'index.htm'
      ]
      linuxFxVersion: 'STATICSITE|1.0'
    }
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
