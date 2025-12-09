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

# 2) Upload to Flask/TAG backend using curl.exe (avoids Invoke-WebRequest -Form compatibility issues)
$buildId = if ($env:BUILD_TAG) { $env:BUILD_TAG } else { "manual-$([guid]::NewGuid().ToString())" }

Write-Host "Uploading Allure results to $REPORT_UPLOAD_URL ..."

$curlArgs = @(
    "-sS",
    "-X", "POST", $REPORT_UPLOAD_URL,
    "-H", "Authorization: Bearer $REPORT_API_TOKEN",
    "-F", "project=$REPORT_PROJECT",
    "-F", "environment=$REPORT_ENV",
    "-F", "build_id=$buildId",
    "-F", "executed_by=jenkins",
    "-F", "file=@$zipPath"
)

try {
    # Explicitly call curl.exe to avoid PowerShell's curl alias
    $process = Start-Process -FilePath "curl.exe" -ArgumentList $curlArgs -NoNewWindow -RedirectStandardOutput "curl_output.txt" -RedirectStandardError "curl_error.txt" -PassThru -Wait

    Write-Host "curl exit code: $($process.ExitCode)"
    Write-Host "Response:"
    if (Test-Path "curl_output.txt") {
        Get-Content "curl_output.txt" | ForEach-Object { Write-Host $_ }
    }
    if ($process.ExitCode -ne 0 -and (Test-Path "curl_error.txt")) {
        Write-Host "curl errors:"
        Get-Content "curl_error.txt" | ForEach-Object { Write-Host $_ }
        exit $process.ExitCode
    }
} catch {
    Write-Error "Failed to invoke curl.exe: $_"
    exit 1
}
