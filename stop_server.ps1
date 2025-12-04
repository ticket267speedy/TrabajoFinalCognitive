# Stop the flaskRun job if running
if (Get-Job -Name flaskRun -ErrorAction SilentlyContinue) {
    Stop-Job -Name flaskRun -Force -ErrorAction SilentlyContinue
    Remove-Job -Name flaskRun -Force -ErrorAction SilentlyContinue
    Write-Host 'flaskRun stopped.'
} else {
    Write-Host 'No flaskRun job found.'
}