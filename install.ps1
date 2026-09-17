# Installation sur Windows (PowerShell).
# Execution : clic droit sur install.ps1 > Executer avec PowerShell
# ou depuis un terminal : powershell -ExecutionPolicy Bypass -File install.ps1

Write-Host "== Installation du bot (Windows) ==" -ForegroundColor Cyan

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python n'est pas installe ou n'est pas dans le PATH." -ForegroundColor Red
    Write-Host "Installe-le depuis https://www.python.org/downloads/ (coche 'Add Python to PATH')."
    exit 1
}

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Fichier .env cree a partir de .env.example - remplis-le avant de lancer le bot." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Installation terminee." -ForegroundColor Green
Write-Host "Pour lancer le bot :"
Write-Host "  .\venv\Scripts\Activate.ps1"
Write-Host "  python main.py"
