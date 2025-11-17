import subprocess
import requests
import time
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

TARGETS = ["google.com", "youtube.com", "rnp.br"]
# Usa IPv4 para evitar problemas com WSL Relay/IPv6
INFLUX_URL = os.environ.get('INFLUXDB_URL', 'http://127.0.0.1:8086')
INFLUX_DB = os.environ.get('INFLUXDB_DB', 'monitoring')
INTERVAL = int(os.environ.get('INTERVAL', '60'))


def create_db():
    url = f"{INFLUX_URL}/query"
    try:
        logging.info('Criando database se não existir')
        r = requests.get(url, params={'q': f'CREATE DATABASE {INFLUX_DB}'}, timeout=5)
        logging.debug('create_db response: %s', r.text)
    except Exception as e:
        logging.warning('Erro ao criar DB: %s', e)


def write_point(measurement, tags, fields, timestamp=None):
    # line protocol
    tag_str = ','.join([f"{k}={v}" for k, v in tags.items()]) if tags else ''
    field_parts = []
    for k, v in fields.items():
        if isinstance(v, int):
            field_parts.append(f"{k}={v}i")
        elif isinstance(v, float):
            field_parts.append(f"{k}={v}")
        elif v is None:
            continue
        else:
            # string field
            field_parts.append(f'{k}="{v}"')
    field_str = ','.join(field_parts)
    if tag_str:
        line = f"{measurement},{tag_str} {field_str}"
    else:
        line = f"{measurement} {field_str}"
    if timestamp:
        line = f"{line} {timestamp}"

    url = f"{INFLUX_URL}/write"
    params = {'db': INFLUX_DB}
    try:
        r = requests.post(url, params=params, data=line, timeout=5)
        if r.status_code not in (204,):
            logging.warning('Influx write failed: %s %s', r.status_code, r.text)
    except Exception as e:
        logging.warning('Erro ao gravar no InfluxDB: %s', e)


def parse_ping_output(output):
    # busca perda e rtt médio (linux)
    loss = None
    rtt = None
    for line in output.splitlines():
        if 'packet loss' in line:
            try:
                parts = line.split(',')
                for p in parts:
                    if '%' in p and 'loss' in p or '%' in p:
                        loss = float(p.strip().split('%')[0])
            except Exception:
                pass
        if 'rtt min/avg' in line or 'rtt min/avg/max' in line or 'round-trip' in line:
            # rtt min/avg/max/mdev = 9.123/12.345/15.678/1.234 ms
            try:
                right = line.split('=')[1].strip()
                vals = right.split(' ')[0].split('/')
                if len(vals) >= 2:
                    rtt = float(vals[1])
            except Exception:
                pass
    return rtt, loss


def do_ping(host):
    try:
        proc = subprocess.run(['ping', '-c', '4', host], capture_output=True, text=True, timeout=15)
        out = proc.stdout + '\n' + proc.stderr
        rtt, loss = parse_ping_output(out)
        return rtt, loss
    except Exception as e:
        logging.warning('Ping falhou para %s: %s', host, e)
        return None, 100.0


def do_http(host):
    url = f"https://{host}"
    try:
        start = time.time()
        r = requests.get(url, timeout=10)
        elapsed = (time.time() - start) * 1000.0
        return r.status_code, elapsed
    except Exception as e:
        logging.warning('HTTP falhou para %s: %s', host, e)
        return None, None


def main():
    logging.info('Agent iniciado. Influx: %s DB: %s', INFLUX_URL, INFLUX_DB)
    # tenta criar DB
    create_db()
    while True:
        now_ns = int(time.time() * 1e9)
        for host in TARGETS:
            rtt, loss = do_ping(host)
            tags = {'host': host}
            fields = {}
            if rtt is not None:
                fields['rtt'] = float(rtt)
            if loss is not None:
                try:
                    fields['loss'] = int(loss)
                except Exception:
                    fields['loss'] = int(float(loss))
            write_point('ping', tags, fields, timestamp=now_ns)

            status, load_ms = do_http(host)
            http_fields = {}
            if status is not None:
                http_fields['status'] = int(status)
            if load_ms is not None:
                http_fields['load_ms'] = float(load_ms)
            write_point('http', tags, http_fields, timestamp=now_ns)

            logging.info('Host %s: ping rtt=%s loss=%s | http status=%s load_ms=%s', host, rtt, loss, status, load_ms)

        time.sleep(INTERVAL)


if __name__ == '__main__':
    main()
