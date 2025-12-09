param()

# =========================
# Allure results upload script for Jenkins (Windows / PowerShell)
# =========================
#
# Usage in Jenkins:
# - Add a build step: "PowerShell"
# - Command: .\upload_allure_results.ps1
# - Ensure tests already generated the allure-results folder earlier in the job.
# - Bind a Secret Text credential to env var REPORT_API_TOKEN (same as ALLURE_UPLOAD_TOKEN in your Flask .env).

$REPORT_UPLOAD_URL = "https://gnat-teaching-gladly.ngrok-free.app/api/reports/upload"
$REPORT_PROJECT    = "Health_care"
$REPORT_ENV        = "QA"

# Prefer to pull the token from a Jenkins Secret Text mapped to an env var
$REPORT_API_TOKEN  = "bbbb3b268947d462cf2162dc273d8207cbe45eef7a5aa3912bf677cf473196f3"

if (-not $REPORT_API_TOKEN) {
    Write-Error "REPORT_API_TOKEN environment variable is not set."
    exit 1
}

# 1) Zip allure-results (tests should already be run before this script)
if (-not (Test-Path "allure-results")) {
    Write-Error "allure-results directory not found!"
    exit 1
}

$zipPath = "allure-results.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

Compress-Archive -Path "allure-results\*" -DestinationPath $zipPath -Force

# 2) Upload to Flask/TAG backend
$headers = @{
    Authorization = "Bearer $REPORT_API_TOKEN"
}

$buildId = if ($env:BUILD_TAG) { $env:BUILD_TAG } else { "manual-$([guid]::NewGuid().ToString())" }

$form = @{
    project     = $REPORT_PROJECT
    environment = $REPORT_ENV
    build_id    = $buildId
    executed_by = "jenkins"
    file        = Get-Item $zipPath
}

Write-Host "Uploading Allure results to $REPORT_UPLOAD_URL ..."
$response = Invoke-WebRequest -Uri $REPORT_UPLOAD_URL -Method Post -Headers $headers -Form $form -ErrorAction Stop

Write-Host "Status: $($response.StatusCode)"
Write-Host "Body:"
Write-Host $response.Content

