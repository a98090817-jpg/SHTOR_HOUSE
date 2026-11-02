param(
    [datetime]$RunAt = [datetime]::Today.AddHours(2)
)

$ErrorActionPreference = 'Stop'
$taskName = 'SHTOR HOUSE daily backup'
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    throw "Scheduled task '$taskName' already exists. It was left unchanged."
}

$backupScript = Join-Path $PSScriptRoot 'backup_site.ps1'
$action = New-ScheduledTaskAction `
    -Execute 'powershell.exe' `
    -Argument ('-NoProfile -ExecutionPolicy Bypass -File "{0}"' -f $backupScript)
$trigger = New-ScheduledTaskTrigger -Daily -At $RunAt
$principal = New-ScheduledTaskPrincipal `
    -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) `
    -LogonType Interactive `
    -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Description 'Creates a daily local SQLite and media backup for SHTOR HOUSE.' | Out-Null

Write-Host "Registered '$taskName' to run daily at $($RunAt.ToString('HH:mm'))."
