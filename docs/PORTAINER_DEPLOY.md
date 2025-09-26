# 🐳 Deploy no Portainer - Starlink Data Analyzer

Guia completo para hospedar o sistema no Portainer usando Docker Compose.

## 📋 Pré-requisitos

### Portainer
- Portainer instalado e funcionando
- Acesso administrativo ao Portainer
- Docker Swarm ou Docker Standalone configurado

### Repositório
- Código no GitHub: `https://github.com/Bitelectronics1/starlink_consumo.git`
- Arquivo `docker-compose.yml` configurado

## 🚀 Deploy via Portainer

### Método 1: Stack Docker Compose (Recomendado)

#### 1. Acesse o Portainer
- URL: `http://seu-ip:9000` ou `https://seu-dominio:9000`
- Faça login com suas credenciais

#### 2. Crie uma Nova Stack
1. Clique em **"Stacks"** no menu lateral
2. Clique em **"Add stack"**
3. Nome: `starlink-analyzer`

#### 3. Configure o Docker Compose
Cole o conteúdo do `docker-compose.yml`:

```yaml
version: '3.8'

services:
  starlink-analyzer:
    build: 
      context: https://github.com/Bitelectronics1/starlink_consumo.git
      dockerfile: Dockerfile
    container_name: starlink-data-analyzer
    ports:
      - "8501:8501"
    environment:
      - INFLUXDB_TOKEN=${INFLUXDB_TOKEN}
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
    volumes:
      - starlink_logs:/app/logs
      - starlink_data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - starlink-network

  starlink-daily-viewer:
    build: 
      context: https://github.com/Bitelectronics1/starlink_consumo.git
      dockerfile: Dockerfile
    container_name: starlink-daily-viewer
    ports:
      - "8502:8501"
    environment:
      - INFLUXDB_TOKEN=${INFLUXDB_TOKEN}
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
    volumes:
      - starlink_logs:/app/logs
      - starlink_data:/app/data
    restart: unless-stopped
    command: ["python", "-m", "streamlit", "run", "src/web/daily_gb_viewer.py", "--server.port=8501", "--server.address=0.0.0.0"]
    networks:
      - starlink-network

networks:
  starlink-network:
    driver: bridge

volumes:
  starlink_logs:
  starlink_data:
```

#### 4. Configure as Variáveis de Ambiente
Na seção **"Environment variables"**:

```bash
INFLUXDB_TOKEN=seu_token_do_influxdb_aqui
```

#### 5. Deploy da Stack
1. Clique em **"Deploy the stack"**
2. Aguarde o build e deploy
3. Verifique os logs se necessário

### Método 2: Container Individual

#### 1. Crie um Container
1. Clique em **"Containers"** no menu lateral
2. Clique em **"Add container"**

#### 2. Configure o Container
- **Name**: `starlink-analyzer`
- **Image**: `python:3.11-slim`
- **Command**: 
  ```bash
  sh -c "git clone https://github.com/Bitelectronics1/starlink_consumo.git /app && cd /app && pip install -r requirements.txt && python -m streamlit run src/web/app_simple.py --server.port=8501 --server.address=0.0.0.0"
  ```

#### 3. Configure as Portas
- **Port mapping**: `8501:8501`

#### 4. Configure as Variáveis de Ambiente
```bash
INFLUXDB_TOKEN=seu_token_do_influxdb_aqui
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

#### 5. Configure os Volumes
- **Volume mapping**: 
  - `/app/logs` → `starlink_logs`
  - `/app/data` → `starlink_data`

## 🌐 Acesso às Aplicações

### URLs de Acesso
- **Aplicação Principal**: `http://seu-ip:8501`
- **Visualizador Diário**: `http://seu-ip:8502`

### Configuração de Firewall
```bash
# Libera portas no UFW
sudo ufw allow 8501
sudo ufw allow 8502
sudo ufw reload
```

## 📊 Gerenciamento no Portainer

### Monitoramento
1. **Stacks** → `starlink-analyzer` → **"Inspect"**
2. Verifique status dos containers
3. Acesse logs em tempo real

### Logs
1. Clique no container
2. Aba **"Logs"**
3. Configure filtros se necessário

### Reinicialização
1. **Stacks** → `starlink-analyzer` → **"Editor"**
2. Clique em **"Update the stack"**
3. Aguarde o redeploy

### Parada/Início
1. **Stacks** → `starlink-analyzer`
2. **"Stop stack"** ou **"Start stack"**

## 🔧 Configurações Avançadas

### Nginx Reverse Proxy
Se usar Nginx no Portainer:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL com Let's Encrypt
1. Instale o **"Nginx Proxy Manager"** no Portainer
2. Configure SSL automático
3. Aponte para `localhost:8501`

## 🛠️ Solução de Problemas

### Container não inicia
1. Verifique os logs no Portainer
2. Confirme se o token InfluxDB está correto
3. Verifique se as portas estão livres

### Erro de Build
1. Verifique se o repositório GitHub está acessível
2. Confirme se o Dockerfile está correto
3. Verifique os logs de build

### Problemas de Rede
1. Verifique se as portas estão mapeadas corretamente
2. Confirme se o firewall está configurado
3. Teste conectividade local

## 📈 Monitoramento

### Health Checks
- Verificação automática a cada 30 segundos
- Reinicialização automática em caso de falha
- Logs de saúde disponíveis

### Métricas
- Uso de CPU e memória
- Tráfego de rede
- Status dos containers

## 🔄 Atualizações

### Atualização via Portainer
1. **Stacks** → `starlink-analyzer` → **"Editor"**
2. Modifique o `docker-compose.yml` se necessário
3. Clique em **"Update the stack"**

### Atualização do Código
1. Faça push das alterações no GitHub
2. No Portainer, **"Update the stack"**
3. Os containers serão rebuildados automaticamente

## 🔒 Segurança

### Recomendações
1. **Firewall**: Configure apenas as portas necessárias
2. **SSL**: Use HTTPS em produção
3. **Tokens**: Mantenha tokens seguros nas variáveis de ambiente
4. **Updates**: Mantenha Portainer e Docker atualizados
5. **Backup**: Configure backup dos volumes

### Variáveis de Ambiente Seguras
- Nunca commite tokens no código
- Use variáveis de ambiente do Portainer
- Configure secrets para dados sensíveis

## 📱 Acesso Mobile

### Configuração para Mobile
- A aplicação é responsiva
- Acesse via IP da VPS: `http://seu-ip:8501`
- Para domínio: `http://seu-dominio.com`

## 📞 Suporte

### Comandos Úteis no Portainer
- **Logs**: Aba "Logs" em cada container
- **Status**: Aba "Inspect" para detalhes
- **Rede**: Aba "Network" para configurações

### Logs de Debug
- Acesse logs em tempo real
- Configure filtros por nível
- Exporte logs se necessário

---

**🐳 Starlink Data Analyzer Portainer** - Deploy automatizado via Portainer

