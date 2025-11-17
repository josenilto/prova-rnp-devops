# Usa uma imagem base Python slim (mais leve)
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala as dependências necessárias para a aplicação Python e o comando 'ping'
# O pacote iputils-ping é necessário para o comando 'ping' dentro do container Alpine/Debian
RUN apt-get update && \
    apt-get install -y iputils-ping && \
    rm -rf /var/lib/apt/lists/*

# Copia o arquivo de requisitos (não temos um, mas é boa prática, instalaremos direto)
# RUN pip install --no-cache-dir -r requirements.txt
# Instala as bibliotecas Python
RUN pip install --no-cache-dir influxdb-client requests

# Copia o script do agente para o container
COPY monitor.py .

# Variáveis de ambiente padrão
ENV INFLUXDB_URL=http://influxdb:8086
ENV INFLUXDB_DB=monitoring
ENV INTERVAL=60

# Comando para executar o agente
CMD ["python", "monitor.py"]