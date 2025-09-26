#!/usr/bin/env python3
"""
Cliente para conexão e consultas no InfluxDB
"""

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.query_api import QueryApi
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from influx_config import INFLUX_CONFIG, BIT_STAR_DEVICES, get_flux_query, get_daily_consumption_query, update_device_list, get_device_display_name

class StarlinkInfluxClient:
    def __init__(self):
        """Inicializa cliente InfluxDB"""
        self.client = None
        self.query_api = None
        self.connect()
    
    def connect(self):
        """Conecta ao InfluxDB"""
        try:
            if not INFLUX_CONFIG["token"]:
                st.error("❌ Token do InfluxDB não configurado! Configure a variável INFLUXDB_TOKEN")
                return False
            
            self.client = InfluxDBClient(
                url=INFLUX_CONFIG["url"],
                token=INFLUX_CONFIG["token"],
                org=INFLUX_CONFIG["org"]
            )
            self.query_api = self.client.query_api()
            return True
        except Exception as e:
            st.error(f"❌ Erro ao conectar no InfluxDB: {str(e)}")
            return False
    
    def test_connection(self):
        """Testa conexão com InfluxDB"""
        try:
            if not self.client:
                return False
            
            # Query simples para testar conexão
            query = f'''
            from(bucket: "{INFLUX_CONFIG['bucket']}")
            |> range(start: -1h)
            |> limit(n: 1)
            '''
            
            result = self.query_api.query(query)
            return len(list(result)) > 0
        except Exception as e:
            st.error(f"❌ Erro ao testar conexão: {str(e)}")
            return False
    
    def get_available_devices(self, days_back=7, custom_time_range=None):
        """Retorna lista de dispositivos disponíveis e atualiza a lista global"""
        try:
            # Se um período personalizado foi fornecido, usa ele; senão usa days_back
            if custom_time_range:
                if ':' in custom_time_range and 'Z' in custom_time_range:
                    # Procura pelo padrão 'Z:' para separar start e stop corretamente
                    if 'Z:' in custom_time_range:
                        parts = custom_time_range.split('Z:', 1)
                        if len(parts) == 2:
                            start_time = parts[0] + 'Z'  # Adiciona o Z de volta
                            end_time = parts[1]
                            range_clause = f'start: {start_time}, stop: {end_time}'
                        else:
                            range_clause = f'start: {custom_time_range}'
                    else:
                        range_clause = f'start: {custom_time_range}'
                else:
                    range_clause = f'start: {custom_time_range}'
            else:
                range_clause = f'start: -{days_back}d'
            
            # Query mais flexível para buscar dispositivos
            query = f'''
            from(bucket: "{INFLUX_CONFIG['bucket']}")
            |> range({range_clause})
            |> filter(fn: (r) => r._measurement == "starlink_data" or r._measurement == "starlink_raw")
            |> filter(fn: (r) => exists r.device or exists r.device_name)
            |> keep(columns: ["device", "device_name", "device_ip"])
            |> distinct()
            |> sort(columns: ["device"])
            '''
            
            result = self.query_api.query(query)
            devices = []
            device_info = {}
            
            for table in result:
                for record in table.records:
                    # Tenta diferentes campos para identificar o dispositivo
                    device_id = None
                    device_name = None
                    device_ip = None
                    
                    # Verifica campos disponíveis
                    if "device" in record.values and record.values["device"]:
                        device_id = record.values["device"].strip()
                    elif "device_name" in record.values and record.values["device_name"]:
                        device_id = record.values["device_name"].strip()
                    
                    if "device_name" in record.values and record.values["device_name"]:
                        device_name = record.values["device_name"].strip()
                    
                    if "device_ip" in record.values and record.values["device_ip"]:
                        device_ip = record.values["device_ip"].strip()
                    
                    if device_id:
                        devices.append(device_id)
                        device_info[device_id] = {
                            "name": device_name or device_id,
                            "ip": device_ip
                        }
            
            # Remove duplicatas e ordena
            devices = sorted(list(set(devices)))
            
            # Atualiza a lista global de dispositivos
            if devices:
                update_device_list(devices)
                st.info(f"📱 {len(devices)} dispositivo(s) encontrado(s)")
            else:
                st.warning("⚠️ Nenhum dispositivo encontrado nos últimos 30 dias")
                
                # Query de diagnóstico adicional
                st.info("🔍 Executando diagnóstico...")
                diag_query = f'''
                from(bucket: "{INFLUX_CONFIG['bucket']}")
                |> range(start: -{days_back}d)
                |> limit(n: 10)
                |> keep(columns: ["_time", "_measurement", "_field", "_value"])
                '''
                
                try:
                    diag_result = self.query_api.query(diag_query)
                    diag_data = []
                    for table in diag_result:
                        for record in table.records:
                            diag_data.append({
                                "time": record.get_time(),
                                "measurement": record.get_measurement(),
                                "field": record.get_field(),
                                "value": record.get_value()
                            })
                    
                    if diag_data:
                        st.write("**Dados encontrados no bucket:**")
                        diag_df = pd.DataFrame(diag_data)
                        st.dataframe(diag_df)
                    else:
                        st.error("❌ Nenhum dado encontrado no bucket")
                except Exception as e:
                    st.error(f"❌ Erro no diagnóstico: {str(e)}")
            
            return devices
        except Exception as e:
            st.error(f"❌ Erro ao buscar dispositivos: {str(e)}")
            return []
    
    def execute_custom_query(self, query):
        """
        Executa uma query Flux customizada
        
        Args:
            query: String com query Flux
            
        Returns:
            Lista de DataFrames com os resultados
        """
        try:
            result = self.query_api.query(query)
            dataframes = []
            
            for table in result:
                records = []
                for record in table.records:
                    records.append({
                        '_time': record.get_time(),
                        '_field': record.get_field(),
                        '_value': record.get_value(),
                        '_measurement': record.get_measurement(),
                        **record.values
                    })
                
                if records:
                    df = pd.DataFrame(records)
                    dataframes.append(df)
            
            return dataframes
        except Exception as e:
            st.error(f"❌ Erro ao executar query: {str(e)}")
            return []
    
    def get_starlink_data(self, devices, time_range, max_gap_minutes=5):
        """
        Busca dados do Starlink do InfluxDB e extrai throughput do JSON
        
        Args:
            devices: Lista de dispositivos
            time_range: Período de tempo (ex: "-24h", "-7d")
            max_gap_minutes: Gap máximo em minutos
        
        Returns:
            DataFrame com dados processados
        """
        try:
            if not devices:
                return pd.DataFrame()
            
            # Gera query Flux
            query = get_flux_query(devices, time_range)
            
            # Executa query
            result = self.query_api.query(query)
            
            # Processa resultados extraindo throughput do JSON
            data = []
            
            for table in result:
                for record in table.records:
                    try:
                        timestamp = record.get_time()
                        field = record.get_field()
                        value = record.get_value()
                        device = record.values.get("device") or record.values.get("device_name", "unknown")
                        
                        # Só processa se for status_json
                        if field == "status_json" and value:
                            # Extrai throughput do JSON
                            throughput_data = self._extract_throughput_from_json(value)
                            
                            if throughput_data:
                                data.append({
                                    'timestamp': timestamp,
                                    'device': device,
                                    'downlink_bps': throughput_data.get('downlinkThroughputBps', 0),
                                    'uplink_bps': throughput_data.get('uplinkThroughputBps', 0),
                                    'downlink_mbps': throughput_data.get('downlinkThroughputBps', 0) / 1_000_000,
                                    'uplink_mbps': throughput_data.get('uplinkThroughputBps', 0) / 1_000_000
                                })
                            
                    except Exception as e:
                        continue
            
            if not data:
                return pd.DataFrame()
            
            df = pd.DataFrame(data)
            df = df.sort_values('timestamp')
            
            # Remove gaps grandes
            if len(df) > 1:
                df['time_diff'] = df['timestamp'].diff()
                df['gap_minutes'] = df['time_diff'].dt.total_seconds() / 60
                df = df[df['gap_minutes'] <= max_gap_minutes]
                df = df.drop(['time_diff', 'gap_minutes'], axis=1)
            
            return df
            
        except Exception as e:
            st.error(f"❌ Erro ao buscar dados: {str(e)}")
            return pd.DataFrame()
    
    def _extract_throughput_from_json(self, json_value):
        """
        Extrai valores de throughput do JSON do status_json
        
        Args:
            json_value: String JSON contendo dados do Starlink
        
        Returns:
            Dict com downlinkThroughputBps e uplinkThroughputBps
        """
        try:
            import json
            
            # Se já é um dict, usa diretamente
            if isinstance(json_value, dict):
                data = json_value
            else:
                # Se é string, faz parse
                data = json.loads(json_value)
            
            # Extrai throughput do JSON aninhado
            throughput = {}
            
            # Procura por downlinkThroughputBps e uplinkThroughputBps no JSON
            if 'downlinkThroughputBps' in data:
                throughput['downlinkThroughputBps'] = float(data['downlinkThroughputBps'])
            elif 'dishGetStatus' in data and 'downlinkThroughputBps' in data['dishGetStatus']:
                throughput['downlinkThroughputBps'] = float(data['dishGetStatus']['downlinkThroughputBps'])
            
            if 'uplinkThroughputBps' in data:
                throughput['uplinkThroughputBps'] = float(data['uplinkThroughputBps'])
            elif 'dishGetStatus' in data and 'uplinkThroughputBps' in data['dishGetStatus']:
                throughput['uplinkThroughputBps'] = float(data['dishGetStatus']['uplinkThroughputBps'])
            
            return throughput
            
        except Exception as e:
            return {}
    
    def get_daily_consumption(self, devices, time_range, max_gap_minutes=5):
        """
        Calcula consumo diário de dados baseado na diferença de tempo entre timestamps
        
        Args:
            devices: Lista de dispositivos
            time_range: Período de tempo
            max_gap_minutes: Gap máximo em minutos (padrão: 5)
        
        Returns:
            DataFrame com consumo diário por dispositivo
        """
        try:
            # Busca dados brutos
            df = self.get_starlink_data(devices, time_range, max_gap_minutes)
            
            if df.empty:
                return pd.DataFrame()
            
            # Adiciona coluna de data
            df['date'] = df['timestamp'].dt.date
            
            daily_data = []
            
            for device in df['device'].unique():
                device_df = df[df['device'] == device].copy()
                
                for date in device_df['date'].unique():
                    day_df = device_df[device_df['date'] == date].sort_values('timestamp')
                    
                    if len(day_df) < 2:
                        continue
                    
                    day_download = 0
                    day_upload = 0
                    gaps = 0
                    valid_intervals = 0
                    
                    # Calcula consumo baseado na diferença de tempo entre registros consecutivos
                    for i in range(len(day_df) - 1):
                        current = day_df.iloc[i]
                        next_row = day_df.iloc[i + 1]
                        
                        # Calcula diferença de tempo em minutos
                        time_diff = next_row['timestamp'] - current['timestamp']
                        time_diff_minutes = time_diff.total_seconds() / 60
                        
                        # Se gap > 5 minutos, considera que não houve continuação de uso
                        if time_diff_minutes > max_gap_minutes:
                            gaps += 1
                            continue
                        
                        # Calcula consumo baseado na velocidade média durante o intervalo
                        time_diff_seconds = time_diff.total_seconds()
                        
                        # Usa a velocidade do registro atual para calcular consumo
                        # Fórmula: (velocidade_bps * tempo_segundos) / 8 bits_por_byte / 1024^3 para GB
                        download_gb = (current['downlink_bps'] * time_diff_seconds) / 8 / (1024 ** 3)
                        upload_gb = (current['uplink_bps'] * time_diff_seconds) / 8 / (1024 ** 3)
                        
                        day_download += download_gb
                        day_upload += upload_gb
                        valid_intervals += 1
                    
                    daily_data.append({
                        'date': date,
                        'device': device,
                        'device_name': get_device_display_name(device),
                        'download_gb': round(day_download, 3),
                        'upload_gb': round(day_upload, 3),
                        'total_gb': round(day_download + day_upload, 3),
                        'gaps': gaps,
                        'valid_intervals': valid_intervals,
                        'records': len(day_df)
                    })
            
            return pd.DataFrame(daily_data).sort_values(['date', 'device'])
            
        except Exception as e:
            st.error(f"❌ Erro ao calcular consumo diário: {str(e)}")
            return pd.DataFrame()
    
    def get_device_summary(self, devices, time_range):
        """
        Retorna resumo dos dispositivos
        
        Args:
            devices: Lista de dispositivos
            time_range: Período de tempo
        
        Returns:
            Dict com resumo por dispositivo
        """
        try:
            df = self.get_starlink_data(devices, time_range)
            
            if df.empty:
                return {}
            
            summary = {}
            
            for device in df['device'].unique():
                device_df = df[df['device'] == device]
                
                if not device_df.empty:
                    summary[device] = {
                        'name': get_device_display_name(device),
                        'total_records': len(device_df),
                        'records': len(device_df),
                        'period_start': device_df['timestamp'].min(),
                        'period_end': device_df['timestamp'].max(),
                        'avg_download_mbps': device_df['downlink_mbps'].mean(),
                        'avg_upload_mbps': device_df['uplink_mbps'].mean(),
                        'max_download_mbps': device_df['downlink_mbps'].max(),
                        'max_upload_mbps': device_df['uplink_mbps'].max()
                    }
            
            return summary
            
        except Exception as e:
            st.error(f"❌ Erro ao gerar resumo: {str(e)}")
            return {}
    
    def close(self):
        """Fecha conexão com InfluxDB"""
        if self.client:
            self.client.close()
