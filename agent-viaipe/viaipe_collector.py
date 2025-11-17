import requests
import json
import time
import logging
import os
import warnings
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# Suppress SSL warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

VIAIPE_API_URL = os.environ.get('VIAIPE_API_URL', 'https://legadoviaipe.rnp.br/api/norte')
INFLUX_URL = os.environ.get('INFLUXDB_URL', 'http://influxdb:8086')
INFLUX_DB = os.environ.get('INFLUXDB_DB', 'monitoring')
INTERVAL = int(os.environ.get('INTERVAL', '300'))  # 5 minutos

def create_db():
    """Garantir que o banco existe"""
    url = f"{INFLUX_URL}/query"
    try:
        logger.info('Criando database se não existir')
        r = requests.get(url, params={'q': f'CREATE DATABASE {INFLUX_DB}'}, timeout=5)
        logger.debug('create_db response: %s', r.text)
    except Exception as e:
        logger.warning('Erro ao criar DB: %s', e)

def write_point(measurement, tags, fields, timestamp=None):
    """Escrever ponto no InfluxDB usando Line Protocol"""
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
            logger.warning('Influx write failed: %s %s', r.status_code, r.text)
    except Exception as e:
        logger.warning('Erro ao gravar no InfluxDB: %s', e)

def fetch_viaipe_data():
    """Consumir dados da API do ViaIpe"""
    try:
        logger.info('Consultando API ViaIpe: %s', VIAIPE_API_URL)
        response = requests.get(VIAIPE_API_URL, timeout=30, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error('Erro ao acessar API ViaIpe: %s', e)
        return None

def parse_viaipe_data(data):
    """
    Parse ViaIpe API response (list of client locations with traffic/quality metrics)
    API returns: [
        {
            "id": "client_id",
            "name": "Client Name",
            "lat": "-8.16647",
            "lng": "-70.3516",
            "data": {
                "interfaces": [
                    {
                        "avg_in": 1677674.52,
                        "avg_out": 5972213.53,
                        ...
                    }
                ],
                "smoke": {
                    "loss": 1.27,  (packet loss %)
                    "val": 5.81,   (latency in ms)
                    "avg_val": 5.32,
                    ...
                }
            }
        },
        ...
    ]
    """
    if not data:
        logger.warning('Nenhum dado recebido da API ViaIpe')
        return

    if not isinstance(data, list):
        logger.error(f"API retornou tipo inesperado: {type(data)}, esperado lista")
        return

    try:
        total_disponibilidade = 0
        total_banda = 0
        total_qualidade = 0
        total_loss = 0
        total_clients = len(data)
        
        if total_clients == 0:
            logger.warning('Nenhum cliente encontrado na resposta da API')
            return
        
        logger.info(f"Processando {total_clients} clientes da API ViaIpe")
        
        # Process each client (location)
        for client in data:
            try:
                client_name = client.get('name', client.get('id', 'unknown'))
                client_id = client.get('id', 'unknown')
                
                # Extract interface traffic data
                interfaces = client.get('data', {}).get('interfaces', [])
                smoke_data = client.get('data', {}).get('smoke', {})
                
                if interfaces:
                    # Calculate metrics from interfaces
                    total_traffic_in = sum(float(i.get('avg_in', 0)) for i in interfaces)
                    total_traffic_out = sum(float(i.get('avg_out', 0)) for i in interfaces)
                    total_bandwidth = total_traffic_in + total_traffic_out
                    
                    # Smoke test quality metrics
                    latency = float(smoke_data.get('val', 0))
                    packet_loss = float(smoke_data.get('loss', 0))
                    
                    # Estimate availability (100% - packet_loss%)
                    disponibilidade = 100.0 - packet_loss
                    
                    total_disponibilidade += disponibilidade
                    total_banda += total_bandwidth
                    total_qualidade += latency
                    total_loss += packet_loss
                    
                    # Write individual client metrics
                    tags = {
                        'client': str(client_name).replace(' ', '_'),
                        'region': 'norte'
                    }
                    
                    fields = {
                        'disponibilidade': disponibilidade,
                        'consumo_banda': total_bandwidth,
                        'qualidade': latency,
                        'packets_loss': packet_loss
                    }
                    
                    now_ns = int(time.time() * 1e9)
                    write_point('viaipe_cliente', tags, fields, timestamp=now_ns)
                    
                    logger.debug(f"Cliente {client_name}: disp={disponibilidade:.2f}% | banda={total_bandwidth:.0f} B/s | latência={latency:.2f}ms | loss={packet_loss:.2f}%")
            
            except Exception as ce:
                logger.error(f"Erro ao processar cliente {client.get('id', 'unknown')}: {ce}")
                continue
        
        # Calculate aggregated metrics
        if total_clients > 0:
            media_disponibilidade = total_disponibilidade / total_clients
            media_banda = total_banda / total_clients
            media_qualidade = total_qualidade / total_clients
            media_loss = total_loss / total_clients
        else:
            media_disponibilidade = 0
            media_banda = 0
            media_qualidade = 0
            media_loss = 0
        
        # Write aggregated metrics
        tags_global = {'region': 'norte'}
        fields_global = {
            'media_disponibilidade': media_disponibilidade,
            'media_banda': media_banda,
            'media_qualidade': media_qualidade,
            'media_loss': media_loss,
            'total_clientes': total_clients
        }
        now_ns = int(time.time() * 1e9)
        write_point('viaipe_agregado', tags_global, fields_global, timestamp=now_ns)
        
        logger.info(f"✓ Agregado NORTE: disponibilidade={media_disponibilidade:.2f}% | banda={media_banda:.0f}B/s | qualidade={media_qualidade:.2f}ms | clientes={total_clients}")
    
    except Exception as e:
        logger.error(f"Erro ao processar dados do ViaIpe: {e}", exc_info=True)

def main():
    logger.info(f'Agent ViaIpe iniciado. API: {VIAIPE_API_URL} | Influx: {INFLUX_URL} | DB: {INFLUX_DB} | Interval: {INTERVAL}s')
    create_db()
    
    while True:
        try:
            data = fetch_viaipe_data()
            if data:
                parse_viaipe_data(data)
            else:
                logger.warning(f'Falha ao obter dados da API ViaIpe, tentando novamente em {INTERVAL}s')
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}", exc_info=True)
        
        time.sleep(INTERVAL)

if __name__ == '__main__':
    main()
