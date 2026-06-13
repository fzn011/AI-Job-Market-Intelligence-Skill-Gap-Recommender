# CareerCompass — one-command Windows setup
# Usage (PowerShell):
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned   # first time only
#   .\setup.ps1
#   .\setup.ps1 -RunApp

param(
    [switch]$RunApp,
    [switch]$SkipHeavyPackages
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " CareerCompass Windows Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$RequiredScripts = @(
    "scripts\generate_career_taxonomies.py",
    "scripts\generate_advanced_features_data.py",
    "scripts\generate_premium_features_data.py",
    "scripts\run_project_check.py"
)
$MissingScripts = @($RequiredScripts | Where-Object { -not (Test-Path (Join-Path $ProjectRoot $_)) })
if ($MissingScripts.Count -gt 0) {
    Write-Host "ERROR: This folder is missing CareerCompass files:" -ForegroundColor Red
    foreach ($item in $MissingScripts) { Write-Host "  - $item" -ForegroundColor Red }
    Write-Host ""
    Write-Host "Your git pull likely failed due to local changes. Run:" -ForegroundColor Yellow
    Write-Host "  git fetch origin main" -ForegroundColor White
    Write-Host "  git reset --hard origin/main" -ForegroundColor White
    Write-Host "  .\setup.ps1 -RunApp" -ForegroundColor White
    Write-Host ""
    Write-Host "Or stash local edits first: git stash push -u -m backup" -ForegroundColor DarkYellow
    exit 1
}

function Find-Python {
    $candidates = @("python", "py", "python3")
    foreach ($cmd in $candidates) {
        try {
            $version = & $cmd --version 2>&1
            if ($LASTEXITCODE -eq 0 -and $version -match "Python 3\.(1[1-9]|[2-9][0-9])") {
                return $cmd
            }
        } catch {}
    }
    return $null
}

$Python = Find-Python
if (-not $Python) {
    Write-Host "ERROR: Python 3.11+ not found." -ForegroundColor Red
    Write-Host "Install from https://www.python.org/downloads/ and enable 'Add to PATH'." -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/7] Using: $Python" -ForegroundColor Green
& $Python --version

$VenvPath = Join-Path $ProjectRoot ".venv"
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "[2/7] Creating virtual environment..." -ForegroundColor Yellow
    & $Python -m venv $VenvPath
} else {
    Write-Host "[2/7] Virtual environment already exists." -ForegroundColor Green
}

Write-Host "[3/7] Upgrading pip..." -ForegroundColor Yellow
& $VenvPython -m pip install --upgrade pip setuptools wheel

Write-Host "[4/7] Installing dependencies (this may take several minutes)..." -ForegroundColor Yellow
if ($SkipHeavyPackages) {
    Write-Host "      Lightweight mode: skipping sentence-transformers download hint." -ForegroundColor DarkYellow
    & $VenvPython -m pip install pandas numpy scikit-learn plotly streamlit pyyaml python-dotenv pytest reportlab joblib matplotlib
} else {
    & $VenvPython -m pip install -r requirements.txt
}

Write-Host "[5/7] Generating career data files..." -ForegroundColor Yellow
& $VenvPython scripts/generate_career_taxonomies.py
& $VenvPython scripts/generate_advanced_features_data.py
& $VenvPython scripts/generate_premium_features_data.py

Write-Host "[6/7] Running health check..." -ForegroundColor Yellow
& $VenvPython scripts/run_project_check.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Health check reported issues. Review output above." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "[7/7] Optional: import expanded demo jobs..." -ForegroundColor Yellow
& $VenvPython scripts/import_jobs_from_csv.py --demo expanded

$SecretsExample = Join-Path $ProjectRoot ".streamlit\secrets.example.toml"
$SecretsFile = Join-Path $ProjectRoot ".streamlit\secrets.toml"
if ((Test-Path $SecretsExample) -and -not (Test-Path $SecretsFile)) {
    Copy-Item $SecretsExample $SecretsFile
    Write-Host "Created .streamlit\secrets.toml from example — add USAJobs/SMTP keys if needed." -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Setup complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Activate the environment:" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Start the app:" -ForegroundColor Cyan
Write-Host "  python -m streamlit run app/streamlit_app.py" -ForegroundColor White
Write-Host ""

if ($RunApp) {
    Write-Host "Starting Streamlit..." -ForegroundColor Green
    & $VenvPython -m streamlit run app/streamlit_app.py
}
