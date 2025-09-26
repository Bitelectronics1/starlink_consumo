#!/bin/bash

# Script de deploy para VPS - Starlink Data Analyzer
# Uso: ./scripts/deploy.sh

set -e

echo "🚀 Iniciando deploy do Starlink Data Analyzer..."

# Verifica se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Instalando..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker instalado. Faça logout e login novamente."
    exit 1
fi

# Verifica se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Instalando..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose instalado."
fi

# Verifica se arquivo .env existe
if [ ! -f .env ]; then
    echo "❌ Arquivo .env não encontrado. Copiando env.example..."
    cp env.example .env
    echo "⚠️ Configure o arquivo .env com suas credenciais antes de continuar."
    echo "Edite: nano .env"
    exit 1
fi

# Para containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Remove imagens antigas
echo "🧹 Limpando imagens antigas..."
docker-compose down --rmi all

# Build e start dos containers
echo "🔨 Fazendo build das imagens..."
docker-compose build --no-cache

echo "🚀 Iniciando containers..."
docker-compose up -d

# Verifica status dos containers
echo "📊 Verificando status dos containers..."
docker-compose ps

# Mostra logs
echo "📋 Logs dos containers:"
docker-compose logs --tail=20

echo ""
echo "✅ Deploy concluído!"
echo "🌐 Aplicação principal: http://localhost:8501"
echo "📊 Visualizador diário: http://localhost:8502"
echo ""
echo "Para ver logs em tempo real:"
echo "docker-compose logs -f"
echo ""
echo "Para parar os containers:"
echo "docker-compose down"
