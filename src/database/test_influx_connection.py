#!/usr/bin/env python3
"""
Script de teste para verificar conexão com InfluxDB
"""

import os
from influx_client import StarlinkInfluxClient
from influx_config import INFLUX_CONFIG

def test_connection():
    """Testa conexão com InfluxDB"""
    print("🔧 Testando conexão com InfluxDB...")
    print(f"URL: {INFLUX_CONFIG['url']}")
    print(f"Org: {INFLUX_CONFIG['org']}")
    print(f"Bucket: {INFLUX_CONFIG['bucket']}")
    print(f"Token: {'✅ Configurado' if INFLUX_CONFIG['token'] else '❌ Não configurado'}")
    print()
    
    if not INFLUX_CONFIG['token']:
        print("❌ Token do InfluxDB não configurado!")
        print("Configure a variável INFLUXDB_TOKEN:")
        print("Windows: $env:INFLUXDB_TOKEN='seu_token'")
        print("Linux/Mac: export INFLUXDB_TOKEN='seu_token'")
        return False
    
    try:
        client = StarlinkInfluxClient()
        
        if client.test_connection():
            print("✅ Conexão com InfluxDB estabelecida com sucesso!")
            
            # Testa busca de dispositivos
            devices = client.get_available_devices()
            if devices:
                from influx_config import get_device_display_name
                device_names = [get_device_display_name(d) for d in devices]
                print(f"📱 Dispositivos encontrados: {', '.join(device_names)}")
                print(f"📋 IDs dos dispositivos: {', '.join(devices)}")
            else:
                print("⚠️ Nenhum dispositivo encontrado")
            
            # Testa busca de dados
            print("\n🔍 Testando busca de dados...")
            df = client.get_starlink_data(devices[:1] if devices else [], "-1h")
            if not df.empty:
                print(f"✅ Dados carregados: {len(df)} registros")
                print(f"Período: {df['timestamp'].min()} - {df['timestamp'].max()}")
            else:
                print("⚠️ Nenhum dado encontrado")
            
            client.close()
            return True
        else:
            print("❌ Falha na conexão com InfluxDB")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_connection()
    if success:
        print("\n🎉 Teste concluído com sucesso!")
        print("Você pode executar as aplicações:")
        print("  streamlit run app_simple.py")
        print("  streamlit run daily_gb_viewer.py")
    else:
        print("\n❌ Teste falhou. Verifique a configuração.")
