# CareerCompass - one-command Windows setup
# Usage (PowerShell):
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned   # first time only
#   .\setup.ps1
#   .\setup.ps1 -RunApp
#   .\setup.ps1 -SkipHeavyPackages
#   .\setup.ps1 -RepairRepo

param(
    [switch]$RunApp,
    [switch]$SkipHeavyPackages,
    [switch]$RepairRepo
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " CareerCompass Windows Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

function Clear-PythonCache {
    Get-ChildItem -Path $ProjectRoot -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}

function Test-RepoUpToDate {
    $UiThemePath = Join-Path $ProjectRoot "src\ui_theme.py"
    $AppPath = Join-Path $ProjectRoot "app\streamlit_app.py"
    $SetupPath = Join-Path $ProjectRoot "setup.ps1"

    if (-not (Test-Path $UiThemePath)) {
        Write-Host "ERROR: Missing src\ui_theme.py" -ForegroundColor Red
        return $false
    }
    if (-not (Select-String -Path $UiThemePath -Pattern 'render_feature_card' -Quiet)) {
        Write-Host "ERROR: src\ui_theme.py is outdated (missing render_feature_card)." -ForegroundColor Red
        return $false
    }
    if (-not (Test-Path (Join-Path $ProjectRoot "src\brand_constants.py"))) {
        Write-Host "ERROR: Missing src\brand_constants.py" -ForegroundColor Red
        return $false
    }
    if (-not (Select-String -Path $AppPath -Pattern 'CareerCompass' -Quiet)) {
        Write-Host "ERROR: app\streamlit_app.py is outdated." -ForegroundColor Red
        return $false
    }
    if (-not (Test-Path $SetupPath)) {
        Write-Host "ERROR: setup.ps1 missing from project root." -ForegroundColor Red
        return $false
    }
    return $true
}

function Repair-RepoFromOrigin {
    Write-Host "Repairing repo from origin/main..." -ForegroundColor Yellow
    git fetch origin main
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: git fetch failed. Check your internet and git remote." -ForegroundColor Red
        return $false
    }
    git reset --hard origin/main
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: git reset failed." -ForegroundColor Red
        return $false
    }
    Clear-PythonCache
    return $true
}

$RequiredScripts = @(
    "scripts\generate_career_taxonomies.py",
    "scripts\generate_advanced_features_data.py",
    "scripts\generate_premium_features_data.py",
    "scripts\run_project_check.py",
    "scripts\verify_app_startup.py",
    "scripts\emergency_repair.py",
    "scripts\import_jobs_from_csv.py"
)
$MissingScripts = @($RequiredScripts | Where-Object { -not (Test-Path (Join-Path $ProjectRoot $_)) })
if ($MissingScripts.Count -gt 0 -or -not (Test-RepoUpToDate)) {
    Write-Host "ERROR: This folder is missing CareerCompass files or has an outdated checkout." -ForegroundColor Red
    if ($MissingScripts.Count -gt 0) {
        foreach ($item in $MissingScripts) { Write-Host "  - $item" -ForegroundColor Red }
    }
    Write-Host ""
    Write-Host "Attempting automatic repair from GitHub main..." -ForegroundColor Yellow
    if (-not (Repair-RepoFromOrigin)) {
        Write-Host "Manual fix:" -ForegroundColor Yellow
        Write-Host "  git fetch origin main" -ForegroundColor White
        Write-Host "  git reset --hard origin/main" -ForegroundColor White
        Write-Host "  .\setup.ps1 -RunApp" -ForegroundColor White
        exit 1
    }
    $MissingScripts = @($RequiredScripts | Where-Object { -not (Test-Path (Join-Path $ProjectRoot $_)) })
    if ($MissingScripts.Count -gt 0 -or -not (Test-RepoUpToDate)) {
        Write-Host "ERROR: Repair completed but files are still missing." -ForegroundColor Red
        exit 1
    }
    Write-Host "Repair OK." -ForegroundColor Green
}

if ($RepairRepo) {
    if (Repair-RepoFromOrigin) {
        Write-Host "Repo repaired. Run .\setup.ps1 -RunApp to finish setup." -ForegroundColor Green
    }
    exit 0
}

Clear-PythonCache

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
    Write-Host "Install from https://www.python.org/downloads/ and enable Add to PATH." -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/9] Using: $Python" -ForegroundColor Green
& $Python --version

Write-Host "[2/9] Repairing outdated source files..." -ForegroundColor Yellow
& $Python scripts/emergency_repair.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Emergency repair failed." -ForegroundColor Red
    exit 1
}

$VenvPath = Join-Path $ProjectRoot ".venv"
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "[3/9] Creating virtual environment..." -ForegroundColor Yellow
    & $Python -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create venv. Close other Python/Streamlit windows and retry." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[3/9] Virtual environment already exists." -ForegroundColor Green
}

Write-Host "[4/9] Upgrading pip..." -ForegroundColor Yellow
& $VenvPython -m pip install --upgrade pip setuptools wheel

Write-Host "[5/9] Installing dependencies (this may take several minutes)..." -ForegroundColor Yellow
if ($SkipHeavyPackages) {
    Write-Host "      Lightweight mode: skipping sentence-transformers." -ForegroundColor DarkYellow
    & $VenvPython -m pip install pandas numpy scikit-learn plotly streamlit pyyaml python-dotenv pytest reportlab joblib matplotlib requests pypdf python-docx
} else {
    & $VenvPython -m pip install -r requirements.txt
}
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pip install failed. Try: .\setup.ps1 -SkipHeavyPackages" -ForegroundColor Red
    exit 1
}

Write-Host "[6/9] Generating career data files..." -ForegroundColor Yellow
& $VenvPython scripts/generate_career_taxonomies.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $VenvPython scripts/generate_advanced_features_data.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $VenvPython scripts/generate_premium_features_data.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[7/9] Running health check..." -ForegroundColor Yellow
& $VenvPython scripts/run_project_check.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Health check reported issues. Review output above." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "[8/9] Importing expanded demo jobs (optional)..." -ForegroundColor Yellow
& $VenvPython scripts/import_jobs_from_csv.py --demo expanded
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Demo import failed. Core app will still run with sample data." -ForegroundColor DarkYellow
}

$SecretsExample = Join-Path $ProjectRoot ".streamlit\secrets.example.toml"
$SecretsFile = Join-Path $ProjectRoot ".streamlit\secrets.toml"
if ((Test-Path $SecretsExample) -and -not (Test-Path $SecretsFile)) {
    Copy-Item $SecretsExample $SecretsFile
    Write-Host "Created .streamlit\secrets.toml from example - add your USAJobs key and email." -ForegroundColor DarkYellow
    Write-Host "  Path: $SecretsFile" -ForegroundColor DarkYellow
}

Write-Host "[9/9] Verifying app startup..." -ForegroundColor Yellow
Clear-PythonCache
& $VenvPython scripts/verify_app_startup.py
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Setup complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Start the app:" -ForegroundColor Cyan
Write-Host "  .\run_app.ps1" -ForegroundColor White
Write-Host "  python -m streamlit run app/streamlit_app.py" -ForegroundColor White
Write-Host ""

if ($RunApp) {
    & $VenvPython -m streamlit run app/streamlit_app.py
}
