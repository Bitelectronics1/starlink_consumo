#!/usr/bin/env python3
"""
Configuração para conexão com InfluxDB
"""

import os
from datetime import datetime, timedelta

# Configurações do InfluxDB
INFLUX_CONFIG = {
    "url": "http://82.25.70.236:8086",
    "org": "Bit Electronics",
    "bucket": "starlink_data",
    "token": os.environ.get("INFLUXDB_TOKEN", "_wGCTqWEmLq825Sp7L7ze709IAMpYY6CO2An_im5xMr7oQcPQmgIY4eykVQHh_Rh5N2dzhluHPrANL1_4seL1Q=="),  # Token deve estar nas variáveis de ambiente
}

# Configurações dos dispositivos Bit Star (será preenchido dinamicamente)
BIT_STAR_DEVICES = {}

def get_device_display_name(device_id):
    """
    Retorna nome de exibição para um dispositivo.
    Se não estiver na lista, usa o ID como nome.
    """
    if device_id in BIT_STAR_DEVICES:
        return BIT_STAR_DEVICES[device_id]["name"]
    else:
        # Gera nome baseado no ID do dispositivo
        return f"Bit Star {device_id.replace('bit', '').replace('star', '')}"

def update_device_list(devices_found):
    """
    Atualiza a lista de dispositivos com base nos encontrados no InfluxDB.
    
    Args:
        devices_found: Lista de IDs de dispositivos encontrados
    """
    global BIT_STAR_DEVICES
    
    # Limpa lista atual
    BIT_STAR_DEVICES = {}
    
    # Adiciona dispositivos encontrados
    for device_id in devices_found:
        BIT_STAR_DEVICES[device_id] = {
            "name": get_device_display_name(device_id),
            "measurement": "starlink_data",
            "tags": {"device": device_id}
        }

# Períodos pré-definidos
TIME_PERIODS = {
    "Última hora": {"start": "-1h", "label": "1 hora"},
    "Últimas 6 horas": {"start": "-6h", "label": "6 horas"},
    "Últimas 12 horas": {"start": "-12h", "label": "12 horas"},
    "Último dia": {"start": "-24h", "label": "1 dia"},
    "Últimos 3 dias": {"start": "-3d", "label": "3 dias"},
    "Última semana": {"start": "-7d", "label": "1 semana"},
    "Últimos 15 dias": {"start": "-15d", "label": "15 dias"},
    "Último mês": {"start": "-30d", "label": "1 mês"},
    "Personalizado": {"start": "custom", "label": "Período personalizado"}
}

def get_flux_query(devices, time_range, measurement="starlink_data"):
    """
    Gera query Flux para buscar dados do InfluxDB
    
    Args:
        devices: Lista de dispositivos para buscar
        time_range: Período de tempo (ex: "-24h", "-7d")
        measurement: Nome da medição no InfluxDB
    
    Returns:
        String com query Flux
    """
    
    # Converte lista de dispositivos em filtro mais flexível
    device_conditions = []
    for device in devices:
        device_conditions.append(f'r.device == "{device}"')
        device_conditions.append(f'r.device_name == "{device}"')
    
    device_filter = " or ".join(device_conditions)
    
    # Determina se é um período personalizado (contém ':') ou predefinido
    if ':' in time_range and 'Z' in time_range:
        # Período personalizado com datas específicas
        # Procura pelo padrão 'Z:' para separar start e stop corretamente
        if 'Z:' in time_range:
            parts = time_range.split('Z:', 1)
            if len(parts) == 2:
                start_time = parts[0] + 'Z'  # Adiciona o Z de volta
                end_time = parts[1]
                range_clause = f'start: {start_time}, stop: {end_time}'
            else:
                range_clause = f'start: {time_range}'
        else:
            range_clause = f'start: {time_range}'
    else:
        # Período predefinido
        range_clause = f'start: {time_range}'
    
    # Query para buscar dados do status_json que contém throughput
    query = f'''from(bucket: "{INFLUX_CONFIG['bucket']}")
|> range({range_clause})
|> filter(fn: (r) => r._measurement == "{measurement}" or r._measurement == "starlink_raw")
|> filter(fn: (r) => {device_filter})
|> filter(fn: (r) => r._field == "status_json")
|> keep(columns: ["_time", "_field", "_value", "device", "device_name", "device_ip"])
|> sort(columns: ["_time"])'''
    
    return query

def get_daily_consumption_query(devices, time_range, measurement="starlink_data"):
    """
    Gera query Flux para consumo diário
    
    Args:
        devices: Lista de dispositivos
        time_range: Período de tempo
        measurement: Nome da medição
    
    Returns:
        String com query Flux para consumo diário
    """
    
    # Converte lista de dispositivos em filtro mais flexível
    device_conditions = []
    for device in devices:
        device_conditions.append(f'r.device == "{device}"')
        device_conditions.append(f'r.device_name == "{device}"')
    
    device_filter = " or ".join(device_conditions)
    
    # Determina se é um período personalizado (contém ':') ou predefinido
    if ':' in time_range and 'Z' in time_range:
        # Período personalizado com datas específicas
        # Procura pelo padrão 'Z:' para separar start e stop corretamente
        if 'Z:' in time_range:
            parts = time_range.split('Z:', 1)
            if len(parts) == 2:
                start_time = parts[0] + 'Z'  # Adiciona o Z de volta
                end_time = parts[1]
                range_clause = f'start: {start_time}, stop: {end_time}'
            else:
                range_clause = f'start: {time_range}'
        else:
            range_clause = f'start: {time_range}'
    else:
        # Período predefinido
        range_clause = f'start: {time_range}'
    
    # Query simplificada para buscar dados do status_json
    query = f'''from(bucket: "{INFLUX_CONFIG['bucket']}")
|> range({range_clause})
|> filter(fn: (r) => r._measurement == "{measurement}" or r._measurement == "starlink_raw")
|> filter(fn: (r) => {device_filter})
|> filter(fn: (r) => r._field == "status_json")
|> keep(columns: ["_time", "_field", "_value", "device", "device_name", "device_ip"])
|> sort(columns: ["_time"])'''
    
    return query
