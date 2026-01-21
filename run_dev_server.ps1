# Quick script to run the development server
Write-Host "Starting Django development server..." -ForegroundColor Green
Write-Host ""
Write-Host "Make sure you are on the development branch!" -ForegroundColor Yellow
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Activate virtual environment and run server
& ".\venv\Scripts\Activate.ps1"
python manage.py runserver
