# 🐳 Deploy Docker - Starlink Data Analyzer

Guia completo para hospedar o sistema na VPS usando Docker.

## 📋 Pré-requisitos

### VPS/Server
- Ubuntu 20.04+ ou similar
- Docker e Docker Compose instalados
- Porta 8501 e 8502 liberadas no firewall
- Pelo menos 2GB RAM e 10GB de espaço

### Local (para desenvolvimento)
- Docker Desktop instalado
- Git para clonar o repositório

## 🚀 Deploy na VPS

### 1. Preparação do Servidor

```bash
# Atualiza o sistema
sudo apt update && sudo apt upgrade -y

# Instala Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instala Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Reinicia a sessão
exit
# Faça login novamente
```

### 2. Clonagem e Configuração

```bash
# Clona o repositório
git clone <seu-repositorio>
cd Starlink_Consumo

# Copia arquivo de configuração
cp env.example .env

# Edita as configurações
nano .env
```

### 3. Configuração do .env

```bash
# Token do InfluxDB (OBRIGATÓRIO)
INFLUXDB_TOKEN=seu_token_do_influxdb_aqui

# Configurações do Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### 4. Deploy Automático

```bash
# Executa o script de deploy
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### 5. Deploy Manual

```bash
# Para containers existentes
docker-compose down

# Build das imagens
docker-compose build --no-cache

# Inicia os containers
docker-compose up -d

# Verifica status
docker-compose ps
```

## 🌐 Acesso às Aplicações

### URLs de Acesso
- **Aplicação Principal**: http://seu-ip:8501
- **Visualizador Diário**: http://seu-ip:8502

### Configuração de Firewall
```bash
# Libera portas no UFW
sudo ufw allow 8501
sudo ufw allow 8502
sudo ufw reload
```

## 📊 Gerenciamento dos Containers

### Scripts Disponíveis

```bash
# Iniciar containers
./scripts/start.sh

# Parar containers
./scripts/stop.sh

# Ver logs em tempo real
./scripts/logs.sh

# Deploy completo
./scripts/deploy.sh
```

### Comandos Docker

```bash
# Status dos containers
docker-compose ps

# Logs dos containers
docker-compose logs -f

# Parar containers
docker-compose down

# Reiniciar containers
docker-compose restart

# Atualizar containers
docker-compose pull
docker-compose up -d
```

## 🔧 Configurações Avançadas

### Nginx Reverse Proxy (Opcional)

```nginx
# /etc/nginx/sites-available/starlink
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

```bash
# Instala Certbot
sudo apt install certbot python3-certbot-nginx

# Obtém certificado SSL
sudo certbot --nginx -d seu-dominio.com
```

## 📈 Monitoramento

### Health Checks
Os containers incluem health checks automáticos:
- Verifica se a aplicação está respondendo
- Reinicia automaticamente em caso de falha
- Logs de saúde disponíveis

### Logs
```bash
# Logs em tempo real
docker-compose logs -f

# Logs específicos
docker-compose logs starlink-analyzer
docker-compose logs starlink-daily-viewer

# Logs com timestamp
docker-compose logs -f -t
```

## 🛠️ Solução de Problemas

### Container não inicia
```bash
# Verifica logs de erro
docker-compose logs starlink-analyzer

# Verifica configuração
docker-compose config

# Rebuild sem cache
docker-compose build --no-cache
```

### Porta ocupada
```bash
# Verifica portas em uso
sudo netstat -tulpn | grep :8501

# Mata processo na porta
sudo fuser -k 8501/tcp
```

### Problemas de memória
```bash
# Verifica uso de recursos
docker stats

# Limpa containers não utilizados
docker system prune -a
```

## 🔄 Atualizações

### Atualização do Código
```bash
# Para containers
docker-compose down

# Atualiza código
git pull

# Rebuild e inicia
docker-compose build --no-cache
docker-compose up -d
```

### Backup de Dados
```bash
# Backup dos volumes
docker run --rm -v starlink_consumo_data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz -C /data .

# Restore dos dados
docker run --rm -v starlink_consumo_data:/data -v $(pwd):/backup alpine tar xzf /backup/data-backup.tar.gz -C /data
```

## 📱 Acesso Mobile

### Configuração para Mobile
- A aplicação é responsiva e funciona em dispositivos móveis
- Acesse via IP da VPS: http://seu-ip:8501
- Para domínio: http://seu-dominio.com

## 🔒 Segurança

### Recomendações
1. **Firewall**: Configure apenas as portas necessárias
2. **SSL**: Use HTTPS em produção
3. **Tokens**: Mantenha tokens seguros no .env
4. **Updates**: Mantenha Docker e sistema atualizados
5. **Backup**: Faça backup regular dos dados

### Variáveis de Ambiente Seguras
```bash
# Nunca commite o arquivo .env
echo ".env" >> .gitignore

# Use variáveis de ambiente do sistema
export INFLUXDB_TOKEN="seu_token"
```

## 📞 Suporte

### Comandos Úteis
```bash
# Status completo
docker-compose ps
docker system df
docker images

# Limpeza
docker system prune -a
docker volume prune
```

### Logs de Debug
```bash
# Logs detalhados
docker-compose logs --tail=100 -f

# Logs de build
docker-compose build --no-cache --progress=plain
```

---

**🐳 Starlink Data Analyzer Docker** - Deploy automatizado para VPS
