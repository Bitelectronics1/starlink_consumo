#!/bin/bash

# Script para parar os containers
# Uso: ./scripts/stop.sh

echo "🛑 Parando Starlink Data Analyzer..."

# Para os containers
docker-compose down

echo "✅ Containers parados!"
