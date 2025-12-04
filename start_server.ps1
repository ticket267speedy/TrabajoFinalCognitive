# Start server as background Job and show health
Set-Location -LiteralPath (Split-Path -Path $MyInvocation.MyCommand.Definition -Parent)
# Stop existing job named flaskRun if exists
if (Get-Job -Name flaskRun -ErrorAction SilentlyContinue) {
    Stop-Job -Name flaskRun -Force -ErrorAction SilentlyContinue
    Remove-Job -Name flaskRun -Force -ErrorAction SilentlyContinue
}
# Load .env GOOGLE_API_KEY and OPENAI_API_KEY into env for the job
$envfile = Join-Path (Get-Location) '.env'
if (Test-Path $envfile) {
    Get-Content $envfile | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)\s*=\s*(.*)') {
            $k = $matches[1].Trim()
            $v = $matches[2].Trim().Trim('"')
            if ($k -and $v) { Set-Item -Path Env:\$k -Value $v }
        }
    }
}

# Start job
Start-Job -Name flaskRun -ScriptBlock {
    Set-Location $using:PWD
    # Ensure virtualenv python is used
    $python = Join-Path $PWD '.venv\Scripts\python.exe'
    if (Test-Path $python) { & $python run.py } else { & python run.py }
} | Out-Null
Start-Sleep -Seconds 2
Write-Host 'Job started. Checking /health...'
try {
    $r = Invoke-RestMethod -Uri 'http://127.0.0.1:7000/health' -TimeoutSec 5
    Write-Host "HEALTH: $($r | ConvertTo-Json -Compress)"
} catch {
    Write-Host "Health check failed: $($_.Exception.Message)"
}
Write-Host 'To view logs: Receive-Job -Name flaskRun -Keep | Select-Object -Last 200'
Write-Host 'To stop: .\stop_server.ps1'