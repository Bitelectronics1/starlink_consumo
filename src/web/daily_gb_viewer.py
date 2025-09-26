#!/usr/bin/env python3
"""
Visualizador de Consumo Diário em GB via InfluxDB
Foca especificamente no consumo diário de dados com comparação entre dispositivos
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'reports'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'auth'))
from pdf_generator import generate_pdf_report
from influx_client import StarlinkInfluxClient
from influx_config import TIME_PERIODS, BIT_STAR_DEVICES, get_device_display_name
from authentication import check_password, show_logout_button

# Configuração da página
st.set_page_config(
    page_title="Consumo Diário Starlink",
    page_icon="📊",
    layout="wide"
)

# Verifica autenticação
if not check_password():
    st.stop()

# Mostra botão de logout
show_logout_button()

st.title("📊 Consumo Diário de Dados Starlink (GB)")
st.markdown("---")

def initialize_influx_client():
    """Inicializa cliente InfluxDB"""
    if 'influx_client' not in st.session_state:
        st.session_state.influx_client = StarlinkInfluxClient()
    return st.session_state.influx_client

def get_available_devices(days_back=30, custom_time_range=None):
    """Retorna dispositivos disponíveis no InfluxDB"""
    client = initialize_influx_client()
    if not client:
        return []
    
    devices = client.get_available_devices(days_back, custom_time_range)
    return devices

def load_influx_data(devices, time_range, max_gap_minutes=5):
    """Carrega dados do InfluxDB"""
    client = initialize_influx_client()
    if not client:
        return pd.DataFrame()
    
    # Testa conexão
    if not client.test_connection():
        st.error("❌ Não foi possível conectar ao InfluxDB")
        return pd.DataFrame()
    
    # Busca dados
    df = client.get_starlink_data(devices, time_range, max_gap_minutes)
    
    if not df.empty:
        st.success(f"✅ {len(df)} registros carregados do InfluxDB")
        st.info(f"📊 Dispositivos: {', '.join(df['device'].unique())}")
    else:
        st.warning("⚠️ Nenhum dado encontrado para os parâmetros selecionados")
    
    return df

def calculate_usage(df, max_gap_minutes=5):
    """Calcula uso total de dados."""
    if df.empty:
        return 0, 0, 0, 0
    
    total_download = 0
    total_upload = 0
    gaps = 0
    
    for i in range(len(df) - 1):
        current = df.iloc[i]
        next_row = df.iloc[i + 1]
        
        time_diff = next_row['timestamp'] - current['timestamp']
        time_diff_minutes = time_diff.total_seconds() / 60
        
        if time_diff_minutes > max_gap_minutes:
            gaps += 1
            continue
        
        time_diff_seconds = time_diff.total_seconds()
        download_gb = (current['downlink_bps'] * time_diff_seconds) / 8 / (1024 ** 3)
        upload_gb = (current['uplink_bps'] * time_diff_seconds) / 8 / (1024 ** 3)
        
        total_download += download_gb
        total_upload += upload_gb
    
    return total_download, total_upload, gaps, len(df)

def calculate_daily_usage(df, max_gap_minutes=5, time_range=None):
    """Calcula uso de dados diariamente por dispositivo."""
    if df.empty:
        return pd.DataFrame()
    
    client = initialize_influx_client()
    if not client:
        return pd.DataFrame()
    
    # Usa método do cliente InfluxDB para cálculo diário
    devices = df['device'].unique().tolist()
    
    # Se não foi fornecido time_range, usa período padrão
    if not time_range:
        time_range = "-30d"
    
    daily_df = client.get_daily_consumption(devices, time_range, max_gap_minutes)
    return daily_df

# Interface
st.sidebar.header("📡 Conexão InfluxDB")

# Testa conexão
client = initialize_influx_client()
if client and client.test_connection():
    st.sidebar.success("✅ Conectado ao InfluxDB")
else:
    st.sidebar.error("❌ Erro de conexão com InfluxDB")
    st.stop()

st.sidebar.header("⏰ Período de Análise")

# Controles de data personalizada
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("Data início:", value=datetime.now().date() - timedelta(days=7))
with col2:
    end_date = st.date_input("Data fim:", value=datetime.now().date())

# Adicionar controles de hora
col1, col2 = st.sidebar.columns(2)
with col1:
    start_time = st.time_input("Hora início:", value=datetime.min.time())
with col2:
    end_time = st.time_input("Hora fim:", value=datetime.max.time())

# Converter para formato InfluxDB
start_datetime = datetime.combine(start_date, start_time)
end_datetime = datetime.combine(end_date, end_time)
time_range = f"{start_datetime.isoformat()}Z:{end_datetime.isoformat()}Z"

# Opção de períodos predefinidos
st.sidebar.markdown("---")
st.sidebar.markdown("**💡 Atalhos de Período:**")
period_option = st.sidebar.selectbox(
    "Aplicar período predefinido:",
    options=["Personalizado"] + list(TIME_PERIODS.keys()),
    index=0
)

if period_option != "Personalizado":
    # Aplica o período predefinido selecionado
    predefined_range = TIME_PERIODS[period_option]["start"]
    st.sidebar.info(f"Período aplicado: {predefined_range}")
    time_range = predefined_range
else:
    # Usa as datas personalizadas definidas acima
    st.sidebar.info(f"Período personalizado: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")

st.sidebar.header("📱 Seleção de Dispositivos")

# Busca dispositivos disponíveis no período selecionado
# Sempre usa o período selecionado (personalizado ou predefinido)
available_devices = get_available_devices(30, time_range)

if not available_devices:
    st.sidebar.warning("⚠️ Nenhum dispositivo encontrado no período selecionado")
    st.stop()

# Seleção múltipla de dispositivos (dinâmica)
if available_devices:
    # Cria opções dinâmicas baseadas nos dispositivos encontrados
    device_options = {}
    for device in available_devices:
        device_name = get_device_display_name(device)
        device_options[device] = device_name
    
    selected_devices = st.sidebar.multiselect(
        "Dispositivos:",
        options=list(device_options.keys()),
        format_func=lambda x: device_options[x],
        default=available_devices[:2] if len(available_devices) >= 2 else available_devices
    )
    
    # Mostra informações sobre dispositivos encontrados
    if len(available_devices) > 0:
        st.sidebar.success(f"✅ {len(available_devices)} dispositivo(s) detectado(s)")
else:
    selected_devices = []
    st.sidebar.warning("⚠️ Nenhum dispositivo encontrado")

# Configurações
st.sidebar.header("⚙️ Configurações")
max_gap = st.sidebar.slider("Gap máximo (min):", 1, 60, 5)

# Carrega dados
if selected_devices:
    df = load_influx_data(selected_devices, time_range, max_gap)
    
    if not df.empty:
        # Mostra informações sobre dispositivos encontrados
        st.success(f"✅ {len(available_devices)} dispositivo(s) encontrado(s)")
        
        # Consumo diário
        daily_df = calculate_daily_usage(df, max_gap, time_range)
        
        if not daily_df.empty:
            # Gráfico de consumo diário
            fig_daily = go.Figure()
            
            for device in daily_df['device'].unique():
                device_daily = daily_df[daily_df['device'] == device].sort_values('date')
                
                fig_daily.add_trace(go.Scatter(
                    x=device_daily['date'],
                    y=device_daily['download_gb'],
                    mode='lines+markers',
                    name=f'{get_device_display_name(device)} - Download',
                    line=dict(color='blue', width=2),
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                'Data: %{x}<br>' +
                                'Download: %{y:.3f} GB<br>' +
                                '<extra></extra>'
                ))
                
                fig_daily.add_trace(go.Scatter(
                    x=device_daily['date'],
                    y=device_daily['upload_gb'],
                    mode='lines+markers',
                    name=f'{get_device_display_name(device)} - Upload',
                    line=dict(color='red', width=2),
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                'Data: %{x}<br>' +
                                'Upload: %{y:.3f} GB<br>' +
                                '<extra></extra>'
                ))
            
            fig_daily.update_layout(
                title="Consumo Diário de Dados",
                xaxis_title="Data",
                yaxis_title="Consumo (GB)",
                hovermode='x unified',
                showlegend=True,
                barmode='group'
            )
            st.plotly_chart(fig_daily, width='stretch')
            
            # Gráfico de consumo acumulado
            fig_cum = go.Figure()
            
            for device in daily_df['device'].unique():
                device_daily = daily_df[daily_df['device'] == device].sort_values('date')
                device_daily['cumulative_download'] = device_daily['download_gb'].cumsum()
                device_daily['cumulative_upload'] = device_daily['upload_gb'].cumsum()
                device_daily['cumulative_total'] = device_daily['total_gb'].cumsum()
                
                fig_cum.add_trace(go.Scatter(
                    x=device_daily['date'],
                    y=device_daily['cumulative_download'],
                    mode='lines+markers',
                    name='Download Acumulado (GB)',
                    line=dict(color='blue', width=2),
                    marker=dict(size=4),
                    hovertemplate='<b>Download Acumulado</b><br>' +
                                'Data: %{x}<br>' +
                                'Download: %{y:.3f} GB<br>' +
                                '<extra></extra>'
                ))
                
                fig_cum.add_trace(go.Scatter(
                    x=device_daily['date'],
                    y=device_daily['cumulative_upload'],
                    mode='lines+markers',
                    name='Upload Acumulado (GB)',
                    line=dict(color='red', width=2),
                    marker=dict(size=4),
                    hovertemplate='<b>Upload Acumulado</b><br>' +
                                'Data: %{x}<br>' +
                                'Upload: %{y:.3f} GB<br>' +
                                '<extra></extra>'
                ))
                
                fig_cum.add_trace(go.Scatter(
                    x=device_daily['date'],
                    y=device_daily['cumulative_total'],
                    mode='lines+markers',
                    name='Total Acumulado (GB)',
                    line=dict(color='green', width=2),
                    marker=dict(size=4),
                    hovertemplate='<b>Total Acumulado</b><br>' +
                                'Data: %{x}<br>' +
                                'Total: %{y:.3f} GB<br>' +
                                '<extra></extra>'
                ))
            
            fig_cum.update_layout(
                title="Consumo Acumulado",
                xaxis_title="Data",
                yaxis_title="Consumo Acumulado (GB)",
                hovermode='x unified',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            st.plotly_chart(fig_cum, width='stretch')
            
            # Tabela de consumo diário
            st.subheader("📋 Tabela de Consumo Diário")
            daily_display = daily_df.copy()
            daily_display['date'] = daily_display['date'].astype(str)
            daily_display = daily_display.round(3)
            st.dataframe(daily_display, width='stretch')
            
            # Estatísticas gerais
            st.subheader("📊 Estatísticas Gerais")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_download = daily_df['download_gb'].sum()
                st.metric("Total Download", f"{total_download:.3f} GB")
            
            with col2:
                total_upload = daily_df['upload_gb'].sum()
                st.metric("Total Upload", f"{total_upload:.3f} GB")
            
            with col3:
                total_consumption = daily_df['total_gb'].sum()
                st.metric("Consumo Total", f"{total_consumption:.3f} GB")
            
            with col4:
                avg_daily = daily_df.groupby('date')['total_gb'].sum().mean()
                st.metric("Média Diária", f"{avg_daily:.3f} GB")
            
            # Botão para gerar relatório PDF
            if st.button("📄 Gerar Relatório PDF"):
                with st.spinner("Gerando relatório..."):
                    try:
                        # Informações dos dispositivos
                        device_names = [get_device_display_name(d) for d in daily_df['device'].unique()]
                        file_info = {
                            'filename': f"Dispositivos: {', '.join(device_names)}",
                            'period': f"{df['timestamp'].min().strftime('%d/%m/%Y')} - {df['timestamp'].max().strftime('%d/%m/%Y')}",
                            'total_records': len(df)
                        }
                        
                        # Informações de uso total
                        total_usage_info = {
                            'download_gb': total_download,
                            'upload_gb': total_upload,
                            'total_gb': total_consumption,
                            'gaps': 0  # Não calculamos gaps no daily viewer
                        }
                        
                        pdf_path = generate_pdf_report(df, daily_df, file_info, total_usage_info)
                        if pdf_path:
                            st.success(f"✅ Relatório gerado: {pdf_path}")
                            
                            # Botão para download
                            with open(pdf_path, "rb") as pdf_file:
                                st.download_button(
                                    label="📥 Baixar Relatório PDF",
                                    data=pdf_file.read(),
                                    file_name=f"starlink_daily_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                    mime="application/pdf"
                                )
                        else:
                            st.error("❌ Erro ao gerar relatório")
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar relatório: {str(e)}")
        else:
            st.warning("Não foi possível calcular o consumo diário")
    else:
        st.warning("⚠️ Nenhum dado encontrado para os parâmetros selecionados")
else:
    st.info("👆 Selecione pelo menos um dispositivo para começar a análise")
