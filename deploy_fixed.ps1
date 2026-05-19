# CROM Azure Web App Deployment Script
# This script deploys the CROM web app to Azure using Bicep

param(
    [string]$ResourceGroup = "rg-CROM-AI",
    [string]$WebAppName = "crom",   # must be lowercase for Azure Web Apps
    [string]$Location = "East US",
    [string]$Subscription = "81e4777c-2e8e-43b7-8de9-18ebd1a19bbd"
)

$ErrorActionPreference = "Stop"

$SuccessColor = "Green"
$ErrorColor = "Red"
$InfoColor = "Cyan"

Write-Host "Starting CROM Web App Deployment..." -ForegroundColor $InfoColor

# ---------------------------------------------------------
# 1. Check Azure CLI
# ---------------------------------------------------------
try {
    az --version > $null
    Write-Host "Azure CLI is installed" -ForegroundColor $SuccessColor
} catch {
    Write-Host "Azure CLI is not installed. Please install it first." -ForegroundColor $ErrorColor
    exit 1
}

# ---------------------------------------------------------
# 2. Set subscription
# ---------------------------------------------------------
Write-Host "Setting subscription..." -ForegroundColor $InfoColor
az account set --subscription $Subscription

# ---------------------------------------------------------
# 3. Ensure resource group exists
# ---------------------------------------------------------
Write-Host "Verifying resource group '$ResourceGroup'..." -ForegroundColor $InfoColor
$rg = az group show --name $ResourceGroup 2>$null

if (-not $rg) {
    Write-Host "Resource group '$ResourceGroup' does not exist. Creating..." -ForegroundColor $InfoColor
    az group create --name $ResourceGroup --location $Location | Out-Null
    Write-Host "Resource group created successfully" -ForegroundColor $SuccessColor
} else {
    Write-Host "Resource group '$ResourceGroup' already exists" -ForegroundColor $SuccessColor
}

# ---------------------------------------------------------
# 4. Deploy Bicep template
# ---------------------------------------------------------
Write-Host "Deploying Azure resources using Bicep template..." -ForegroundColor $InfoColor

$deploymentName = "crom-deployment-$(Get-Date -Format 'yyyyMMddHHmmss')"

try {
    $deployResult = az deployment group create `
        --name $deploymentName `
        --resource-group $ResourceGroup `
        --template-file "infra/main.bicep" `
        --parameters appServicePlanName="asp-crom" webAppName=$WebAppName location=$Location `
        --output json | ConvertFrom-Json

    Write-Host "Deployment completed successfully" -ForegroundColor $SuccessColor
} catch {
    Write-Host "Deployment failed: $_" -ForegroundColor $ErrorColor
    exit 1
}

# ---------------------------------------------------------
# 5. Retrieve deployment outputs
# ---------------------------------------------------------
Write-Host "Retrieving deployment outputs..." -ForegroundColor $InfoColor

$output = az deployment group show `
    --name $deploymentName `
    --resource-group $ResourceGroup `
    --query properties.outputs `
    --output json | ConvertFrom-Json

Write-Host "Deployment outputs:" -ForegroundColor $InfoColor
$output | ConvertTo-Json -Depth 10

# ---------------------------------------------------------
# 6. Prepare ZIP package (fixed)
# ---------------------------------------------------------
Write-Host "Deploying web app content..." -ForegroundColor $InfoColor

$timestamp = Get-Date -Format 'yyyyMMddHHmmss'
$tempDir = "$env:TEMP\cromapp_$timestamp"

if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -Type Directory -Path $tempDir | Out-Null

Write-Host "Preparing application files..." -ForegroundColor $InfoColor

Copy-Item "app.py" "$tempDir\app.py" -Force
Copy-Item "requirements.txt" "$tempDir\requirements.txt" -Force

# Fix: ensure templates folder is copied correctly
if (Test-Path "templates") {
    Copy-Item "templates" "$tempDir\templates" -Recurse -Force
} else {
    New-Item -Type Directory -Path "$tempDir\templates" | Out-Null
    Copy-Item "index.html" "$tempDir\templates\index.html" -Force
}

# ---------------------------------------------------------
# 7. Create ZIP using Compress-Archive (no file locking)
# ---------------------------------------------------------
Write-Host "Creating ZIP package..." -ForegroundColor $InfoColor

$publishZip = "$tempDir\app.zip"

if (Test-Path $publishZip) {
    Remove-Item $publishZip -Force -ErrorAction SilentlyContinue
}

Compress-Archive -Path "$tempDir\*" -DestinationPath $publishZip -Force

Start-Sleep -Milliseconds 300

# ---------------------------------------------------------
# 8. Deploy ZIP to Azure Web App
# ---------------------------------------------------------
Write-Host "Uploading application files to $WebAppName..." -ForegroundColor $InfoColor

try {
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
    Start-Sleep -Milliseconds 500
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# ---------------------------------------------------------
# 9. Output final URL
# ---------------------------------------------------------
Write-Host "Retrieving web app URL..." -ForegroundColor $InfoColor

$webAppUrl = az webapp show `
    --resource-group $ResourceGroup `
    --name $WebAppName `
    --query "defaultHostName" `
    --output tsv

Write-Host "Web App is available at: https://$webAppUrl" -ForegroundColor $SuccessColor
Write-Host "Deployment completed successfully!" -ForegroundColor $SuccessColor
