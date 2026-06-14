# CareerCompass - launch app (run after setup.ps1)
# Usage: .\run_app.ps1

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "ERROR: Virtual environment not found." -ForegroundColor Red
    Write-Host "Run setup first: .\setup.ps1" -ForegroundColor Yellow
    exit 1
}

function Import-CareerCompassSecrets {
    param([string]$SecretsPath)

    if (-not (Test-Path $SecretsPath)) {
        return $false
    }

    $raw = Get-Content -Raw -Path $SecretsPath
    $loaded = $false

    if ($raw -match 'USAJOBS_API_KEY\s*=\s*"([^"]+)"') {
        $env:USAJOBS_API_KEY = $Matches[1]
        $loaded = $true
    }
    if ($raw -match 'USAJOBS_USER_EMAIL\s*=\s*"([^"]+)"') {
        $env:USAJOBS_USER_EMAIL = $Matches[1]
        $loaded = $true
    }

    return ($env:USAJOBS_API_KEY -and $env:USAJOBS_USER_EMAIL)
}

Get-ChildItem -Path $ProjectRoot -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Syncing latest app files from GitHub..." -ForegroundColor Cyan
if (Test-Path (Join-Path $ProjectRoot ".git")) {
    git -C $ProjectRoot fetch origin main 2>$null
    if ($LASTEXITCODE -eq 0) {
        git -C $ProjectRoot checkout origin/main -- app src/cv_upload_ui.py src/ui_theme.py src/_repair/ui_theme.py 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "App pages synced from origin/main" -ForegroundColor Green
        } else {
            Write-Host "WARNING: Could not sync from origin/main. Run: git fetch origin main && git reset --hard origin/main" -ForegroundColor Yellow
        }
    }
}

Write-Host "Repairing source files..." -ForegroundColor Cyan
& $VenvPython scripts/emergency_repair.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Emergency repair failed. Run: python scripts/emergency_repair.py" -ForegroundColor Red
    exit $LASTEXITCODE
}

$SecretsFile = Join-Path $ProjectRoot ".streamlit\secrets.toml"
$env:STREAMLIT_SECRETS_FILE = $SecretsFile
if (Import-CareerCompassSecrets $SecretsFile) {
    Write-Host "USAJobs credentials loaded from $SecretsFile" -ForegroundColor Green
} else {
    Write-Host "WARNING: Could not load USAJobs credentials from $SecretsFile" -ForegroundColor Yellow
    Write-Host "Create the file with quoted USAJOBS_API_KEY and USAJOBS_USER_EMAIL values." -ForegroundColor Yellow
}

Write-Host "Verifying CareerCompass..." -ForegroundColor Cyan
& $VenvPython scripts/verify_app_startup.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Fix the errors above, then run .\setup.ps1" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "Bootstrapping secrets..." -ForegroundColor Cyan
& $VenvPython scripts/bootstrap_secrets.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "USAJobs bootstrap failed. Data Import connector may use demo data until secrets are fixed." -ForegroundColor Yellow
}

Write-Host "Checking CV upload dependencies..." -ForegroundColor Cyan
& $VenvPython -c "import pypdf; import docx"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing pypdf and python-docx for CV/resume upload..." -ForegroundColor Yellow
    & $VenvPython -m pip install pypdf python-docx
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install CV upload packages." -ForegroundColor Red
        exit 1
    }
}

Write-Host "Starting Streamlit at http://localhost:8501" -ForegroundColor Green
& $VenvPython -m streamlit run app/streamlit_app.py
