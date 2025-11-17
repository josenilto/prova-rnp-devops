#!/bin/bash
# Script para importar dashboard no Grafana via API

GRAFANA_URL="http://localhost:3000"
GRAFANA_USER="admin"
GRAFANA_PASS="admin"
DASHBOARD_FILE="/var/lib/grafana/dashboards/agent-dashboard.json"

# Aguardar Grafana ficar pronto
echo "Aguardando Grafana..."
for i in {1..30}; do
  if curl -s "$GRAFANA_URL/api/health" > /dev/null 2>&1; then
    echo "Grafana OK"
    break
  fi
  sleep 1
done

# Importar dashboard
echo "Importando dashboard..."
curl -X POST "$GRAFANA_URL/api/dashboards/db" \
  -H "Content-Type: application/json" \
  -u "$GRAFANA_USER:$GRAFANA_PASS" \
  -d @"$DASHBOARD_FILE" || echo "Erro ao importar dashboard"

echo "Dashboard importado!"
