# CROM Azure Web App Deployment Script
# This script deploys the CROM web app to Azure using Bicep

param(
    [string]$ResourceGroup = "rg-CROM-AI",
    [string]$WebAppName = "CROM",
    [string]$Location = "East US",
    [string]$Subscription = "Azure subscription 1"
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
$SuccessColor = "Green"
$ErrorColor = "Red"
$InfoColor = "Cyan"

Write-Host "Starting CROM Web App Deployment..." -ForegroundColor $InfoColor

# Check if Azure CLI is installed
try {
    $azVersion = az --version
    Write-Host "Azure CLI is installed" -ForegroundColor $SuccessColor
} catch {
    Write-Host "Azure CLI is not installed. Please install it first." -ForegroundColor $ErrorColor
    exit 1
}

# Set the subscription
Write-Host "Setting subscription..." -ForegroundColor $InfoColor
az account set --subscription $Subscription

# Verify resource group exists
Write-Host "Verifying resource group '$ResourceGroup'..." -ForegroundColor $InfoColor
$rg = az group show --name $ResourceGroup 2>$null
if (-not $rg) {
    Write-Host "Resource group '$ResourceGroup' does not exist. Creating..." -ForegroundColor $InfoColor
    az group create --name $ResourceGroup --location $Location
    Write-Host "Resource group created successfully" -ForegroundColor $SuccessColor
} else {
    Write-Host "Resource group '$ResourceGroup' already exists" -ForegroundColor $SuccessColor
}

# Deploy the Bicep template
Write-Host "Deploying Azure resources using Bicep template..." -ForegroundColor $InfoColor
$deploymentName = "crom-deployment-$(Get-Date -Format 'yyyyMMddHHmmss')"

try {
    az deployment group create `
        --name $deploymentName `
        --resource-group $ResourceGroup `
        --template-file "infra/main.bicep" `
        --parameters `
            appServicePlanName="asp-crom" `
            webAppName=$WebAppName `
            resourceGroupName=$ResourceGroup `
            location=$Location
    
    Write-Host "Deployment completed successfully" -ForegroundColor $SuccessColor
} catch {
    Write-Host "Deployment failed: $_" -ForegroundColor $ErrorColor
    exit 1
}

# Get the deployment outputs
Write-Host "Retrieving deployment outputs..." -ForegroundColor $InfoColor
$output = az deployment group show `
    --name $deploymentName `
    --resource-group $ResourceGroup `
    --query properties.outputs

Write-Host "Deployment outputs:" -ForegroundColor $InfoColor
Write-Host $output

# Deploy the web app content
Write-Host "Deploying web app content..." -ForegroundColor $InfoColor

# Create a temporary directory for deployment
$timestamp = Get-Date -Format 'yyyyMMddHHmmss'
$tempDir = "$env:TEMP\cromapp_$timestamp"
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -Type Directory -Path $tempDir | Out-Null

# Copy application files
Write-Host "Preparing application files..." -ForegroundColor $InfoColor
Copy-Item "app.py" "$tempDir\app.py" -Force
Copy-Item "requirements.txt" "$tempDir\requirements.txt" -Force
Copy-Item "templates" "$tempDir\templates" -Recurse -Force

# Create templates directory if it doesn't exist
if (-not (Test-Path "$tempDir\templates")) {
    New-Item -Type Directory -Path "$tempDir\templates" | Out-Null
    Copy-Item "index.html" "$tempDir\templates\index.html" -Force
}

# Deploy using zip deploy
Write-Host "Uploading application files to $WebAppName..." -ForegroundColor $InfoColor
$publishZip = "$tempDir\app.zip"

try {
    # Create zip file with better error handling
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    
    # Remove zip if it exists
    if (Test-Path $publishZip) {
        Remove-Item $publishZip -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 500
    }
    
    [System.IO.Compression.ZipFile]::CreateFromDirectory("$tempDir", "$publishZip", "Optimal", $false)
    
    # Deploy the zip file
    az webapp deployment source config-zip `
        --resource-group $ResourceGroup `
        --name $WebAppName `
        --src $publishZip
    
    Write-Host "Application files uploaded successfully" -ForegroundColor $SuccessColor
}
catch {
    Write-Host "Error during deployment: $_" -ForegroundColor $ErrorColor
}
finally {
    # Clean up temp files - wait a moment before cleanup
    Start-Sleep -Milliseconds 1000
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Get the web app URL
Write-Host "Retrieving web app URL..." -ForegroundColor $InfoColor
$webAppUrl = az webapp show `
    --resource-group $ResourceGroup `
    --name $WebAppName `
    --query "defaultHostName" `
    --output tsv

$fullUrl = "https://$webAppUrl"
Write-Host "Web App is available at: $fullUrl" -ForegroundColor $SuccessColor
Write-Host "Deployment completed successfully!" -ForegroundColor $SuccessColor
