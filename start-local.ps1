param([int]$Port = 5190)
$ErrorActionPreference = 'Stop'
if ($env:DB_NAME -or ($env:APP_ENV -and $env:APP_ENV -ne 'development')) {
    throw 'Use a development-only terminal without staging/production database environment variables.'
}
Set-Location -LiteralPath $PSScriptRoot
if (!(Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
    py -3 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.12 or newer first.' }
    & './.venv/Scripts/python.exe' -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
}
$env:APP_ENV = 'development'
& './.venv/Scripts/python.exe' manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) { throw 'Migration failed.' }
Write-Host "Open http://127.0.0.1:$Port/ (HTTP for local development)"
& './.venv/Scripts/python.exe' manage.py runserver "127.0.0.1:$Port"
