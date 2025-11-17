#!/usr/bin/env python3
"""
Script para validar que as queries do Grafana estão retornando dados corretos
"""
import requests
import json
import sys

INFLUX_URL = "http://127.0.0.1:8086"
DB = "monitoring"

def test_query(name, query):
    """Testa uma query InfluxDB e mostra resultado"""
    url = f"{INFLUX_URL}/query"
    try:
        r = requests.get(url, params={"db": DB, "q": query}, timeout=10)
        r.raise_for_status()
        data = r.json()
        
        result = data.get("results", [{}])[0]
        series = result.get("series")
        
        if series:
            print(f"✅ [{name}] OK - {len(series[0]['values'])} pontos")
            return True
        else:
            print(f"❌ [{name}] Sem dados")
            return False
    except Exception as e:
        print(f"❌ [{name}] Erro: {e}")
        return False

def main():
    print("=" * 60)
    print("Validação de Queries - Dashboard Grafana")
    print("=" * 60)
    
    queries = {
        "Ping RTT (média)": 'SELECT mean("rtt") FROM "ping" WHERE time > now() - 1h GROUP BY time(5m), "host"',
        "HTTP Load Time": 'SELECT mean("load_ms") FROM "http" WHERE time > now() - 1h GROUP BY time(5m), "host"',
        "Packet Loss": 'SELECT mean("loss") FROM "ping" WHERE time > now() - 1h GROUP BY time(5m), "host"',
        "Last HTTP Status": 'SELECT last("status") FROM "http" WHERE time > now() - 1h GROUP BY "host"',
    }
    
    results = []
    for name, query in queries.items():
        ok = test_query(name, query)
        results.append(ok)
    
    print("=" * 60)
    if all(results):
        print("✅ Todas as queries estão retornando dados!")
        return 0
    else:
        print("❌ Algumas queries não retornaram dados")
        return 1

if __name__ == "__main__":
    sys.exit(main())
