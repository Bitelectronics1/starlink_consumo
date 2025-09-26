# Dockerfile para Starlink Data Analyzer
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de dependências
COPY requirements.txt pyproject.toml ./

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte
COPY src/ ./src/
COPY docs/ ./docs/

# Cria diretório para logs
RUN mkdir -p /app/logs

# Expõe a porta do Streamlit
EXPOSE 8501

# Define variáveis de ambiente
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Comando para iniciar a aplicação
CMD ["python", "-m", "streamlit", "run", "src/web/app_simple.py", "--server.port=8501", "--server.address=0.0.0.0"]
