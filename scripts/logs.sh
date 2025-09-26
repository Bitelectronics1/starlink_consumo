#!/bin/bash

# Script para ver logs dos containers
# Uso: ./scripts/logs.sh

echo "📋 Logs do Starlink Data Analyzer..."

# Mostra logs em tempo real
docker-compose logs -f
