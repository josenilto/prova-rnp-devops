# 🚀 QUICK START - PROVA RNP DEVOPS

## ⚡ Acesso Rápido

### Dashboards Grafana
- **Q1 - Web Monitoring:** <http://localhost:3000/d/agent-monitoring>
- **Q2 - ViaIpe Operations:** <http://localhost:3000/d/viaipe-operacional>

### Credenciais Grafana
- **URL:** <http://localhost:3000>
- **User:** `admin`
- **Password:** `admin`

### API InfluxDB
- **URL:** <http://localhost:8086>
- **Database:** `monitoring`

---

## 📊 Status Atual

| Componente | Status | Porta |
|---|---|---|
| InfluxDB | ✅ Running | 8086 |
| Grafana | ✅ Running | 3000 |
| Web Agent (Q1) | ✅ Running | - |
| ViaIpe Agent (Q2) | ✅ Running | - |

---

## 📈 Dados Coletados

### Questão 1: Web Monitoring
- **Alvos:** google.com, youtube.com, rnp.br
- **Métrica Ping:** RTT (ms), Packet Loss (%)
- **Métrica HTTP:** Status Code, Load Time (ms)
- **Intervalo:** 60 segundos
- **Data Points:** 526+

### Questão 2: ViaIpe Statistics
- **API:** <https://legadoviaipe.rnp.br/api/norte>
- **Clientes:** 263
- **Métricas:** Disponibilidade, Banda, Qualidade, Latência
- **Intervalo:** 300 segundos
- **Data Points:** 528+

---

## 🛠️ Comandos Úteis

### Monitorar Logs
```bash
docker-compose logs -f                    # Todos os serviços
docker-compose logs -f web-agent          # Apenas Q1
docker-compose logs -f viaipe-agent       # Apenas Q2
```

### Verificar Status
```bash
docker-compose ps                         # Status dos containers
```

### Parar/Reiniciar
```bash
docker-compose stop                       # Parar
docker-compose up -d                      # Retomar
docker-compose restart <service>          # Reiniciar serviço
```

### Queries InfluxDB
```bash
# Ping RTT (Q1)
docker exec influxdb influx -database monitoring -execute "SELECT * FROM ping ORDER BY time DESC LIMIT 5;"

# HTTP Status (Q1)
docker exec influxdb influx -database monitoring -execute "SELECT * FROM http ORDER BY time DESC LIMIT 5;"

# ViaIpe Agregado (Q2)
docker exec influxdb influx -database monitoring -execute "SELECT * FROM viaipe_agregado ORDER BY time DESC LIMIT 5;"
```

---

## 📂 Arquivos Principais

| Arquivo | Propósito |
|---|---|
| `docker-compose.yml` | Orquestração de 4 containers |
| `agent/monitor.py` | Coleta Q1 (Ping + HTTP) |
| `agent-viaipe/viaipe_collector.py` | Coleta Q2 (ViaIpe API) |
| `README.md` | Documentação completa |
| `ACESSO_DASHBOARDS.md` | Guia de dashboards |
| `IMPLEMENTACAO_CONCLUIDA.txt` | Resumo final |

---

## ✅ Verificação Rápida

```bash
# 1. Todos containers rodando?
docker-compose ps
# Esperado: 4x "Up"

# 2. Dados sendo coletados?
docker-compose logs --tail 5
# Esperado: mensagens de coleta

# 3. Grafana acessível?
curl.exe -s http://localhost:3000 | head -c 100
# Esperado: HTML do Grafana

# 4. InfluxDB tem dados?
docker exec influxdb influx -database monitoring -execute "SELECT COUNT(*) FROM ping; SELECT COUNT(*) FROM viaipe_agregado;"
# Esperado: números > 0
```

---

## 🎯 Próximos Passos

1. **Abrir Grafana:** <http://localhost:3000>
2. **Login:** admin / admin
3. **Ver Dashboard Q1:** <http://localhost:3000/d/agent-monitoring>
4. **Ver Dashboard Q2:** <http://localhost:3000/d/viaipe-operacional>
5. **Explorar dados** nos gráficos interativos

---

## 📞 Troubleshooting Rápido

| Problema | Solução |
|---|---|
| Grafana indisponível | `docker-compose restart grafana` |
| Sem dados | Aguardar 1-2 min, verificar `docker-compose logs` |
| Containers não iniciam | `docker-compose down -v && docker-compose up -d --build` |
| Porta 3000 em uso | `docker-compose stop` e tentar novamente |

---

**Status:** ✅ OPERACIONAL E TESTADO  
**Data:** 17/11/2025  
**Pronto para:** AVALIAÇÃO
