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

Get-ChildItem -Path $ProjectRoot -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Repairing source files..." -ForegroundColor Cyan
& $VenvPython scripts/emergency_repair.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Emergency repair failed. Run: python scripts/emergency_repair.py" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "Verifying CareerCompass..." -ForegroundColor Cyan
& $VenvPython scripts/verify_app_startup.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Fix the errors above, then run .\setup.ps1" -ForegroundColor Red
    exit $LASTEXITCODE
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
