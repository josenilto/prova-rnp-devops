param(
    [string]$InfluxUrl = 'http://localhost:8086',
    [string]$Db = 'monitoring'
)

Write-Host "Verificando InfluxDB em $InfluxUrl, DB: $Db"

$queries = @{
    ping = "SELECT count(\"rtt\") FROM \"ping\" WHERE time > now() - 5m";
    http = "SELECT count(\"status\") FROM \"http\" WHERE time > now() - 5m";
}

$ok = $true
foreach ($k in $queries.Keys) {
    $q = $queries[$k]
    $uri = "$InfluxUrl/query?db=$Db&q=$( [uri]::EscapeDataString($q) )"
    try {
        $resp = Invoke-RestMethod -Uri $uri -Method Get -TimeoutSec 10
        $series = $resp.results[0].series
        if ($null -eq $series) {
            Write-Host "[$k] Nenhuma série retornada (0)" -ForegroundColor Yellow
            $count = 0
        } else {
            $count = $series[0].values[0][1]
            Write-Host "[$k] Pontos nos últimos 5 minutos: $count" -ForegroundColor Green
        }
        if ($count -eq 0) { $ok = $false }
    } catch {
        Write-Host "Erro ao consultar InfluxDB: $_" -ForegroundColor Red
        $ok = $false
    }
}

if ($ok) { Write-Host "Verificação OK: métricas chegando." -ForegroundColor Green; exit 0 } else { Write-Host "Verificação falhou: revisar logs e agentes." -ForegroundColor Red; exit 1 }
