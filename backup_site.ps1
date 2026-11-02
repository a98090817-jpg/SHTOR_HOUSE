$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

$pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
if ($pythonCommand) {
    $pythonPath = $pythonCommand.Source
} else {
    $pythonPath = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python311\python.exe'
}

if (-not (Test-Path $pythonPath)) {
    throw "Python executable not found: $pythonPath"
}

& $pythonPath manage.py backup_site
if ($LASTEXITCODE -ne 0) {
    throw "Site backup failed with exit code $LASTEXITCODE."
}
