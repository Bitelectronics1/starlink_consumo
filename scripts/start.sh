#!/bin/bash

# Script para iniciar os containers
# Uso: ./scripts/start.sh

echo "🚀 Iniciando Starlink Data Analyzer..."

# Verifica se arquivo .env existe
if [ ! -f .env ]; then
    echo "❌ Arquivo .env não encontrado. Copiando env.example..."
    cp env.example .env
    echo "⚠️ Configure o arquivo .env com suas credenciais antes de continuar."
    exit 1
fi

# Inicia os containers
docker-compose up -d

# Verifica status
docker-compose ps

echo ""
echo "✅ Containers iniciados!"
echo "🌐 Aplicação principal: http://localhost:8501"
echo "📊 Visualizador diário: http://localhost:8502"
echo ""
echo "Para ver logs: docker-compose logs -f"
echo "Para parar: docker-compose down"
