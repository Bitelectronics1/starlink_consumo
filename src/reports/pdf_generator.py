#!/usr/bin/env python3
"""
Gerador de Relatórios PDF para Análise de Dados Starlink
"""

import io
import base64
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import plotly.graph_objects as go
import plotly.io as pio
from plotly.utils import PlotlyJSONEncoder
import json

class StarlinkPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Configura estilos personalizados para o PDF."""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        
        # Cabeçalho de seção
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            textColor=colors.darkgreen
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
        
        # Texto de métrica
        self.styles.add(ParagraphStyle(
            name='MetricText',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=4,
            textColor=colors.darkred,
            alignment=TA_CENTER
        ))

    def plotly_to_image(self, fig, width=800, height=400):
        """Converte gráfico Plotly para imagem."""
        try:
            # Converte para imagem PNG
            img_bytes = pio.to_image(fig, format="png", width=width, height=height)
            return Image(io.BytesIO(img_bytes), width=width*0.75, height=height*0.75)
        except Exception as e:
            print(f"Erro ao converter gráfico: {e}")
            return None

    def create_throughput_chart(self, df, title="Throughput em Tempo Real"):
        """Cria gráfico de throughput."""
        if df.empty:
            return None
            
        fig = go.Figure()
        
        # Adiciona linhas de throughput
        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=df['downlink_mbps'], 
            mode='lines',
            name='Download (Mbps)',
            line=dict(color='blue', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=df['uplink_mbps'], 
            mode='lines',
            name='Upload (Mbps)',
            line=dict(color='red', width=2)
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Timestamp',
            yaxis_title='Throughput (Mbps)',
            hovermode='x unified',
            showlegend=True,
            width=800,
            height=400
        )
        
        return self.plotly_to_image(fig)

    def create_daily_consumption_chart(self, daily_df, title="Consumo Diário de Dados"):
        """Cria gráfico de consumo diário."""
        if daily_df.empty:
            return None
            
        fig = go.Figure()
        
        # Gráfico de barras
        fig.add_trace(go.Bar(
            x=daily_df['date'], 
            y=daily_df['download_gb'], 
            name='Download (GB)',
            marker_color='blue',
            text=[f"{x:.2f}" for x in daily_df['download_gb']],
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            x=daily_df['date'], 
            y=daily_df['upload_gb'], 
            name='Upload (GB)',
            marker_color='red',
            text=[f"{x:.2f}" for x in daily_df['upload_gb']],
            textposition='auto'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Data',
            yaxis_title='Consumo (GB)',
            barmode='group',
            showlegend=True,
            width=800,
            height=400
        )
        
        return self.plotly_to_image(fig)

    def create_cumulative_chart(self, daily_df, title="Consumo Acumulado"):
        """Cria gráfico de consumo acumulado."""
        if daily_df.empty:
            return None
            
        # Calcula valores acumulados
        daily_df = daily_df.copy()
        daily_df['download_cumulative'] = daily_df['download_gb'].cumsum()
        daily_df['upload_cumulative'] = daily_df['upload_gb'].cumsum()
        daily_df['total_cumulative'] = daily_df['total_gb'].cumsum()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_df['date'], 
            y=daily_df['download_cumulative'], 
            mode='lines+markers',
            name='Download Acumulado (GB)',
            line=dict(color='blue', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_df['date'], 
            y=daily_df['upload_cumulative'], 
            mode='lines+markers',
            name='Upload Acumulado (GB)',
            line=dict(color='red', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_df['date'], 
            y=daily_df['total_cumulative'], 
            mode='lines+markers',
            name='Total Acumulado (GB)',
            line=dict(color='green', width=3)
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Data',
            yaxis_title='Consumo Acumulado (GB)',
            showlegend=True,
            width=800,
            height=400
        )
        
        return self.plotly_to_image(fig)

    def create_distribution_chart(self, df, column, title, color='blue'):
        """Cria gráfico de distribuição."""
        if df.empty or column not in df.columns:
            return None
            
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=df[column],
            nbinsx=20,
            name=title,
            marker_color=color
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=column.replace('_', ' ').title(),
            yaxis_title='Frequência',
            width=400,
            height=300
        )
        
        return self.plotly_to_image(fig)

    def generate_pdf_report(self, 
                          df: pd.DataFrame, 
                          daily_df: pd.DataFrame,
                          file_info: Dict,
                          total_usage: Dict = None,
                          output_path: str = "starlink_report.pdf"):
        """Gera relatório PDF completo."""
        
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Título principal
        story.append(Paragraph("🚀 RELATÓRIO DE ANÁLISE STARLINK", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Informações do arquivo
        story.append(Paragraph("📊 Informações do Arquivo", self.styles['CustomHeading1']))
        story.append(Paragraph(f"<b>Arquivo:</b> {file_info.get('filename', 'N/A')}", self.styles['CustomNormal']))
        story.append(Paragraph(f"<b>Data de Geração:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", self.styles['CustomNormal']))
        story.append(Paragraph(f"<b>Total de Registros:</b> {len(df):,}", self.styles['CustomNormal']))
        story.append(Paragraph(f"<b>Período:</b> {file_info.get('period', 'N/A')}", self.styles['CustomNormal']))
        story.append(Spacer(1, 20))
        
        # Métricas principais (como na interface)
        if total_usage:
            story.append(Paragraph("📊 Métricas Principais", self.styles['CustomHeading1']))
            
            # Tabela de métricas principais
            metrics_data = [
                ['Métrica', 'Valor'],
                ['Download', f"{total_usage.get('download_gb', 0):.2f} GB"],
                ['Upload', f"{total_usage.get('upload_gb', 0):.2f} GB"],
                ['Total', f"{total_usage.get('total_gb', 0):.2f} GB"],
                ['Gaps Detectados', str(total_usage.get('gaps', 0))],
                ['Registros Processados', f"{len(df):,}"]
            ]
            
            metrics_table = Table(metrics_data)
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(metrics_table)
            story.append(Spacer(1, 20))
        
        # Estatísticas de throughput
        if not df.empty:
            story.append(Paragraph("📈 Estatísticas de Throughput", self.styles['CustomHeading1']))
            
            # Tabela de estatísticas
            stats_data = [
                ['Métrica', 'Download (Mbps)', 'Upload (Mbps)'],
                ['Média', f"{df['downlink_mbps'].mean():.2f}", f"{df['uplink_mbps'].mean():.2f}"],
                ['Máximo', f"{df['downlink_mbps'].max():.2f}", f"{df['uplink_mbps'].max():.2f}"],
                ['Mínimo', f"{df['downlink_mbps'].min():.2f}", f"{df['uplink_mbps'].min():.2f}"],
                ['Mediana', f"{df['downlink_mbps'].median():.2f}", f"{df['uplink_mbps'].median():.2f}"]
            ]
            
            stats_table = Table(stats_data)
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(stats_table)
            story.append(Spacer(1, 20))
        
        # Seção: Aba Throughput
        story.append(Paragraph("⚡ ABA: THROUGHPUT", self.styles['CustomHeading1']))
        story.append(Paragraph("Throughput ao Longo do Tempo", self.styles['CustomHeading2']))
        
        # Gráfico de throughput
        throughput_chart = self.create_throughput_chart(df)
        if throughput_chart:
            story.append(throughput_chart)
            story.append(Spacer(1, 20))
        else:
            story.append(Paragraph("⚠️ Gráfico de throughput não disponível", self.styles['CustomNormal']))
            story.append(Spacer(1, 20))
        
        # Seção: Aba Consumo Diário
        if not daily_df.empty:
            story.append(Paragraph("📅 ABA: CONSUMO DIÁRIO", self.styles['CustomHeading1']))
            
            # Gráfico de consumo diário
            daily_chart = self.create_daily_consumption_chart(daily_df)
            if daily_chart:
                story.append(Paragraph("Consumo Diário por Tipo", self.styles['CustomHeading2']))
                story.append(daily_chart)
                story.append(Spacer(1, 20))
            
            # Gráfico acumulado
            cumulative_chart = self.create_cumulative_chart(daily_df)
            if cumulative_chart:
                story.append(Paragraph("Consumo Acumulado", self.styles['CustomHeading2']))
                story.append(cumulative_chart)
                story.append(Spacer(1, 20))
            
            # Tabela de consumo diário
            story.append(Paragraph("Tabela de Consumo Diário", self.styles['CustomHeading2']))
            
            # Prepara dados da tabela
            table_data = [['Data', 'Download (GB)', 'Upload (GB)', 'Total (GB)', 'Gaps', 'Registros']]
            for _, row in daily_df.iterrows():
                table_data.append([
                    str(row['date']),
                    f"{row['download_gb']:.3f}",
                    f"{row['upload_gb']:.3f}",
                    f"{row['total_gb']:.3f}",
                    str(row['gaps']),
                    str(row['records'])
                ])
            
            daily_table = Table(table_data)
            daily_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(daily_table)
            story.append(Spacer(1, 20))
            
            # Estatísticas diárias
            story.append(Paragraph("📊 Estatísticas Diárias", self.styles['CustomHeading2']))
            daily_stats = [
                f"<b>Maior consumo diário:</b> {daily_df['total_gb'].max():.2f} GB",
                f"<b>Menor consumo diário:</b> {daily_df['total_gb'].min():.2f} GB",
                f"<b>Média diária:</b> {daily_df['total_gb'].mean():.2f} GB",
                f"<b>Total de dias analisados:</b> {len(daily_df)} dias"
            ]
            
            for stat in daily_stats:
                story.append(Paragraph(stat, self.styles['CustomNormal']))
            
            story.append(Spacer(1, 20))
        
        # Seção: Aba Distribuição
        if not df.empty:
            story.append(Paragraph("📊 ABA: DISTRIBUIÇÃO", self.styles['CustomHeading1']))
            
            # Cria duas colunas para os gráficos de distribuição
            col1_data = self.create_distribution_chart(df, 'downlink_mbps', 'Distribuição Download (Mbps)', 'blue')
            col2_data = self.create_distribution_chart(df, 'uplink_mbps', 'Distribuição Upload (Mbps)', 'red')
            
            if col1_data and col2_data:
                # Tabela com duas colunas para os gráficos
                dist_table = Table([[col1_data, col2_data]], colWidths=[4*inch, 4*inch])
                dist_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                ]))
                story.append(dist_table)
                story.append(Spacer(1, 20))
        
        # Resumo final
        story.append(Paragraph("📋 Resumo Executivo", self.styles['CustomHeading1']))
        
        if not daily_df.empty:
            total_download = daily_df['download_gb'].sum()
            total_upload = daily_df['upload_gb'].sum()
            total_consumption = total_download + total_upload
            
            summary_text = f"""
            <b>Consumo Total de Dados:</b><br/>
            • Download: {total_download:.2f} GB<br/>
            • Upload: {total_upload:.2f} GB<br/>
            • Total: {total_consumption:.2f} GB<br/><br/>
            
            <b>Período de Análise:</b> {len(daily_df)} dias<br/>
            <b>Média Diária:</b> {total_consumption/len(daily_df):.2f} GB/dia<br/>
            <b>Arquivo Analisado:</b> {file_info.get('filename', 'N/A')}
            """
        else:
            summary_text = f"""
            <b>Arquivo Analisado:</b> {file_info.get('filename', 'N/A')}<br/>
            <b>Registros Processados:</b> {len(df):,}<br/>
            <b>Status:</b> Dados processados com sucesso
            """
        
        story.append(Paragraph(summary_text, self.styles['CustomNormal']))
        
        # Rodapé
        story.append(Spacer(1, 30))
        story.append(Paragraph("Relatório gerado automaticamente pelo Starlink Data Analyzer", 
                              self.styles['CustomNormal']))
        
        # Gera o PDF
        doc.build(story)
        return output_path

def generate_pdf_report(df, daily_df, file_info, total_usage=None, output_path="starlink_report.pdf"):
    """Função de conveniência para gerar relatório PDF."""
    generator = StarlinkPDFGenerator()
    return generator.generate_pdf_report(df, daily_df, file_info, total_usage, output_path)
