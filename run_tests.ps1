$msgs = @(
  'Responde solo: OK',
  '¿Cómo agrego un estudiante al curso?',
  '¿Qué hago si la cámara no reconoce a un estudiante?',
  'Hola',
  '¿Cuál es la capital de Francia?'
)

foreach ($m in $msgs) {
  $body = @{ message = $m; role = 'profesor' } | ConvertTo-Json -Compress
  Write-Host "`n==> Pregunta: $m"
  try {
    $r = Invoke-RestMethod -Uri 'http://127.0.0.1:7000/api/chatbot' -Method Post -Body $body -ContentType 'application/json' -TimeoutSec 10
    Write-Host (ConvertTo-Json $r -Depth 4)
  } catch {
    Write-Host "Error en petición: $($_.Exception.Message)"
  }
}
