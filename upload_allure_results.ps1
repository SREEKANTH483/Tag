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

# Prefer to hard-code the token (must match ALLURE_UPLOAD_TOKEN in .env)
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

# 2) Upload to Flask/TAG backend using .NET HttpClient (robust multipart/form-data)
$buildId = if ($env:BUILD_TAG) { $env:BUILD_TAG } else { "manual-$([guid]::NewGuid().ToString())" }

Write-Host "Uploading Allure results to $REPORT_UPLOAD_URL ..."

try {
    Add-Type -AssemblyName System.Net.Http | Out-Null

    $handler = New-Object System.Net.Http.HttpClientHandler
    $client  = New-Object System.Net.Http.HttpClient($handler)
    $client.Timeout = [System.TimeSpan]::FromMinutes(5)

    $client.DefaultRequestHeaders.Clear()
    $client.DefaultRequestHeaders.Add("Authorization", "Bearer $REPORT_API_TOKEN")

    $multipart = New-Object System.Net.Http.MultipartFormDataContent

    $multipart.Add((New-Object System.Net.Http.StringContent($REPORT_PROJECT)), "project")
    $multipart.Add((New-Object System.Net.Http.StringContent($REPORT_ENV)), "environment")
    $multipart.Add((New-Object System.Net.Http.StringContent($buildId)), "build_id")
    $multipart.Add((New-Object System.Net.Http.StringContent("jenkins")), "executed_by")

    $zipFullPath = (Resolve-Path $zipPath).Path
    $fileStream  = [System.IO.File]::OpenRead($zipFullPath)
    $fileContent = New-Object System.Net.Http.StreamContent($fileStream)
    $fileContent.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse("application/zip")
    $multipart.Add($fileContent, "file", "allure-results.zip")

    $response   = $client.PostAsync($REPORT_UPLOAD_URL, $multipart).Result
    $statusCode = [int]$response.StatusCode
    $body       = $response.Content.ReadAsStringAsync().Result

    Write-Host "Status: $statusCode"
    Write-Host "Body:"
    Write-Host $body

    $fileStream.Dispose()
    $fileContent.Dispose()
    $multipart.Dispose()
    $client.Dispose()

    if ($statusCode -ge 400) {
        Write-Error "Upload failed with HTTP status code $statusCode"
        exit 1
    }
} catch {
    Write-Error "Failed to upload Allure results: $_"
    exit 1
}
