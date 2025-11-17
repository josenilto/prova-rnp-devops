# 🎯 GUIA DE ACESSO - DASHBOARDS GRAFANA

## Informações de Login

- **URL:** <http://localhost:3000>
- **Usuário:** admin
- **Senha:** admin

---

## Dashboard 1: Agent Monitoring (Questão 1)

### URL Direta

<http://localhost:3000/d/agent-monitoring>

### Painéis Disponíveis

1. **Ping RTT (ms)** — Latência de resposta por host
   - Mostra: google.com, youtube.com, rnp.br
   - Unidade: Milissegundos
   - Tipo: Timeseries

2. **HTTP Load Time (ms)** — Tempo de carregamento das páginas
   - Mostra: google.com, youtube.com, rnp.br
   - Unidade: Milissegundos
   - Tipo: Timeseries

3. **Packet Loss (%)** — Perda de pacotes ao longo do tempo
   - Mostra: Tendência de perda de pacotes
   - Unidade: Percentual
   - Tipo: Timeseries

4. **Last HTTP Status** — Últimos códigos de status HTTP coletados
   - Mostra: Status codes (200, 404, etc)
   - Tipo: Gauge

### Período de Atualização

- Dashboard atualiza a cada 30 segundos
- Dados mostram as últimas 1 hora
- Agente coleta a cada 60 segundos

### Exemplo de Dados Esperados

```text
google.com:   RTT=5-10ms, Status=200, Load=500ms
youtube.com:  RTT=5-10ms, Status=200, Load=450ms
rnp.br:       RTT=5-10ms, Status=200, Load=600ms
```

---

## Dashboard 2: ViaIpe - Operações Norte (Questão 2)

### URL Direta

<http://localhost:3000/d/viaipe-operacional>

### Painéis Disponíveis

1. **Disponibilidade Média de Clientes (%)** — Percentual de disponibilidade regional
   - Mostra: Tendência de disponibilidade
   - Unidade: Percentual
   - Tipo: Timeseries
   - Esperado: 99-100%

2. **Consumo Médio de Banda (Mbps)** — Uso de largura de banda regional
   - Mostra: Banda média em Mbps
   - Unidade: Mbps
   - Tipo: Timeseries
   - Esperado: 10-20 Mbps

3. **Qualidade Média (Latência ms)** — Latência média da região
   - Mostra: Latência ao longo do tempo
   - Unidade: Milissegundos
   - Tipo: Timeseries
   - Esperado: 5-10 ms

4. **Total de Clientes Monitorados** — Contagem de clientes ativos
   - Mostra: Número de pontos de presença
   - Tipo: Gauge
   - Esperado: 260-270 clientes

### Período de Atualização

- Dashboard atualiza a cada 30 segundos
- Dados mostram as últimas 1 hora
- Agente coleta a cada 300 segundos (5 minutos)

### Exemplo de Dados Esperados

```text
Disponibilidade:     99.93%
Banda Média:         14.15 MB/s
Latência Média:      6.36 ms
Total de Clientes:   263
Perda de Pacotes:    0.067%
```

---

## Navegação entre Dashboards

### Método 1: Menu Lateral

1. Clique no ícone de menu (≡) no canto superior esquerdo
2. Selecione "Dashboards"
3. Escolha entre "Agent Monitoring" ou "ViaIpe - Operações Norte"

### Método 2: URLs Diretas

- Q1: <http://localhost:3000/d/agent-monitoring>
- Q2: <http://localhost:3000/d/viaipe-operacional>

### Método 3: Home Screen

1. Clique no logo do Grafana no canto superior esquerdo
2. Selecione o dashboard desejado

---

## Customização dos Dashboards

### Alterar Período de Tempo

1. Clique em "Last 1 hour" (canto superior direito)
2. Selecione o período desejado (5m, 30m, 1h, 6h, 24h, etc)

### Pausar Atualização Automática

1. Clique em "30s" (canto superior direito, próximo ao relógio)
2. Desative "Auto" para pausar

### Exportar Dados

1. Clique em "..." (canto superior direito do painel)
2. Selecione "More" → "Export"

### Compartilhar Dashboard

1. Clique em "Share" (canto superior direito)
2. Copie a URL ou gere um link compartilhado

---

## Troubleshooting

### Dados Não Aparecem

```powershell
# Verificar se agente está coletando
docker-compose logs web-agent
docker-compose logs viaipe-agent

# Verificar se InfluxDB tem dados
docker exec influxdb influx -database monitoring -execute "SELECT COUNT(*) FROM ping; SELECT COUNT(*) FROM viaipe_agregado;"
```

### Dashboard Carrega Devagar

- Reduzir período de tempo visualizado
- Fechar outros dashboards abertos
- Verificar saúde do InfluxDB

### Grafana Inacessível

```powershell
# Reiniciar Grafana
docker-compose restart grafana

# Verificar logs
docker-compose logs grafana
```

---

## Dados em Tempo Real no InfluxDB

### Via Terminal

```powershell
# Últimas medições de ping (Q1)
docker exec influxdb influx -database monitoring -execute "SELECT * FROM ping ORDER BY time DESC LIMIT 5;"

# Últimas medições HTTP (Q1)
docker exec influxdb influx -database monitoring -execute "SELECT * FROM http ORDER BY time DESC LIMIT 5;"

# Últimas agregações ViaIpe (Q2)
docker exec influxdb influx -database monitoring -execute "SELECT * FROM viaipe_agregado ORDER BY time DESC LIMIT 5;"
```

### Via API InfluxDB

```powershell
# Query ping
curl.exe -s "http://localhost:8086/query?db=monitoring&q=SELECT * FROM ping LIMIT 5"

# Query HTTP
curl.exe -s "http://localhost:8086/query?db=monitoring&q=SELECT * FROM http LIMIT 5"

# Query ViaIpe agregado
curl.exe -s "http://localhost:8086/query?db=monitoring&q=SELECT * FROM viaipe_agregado LIMIT 5"
```

---

## Observações Finais

- Ambos os dashboards estão pré-configurados e funcionando
- Dados são coletados continuamente pelos agentes
- Histórico completo armazenado no InfluxDB
- É possível fazer drill-down nos gráficos para ver mais detalhes
- Tooltips aparecem ao passar o mouse nos pontos de dados

**Última atualização:** 17/11/2025  
**Status:** ✅ OPERACIONAL
