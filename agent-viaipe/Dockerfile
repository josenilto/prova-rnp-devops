FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && \
    apt-get install -y ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY viaipe_collector.py ./

ENV VIAIPE_API_URL=https://legadoviaipe.rnp.br/api/norte
ENV INFLUXDB_URL=http://influxdb:8086
ENV INFLUXDB_DB=monitoring
ENV INTERVAL=300

CMD ["python", "viaipe_collector.py"]
