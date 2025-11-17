import requests
import sys

INFLUX = 'http://localhost:8086'
DB = 'monitoring'

queries = {
    'ping': 'SELECT count("rtt") FROM "ping" WHERE time > now() - 5m',
    'http': 'SELECT count("status") FROM "http" WHERE time > now() - 5m',
}

def run_query(q):
    url = f"{INFLUX}/query"
    try:
        r = requests.get(url, params={'db': DB, 'q': q}, timeout=10)
        r.raise_for_status()
        j = r.json()
        res = j.get('results', [])[0]
        series = res.get('series')
        if not series:
            return 0
        return series[0]['values'][0][1]
    except Exception as e:
        print('Erro ao consultar InfluxDB:', e)
        return None

def main():
    ok = True
    for k, q in queries.items():
        val = run_query(q)
        if val is None:
            ok = False
            print(f'[{k}] Erro na consulta')
        else:
            print(f'[{k}] Pontos nos últimos 5 minutos: {val}')
            if val == 0:
                ok = False

    if ok:
        print('Verificação OK: métricas chegando.')
        sys.exit(0)
    else:
        print('Verificação falhou: revisar logs e agentes.')
        sys.exit(1)

if __name__ == "__main__":
    main()
