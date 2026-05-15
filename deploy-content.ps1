# Deploy web content to CROM web app

# Create a temporary directory
$tempDir = New-Item -Type Directory -Path "$env:TEMP\cromapp" -Force

# Copy the index.html to the temp directory
Copy-Item "index.html" "$tempDir\index.html" -Force

# Create a zip file
$publishZip = "$tempDir\app.zip"
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory("$tempDir", "$publishZip", 'Optimal', $false)

Write-Host "ZIP file created at $publishZip"

# Deploy using zip deploy
az webapp deployment source config-zip --resource-group rg-CROM-AI --name CROM --src $publishZip

if ($LASTEXITCODE -eq 0) {
    Write-Host "Application files deployed successfully!"
    
    # Give it a moment to process
    Start-Sleep -Seconds 3
    
    # Get the web app URL
    $webAppUrl = az webapp show --resource-group rg-CROM-AI --name CROM --query 'defaultHostName' --output tsv
    Write-Host "Web App is available at: https://$webAppUrl"
} else {
    Write-Host "Deployment failed!" -ForegroundColor Red
}

# Clean up
Remove-Item $tempDir -Recurse -Force
