Set-Location $PSScriptRoot
python -m pip install -r requirements.txt -q
$port = 8001
if (netstat -ano | Select-String ":8001\s" | Select-String "LISTENING") {
    Write-Host "Puerto 8001 ocupado. Usando 8011..." -ForegroundColor Yellow
    $port = 8011
}
Write-Host "RAG base (sin IA): http://127.0.0.1:$port" -ForegroundColor Green
Write-Host "API:             http://127.0.0.1:$port/docs" -ForegroundColor Gray
python -m uvicorn app:app --reload --port $port
