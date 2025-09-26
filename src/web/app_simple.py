#!/usr/bin/env python3
"""
Aplicação Streamlit para Análise de Dados Starlink via InfluxDB
Versão com integração direta ao InfluxDB e comparação entre dispositivos
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
    page_title="Starlink Data Analyzer",
    page_icon="🚀",
    layout="wide"
)

# Verifica autenticação
if not check_password():
    st.stop()

# Mostra botão de logout
show_logout_button()

st.title("🚀 Starlink Data Analyzer")
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
    """Calcula uso de dados."""
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

def get_device_summary(df):
    """Retorna resumo dos dispositivos"""
    if df.empty:
        return {}
    
    client = initialize_influx_client()
    if not client:
        return {}
    
    devices = df['device'].unique().tolist()
    time_range = "-30d"  # Usa período padrão
    
    return client.get_device_summary(devices, time_range)

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

# Análise
if selected_devices:
    st.header("📊 Análise de Dados Starlink")
    
    # Carrega dados do InfluxDB
    df = load_influx_data(selected_devices, time_range, max_gap)
    
    if not df.empty:
        # Calcula uso total
        download_gb, upload_gb, gaps, records = calculate_usage(df, max_gap)
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Download Total", f"{download_gb:.2f} GB")
        with col2:
            st.metric("Upload Total", f"{upload_gb:.2f} GB")
        with col3:
            st.metric("Total Geral", f"{download_gb + upload_gb:.2f} GB")
        with col4:
            st.metric("Gaps", gaps)
        
        # Estatísticas de Throughput
        st.subheader("📈 Estatísticas de Throughput")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Download (Mbps)**")
            throughput_stats = {
                'Métrica': ['Média', 'Máximo', 'Mínimo', 'Mediana'],
                'Download (Mbps)': [
                    f"{df['downlink_mbps'].mean():.2f}",
                    f"{df['downlink_mbps'].max():.2f}",
                    f"{df['downlink_mbps'].min():.2f}",
                    f"{df['downlink_mbps'].median():.2f}"
                ],
                'Upload (Mbps)': [
                    f"{df['uplink_mbps'].mean():.2f}",
                    f"{df['uplink_mbps'].max():.2f}",
                    f"{df['uplink_mbps'].min():.2f}",
                    f"{df['uplink_mbps'].median():.2f}"
                ]
            }
            st.dataframe(pd.DataFrame(throughput_stats), use_container_width=True, hide_index=True)
        
        with col2:
            # Estatísticas Diárias
            daily_df = calculate_daily_usage(df, max_gap, time_range)
            if not daily_df.empty:
                st.markdown("**📊 Estatísticas Diárias**")
                daily_stats = {
                    'Métrica': [
                        'Maior consumo diário',
                        'Menor consumo diário', 
                        'Média diária',
                        'Total de dias analisados'
                    ],
                    'Valor': [
                        f"{daily_df['total_gb'].max():.2f} GB",
                        f"{daily_df['total_gb'].min():.2f} GB",
                        f"{daily_df['total_gb'].mean():.2f} GB",
                        f"{len(daily_df)} dias"
                    ]
                }
                st.dataframe(pd.DataFrame(daily_stats), use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma estatística diária disponível")
        
        # Resumo por dispositivo
        if len(selected_devices) > 1:
            st.subheader("📱 Resumo por Dispositivo")
            device_summary = get_device_summary(df)
            
            if device_summary:
                summary_data = []
                for device, info in device_summary.items():
                    summary_data.append({
                        'Dispositivo': info['name'],
                        'Registros': info['total_records'],
                        'Período': f"{info['period_start'].strftime('%d/%m %H:%M')} - {info['period_end'].strftime('%d/%m %H:%M')}",
                        'Download Médio (Mbps)': f"{info['avg_download_mbps']:.2f}",
                        'Upload Médio (Mbps)': f"{info['avg_upload_mbps']:.2f}"
                    })
                
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)
        
        # Gráficos
        st.subheader("📈 Gráficos")
        
        # Tabs para diferentes visualizações
        tab1, tab2, tab3, tab4 = st.tabs(["⚡ Throughput", "📅 Consumo Diário", "📊 Comparação", "📈 Distribuição"])
        
        with tab1:
            # Throughput ao longo do tempo com múltiplos dispositivos
            fig = go.Figure()
            
            # Cores para diferentes dispositivos
            colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
            
            for i, device in enumerate(df['device'].unique()):
                device_df = df[df['device'] == device]
                device_name = get_device_display_name(device)
                color = colors[i % len(colors)]
                
                fig.add_trace(go.Scatter(
                    x=device_df['timestamp'], 
                    y=device_df['downlink_mbps'], 
                    name=f'{device_name} - Download',
                    line=dict(color=color, width=2),
                    mode='lines'
                ))
                fig.add_trace(go.Scatter(
                    x=device_df['timestamp'], 
                    y=device_df['uplink_mbps'], 
                    name=f'{device_name} - Upload',
                    line=dict(color=color, width=2, dash='dash'),
                    mode='lines'
                ))
            
            fig.update_layout(
                title="Throughput ao Longo do Tempo",
                xaxis_title="Data/Hora", 
                yaxis_title="Mbps",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            # Consumo diário por dispositivo
            daily_df = calculate_daily_usage(df, max_gap, time_range)
            
            if not daily_df.empty:
                # Gráfico de barras do consumo diário por dispositivo
                fig_daily = go.Figure()
                
                for device in daily_df['device'].unique():
                    device_daily = daily_df[daily_df['device'] == device]
                    device_name = get_device_display_name(device)
                    
                    fig_daily.add_trace(go.Bar(
                        x=device_daily['date'], 
                        y=device_daily['download_gb'], 
                        name=f'{device_name} - Download',
                        text=[f"{x:.2f}" for x in device_daily['download_gb']],
                        textposition='auto'
                    ))
                    fig_daily.add_trace(go.Bar(
                        x=device_daily['date'], 
                        y=device_daily['upload_gb'], 
                        name=f'{device_name} - Upload',
                        text=[f"{x:.2f}" for x in device_daily['upload_gb']],
                        textposition='auto'
                    ))
                
                fig_daily.update_layout(
                    title="Consumo Diário de Dados por Dispositivo (GB)", 
                    xaxis_title="Data", 
                    yaxis_title="Consumo (GB)",
                    barmode='group',
                    showlegend=True
                )
                st.plotly_chart(fig_daily, use_container_width=True)
                
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
                st.plotly_chart(fig_cum, use_container_width=True)
                
                # Tabela de consumo diário
                st.subheader("📋 Tabela de Consumo Diário")
                daily_display = daily_df.copy()
                daily_display['date'] = daily_display['date'].astype(str)
                daily_display = daily_display.round(3)
                st.dataframe(daily_display, use_container_width=True)
            else:
                st.warning("Não foi possível calcular o consumo diário")
        
        with tab3:
            # Comparação entre dispositivos
            if len(selected_devices) > 1:
                st.subheader("📊 Comparação entre Dispositivos")
                
                # Gráfico de comparação de throughput médio
                device_stats = []
                for device in df['device'].unique():
                    device_df = df[df['device'] == device]
                    device_name = get_device_display_name(device)
                    device_stats.append({
                        'Dispositivo': device_name,
                        'Download Médio (Mbps)': device_df['downlink_mbps'].mean(),
                        'Upload Médio (Mbps)': device_df['uplink_mbps'].mean(),
                        'Download Máximo (Mbps)': device_df['downlink_mbps'].max(),
                        'Upload Máximo (Mbps)': device_df['uplink_mbps'].max(),
                        'Registros': len(device_df)
                    })
                
                stats_df = pd.DataFrame(device_stats)
                
                # Gráfico de comparação
                fig_compare = go.Figure()
                
                devices = stats_df['Dispositivo'].tolist()
                download_avg = stats_df['Download Médio (Mbps)'].tolist()
                upload_avg = stats_df['Upload Médio (Mbps)'].tolist()
                
                fig_compare.add_trace(go.Bar(
                    name='Download Médio',
                    x=devices,
                    y=download_avg,
                    marker_color='blue'
                ))
                
                fig_compare.add_trace(go.Bar(
                    name='Upload Médio',
                    x=devices,
                    y=upload_avg,
                    marker_color='red'
                ))
                
                fig_compare.update_layout(
                    title="Comparação de Throughput Médio por Dispositivo",
                    xaxis_title="Dispositivo",
                    yaxis_title="Throughput (Mbps)",
                    barmode='group'
                )
                st.plotly_chart(fig_compare, use_container_width=True)
                
                # Tabela comparativa
                st.subheader("📋 Tabela Comparativa")
                st.dataframe(stats_df, use_container_width=True)
            else:
                st.info("Selecione múltiplos dispositivos para ver comparações")
        
        with tab4:
            # Gráficos de distribuição
            col1, col2 = st.columns(2)
            
            with col1:
                fig_hist = px.histogram(df, x='downlink_mbps', 
                                      title='Distribuição Download (Mbps) por Dispositivo', 
                                      nbins=20)
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                fig_hist = px.histogram(df, x='uplink_mbps', 
                                      title='Distribuição Upload (Mbps) por Dispositivo', 
                                      nbins=20)
                st.plotly_chart(fig_hist, use_container_width=True)
        
        # Botão de exportação PDF
        st.sidebar.markdown("---")
        st.sidebar.header("📄 Exportar Relatório")
        
        # Botão de exportação PDF
        if st.sidebar.button("📄 Gerar Relatório PDF", type="primary"):
            with st.spinner("Gerando relatório PDF..."):
                try:
                    # Calcula dados diários para o PDF
                    daily_df = calculate_daily_usage(df, max_gap, time_range)
                    
                    # Informações dos dispositivos
                    device_names = [get_device_display_name(d) for d in selected_devices]
                    file_info = {
                        'filename': f"Dispositivos: {', '.join(device_names)}",
                        'period': f"{df['timestamp'].min().strftime('%d/%m/%Y')} - {df['timestamp'].max().strftime('%d/%m/%Y')}",
                        'total_records': len(df)
                    }
                    
                    # Informações de uso total
                    total_usage_info = {
                        'download_gb': download_gb,
                        'upload_gb': upload_gb,
                        'total_gb': download_gb + upload_gb,
                        'gaps': gaps
                    }
                    
                    # Gera PDF
                    pdf_path = generate_pdf_report(df, daily_df, file_info, total_usage_info)
                    
                    # Lê o arquivo PDF e oferece download
                    with open(pdf_path, "rb") as pdf_file:
                        pdf_bytes = pdf_file.read()
                    
                    st.sidebar.success("✅ Relatório PDF gerado!")
                    st.sidebar.download_button(
                        label="📥 Baixar PDF",
                        data=pdf_bytes,
                        file_name=f"starlink_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                    
                    # Remove arquivo temporário
                    os.remove(pdf_path)
                    
                except Exception as e:
                    st.sidebar.error(f"❌ Erro ao gerar PDF: {str(e)}")
    else:
        st.warning("⚠️ Nenhum dado encontrado para os parâmetros selecionados")
else:
    st.info("👆 Selecione pelo menos um dispositivo para começar a análise")
