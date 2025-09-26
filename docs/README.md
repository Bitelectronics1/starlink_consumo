# 🚀 Starlink GB - Analisador de Dados

Sistema completo para análise de consumo de dados de antenas Starlink via InfluxDB, com interface web intuitiva, comparação entre dispositivos e relatórios detalhados.

## 📁 Estrutura do Projeto

```
Starlink_Consumo/
├── 🌐 src/web/                 # Interfaces Web Streamlit
│   ├── app_simple.py           # Aplicação principal Streamlit (InfluxDB)
│   └── daily_gb_viewer.py      # Visualizador de consumo diário (InfluxDB)
├── 🔌 src/database/            # Integração com InfluxDB
│   ├── influx_client.py        # Cliente para conexão InfluxDB
│   └── test_influx_connection.py # Teste de conexão
├── 📊 src/reports/             # Geradores de Relatórios
│   └── pdf_generator.py        # Gerador de relatórios PDF (unificado)
├── ⚙️ src/config/              # Configurações do Sistema
│   └── influx_config.py        # Configuração e queries Flux
├── 🚀 scripts/                 # Scripts de Execução
│   ├── run_app.cmd             # Executar aplicação principal
│   └── run_daily_viewer.cmd    # Executar visualizador diário
├── 📚 docs/                    # Documentação
│   ├── CONFIGURACAO_INFLUXDB.md # Guia de configuração InfluxDB
│   ├── DETECCAO_DINAMICA_DISPOSITIVOS.md # Documentação de funcionalidades
│   └── README.md               # Este arquivo
├── ⚙️ CONFIGURAÇÃO:
│   ├── pyproject.toml          # Configuração do projeto Python
│   └── requirements.txt        # Dependências Python
```

## 🚀 Instalação Rápida

### 🐳 **Opção 1: Docker (Recomendado para VPS)**
```bash
# 1. Configurar variáveis de ambiente
cp env.example .env
# Editar .env com seu token InfluxDB

# 2. Deploy automático
./scripts/deploy.sh

# 3. Acessar aplicação
# http://localhost:8501 (aplicação principal)
# http://localhost:8502 (visualizador diário)
```

### 💻 **Opção 2: Instalação Local**
```bash
# 1. Instalar dependências
python -m pip install -r requirements.txt

# 2. Configurar token InfluxDB
$env:INFLUXDB_TOKEN="seu_token_aqui"

# 3. Testar conexão (opcional)
python src/database/test_influx_connection.py

# 4. Iniciar aplicação web
scripts/run_app.cmd
```

## 📱 Interfaces Disponíveis

### 🌐 **Interface Web Principal** (Recomendado)
```bash
scripts/run_app.cmd
```
**Funcionalidades:**
- ✅ Conexão direta com InfluxDB
- ✅ Seleção múltipla de dispositivos Bit Star
- ✅ Períodos flexíveis (hora até mês + personalizado)
- ✅ Gráficos interativos com Plotly
- ✅ Análise de throughput em tempo real
- ✅ Consumo diário com gráficos de barras
- ✅ Comparação entre múltiplos dispositivos
- ✅ Configuração de gaps via slider
- ✅ Relatórios PDF com dados do InfluxDB

### 📊 **Visualizador de Consumo Diário**
```bash
scripts/run_daily_viewer.cmd
```
**Funcionalidades:**
- ✅ Foco exclusivo no consumo diário em GB
- ✅ Conexão direta com InfluxDB
- ✅ Comparação entre múltiplos dispositivos
- ✅ Gráficos de barras com valores em GB
- ✅ Gráfico acumulativo de consumo por dispositivo
- ✅ Tabela detalhada de dados diários
- ✅ Estatísticas de consumo por dispositivo

## 💻 Uso das Aplicações

### 🌐 **Interface Web Principal**
```bash
# Executa a aplicação principal
scripts/run_app.cmd
```

### 📊 **Visualizador de Consumo Diário**
```bash
# Executa o visualizador focado em consumo diário
scripts/run_daily_viewer.cmd
```

## 🎯 Funcionalidades Principais

### 📊 **Análise de Dados Starlink**
- ✅ **Conexão direta com InfluxDB** para dados em tempo real
- ✅ **Extração de throughput** (download/upload) em bps
- ✅ **Cálculo de consumo** em GB com precisão
- ✅ **Detecção de gaps** configuráveis (>5 min por padrão)
- ✅ **Análise temporal** com timestamps precisos
- ✅ **Tratamento de erros** robusto

### 📈 **Visualizações Interativas**
- ✅ **Gráficos de throughput** em tempo real
- ✅ **Consumo diário** com gráficos de barras
- ✅ **Gráficos acumulativos** de consumo total
- ✅ **Distribuição de dados** com histogramas
- ✅ **Comparativo entre arquivos** múltiplos
- ✅ **Zoom e interação** nos gráficos

### 📋 **Relatórios e Métricas**
- ✅ **Relatórios detalhados** por arquivo
- ✅ **Consumo diário** com tabelas completas
- ✅ **Estatísticas de Throughput** (média, máximo, mínimo, mediana)
- ✅ **Estatísticas Diárias** (maior/menor consumo, média, total de dias)
- ✅ **Métricas em tempo real** na interface
- ✅ **Exportação** de relatórios em PDF
- ✅ **Relatórios consolidados** de múltiplos arquivos
- ✅ **Gráficos de consumo acumulado** para análise de tendências

### 🌐 **Interface Web Avançada**
- ✅ **Seleção múltipla** de dispositivos Bit Star
- ✅ **Configuração dinâmica** de parâmetros
- ✅ **Navegação por abas** intuitiva
- ✅ **Responsividade** para diferentes telas
- ✅ **Detecção automática** de dispositivos

## 📋 Requisitos do Sistema

- **Python:** 3.12+
- **Bibliotecas:** pandas, numpy, streamlit, plotly
- **Sistema:** Windows 10/11 (testado)
- **Memória:** Mínimo 4GB RAM
- **Espaço:** 100MB para instalação

## 🚀 Início Rápido

### **Opção 1: Interface Web (Recomendado)**
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Iniciar aplicação principal
scripts/run_app.cmd

# 3. Acessar: http://localhost:8501
```

### **Opção 2: Visualizador de Consumo Diário**
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Iniciar visualizador diário
scripts/run_daily_viewer.cmd

# 3. Acessar: http://localhost:8501
```

### **Opção 3: Executáveis (Futuro)**
```bash
# Em desenvolvimento - executáveis standalone
# Será implementado conforme necessário
```

## 📖 Guia de Uso

### **1. Configuração do InfluxDB**
- Configure o token do InfluxDB: `$env:INFLUXDB_TOKEN="seu_token"`
- Verifique a conexão: `python src/database/test_influx_connection.py`
- Os dados devem estar no bucket `starlink_data` com tag `device`

### **2. Análise via Interface Web**
1. Execute `scripts/run_app.cmd`
2. Selecione dispositivos na barra lateral
3. Escolha o período de análise
4. Configure o gap máximo (padrão: 5 min)
5. Visualize os gráficos e relatórios
6. Use as abas para diferentes visualizações

### **3. Análise de Consumo Diário**
1. Execute `scripts/run_daily_viewer.cmd`
2. Foco exclusivo no consumo em GB
3. Gráficos de barras e acumulativos
4. Tabela detalhada de dados diários

## 🔧 Configurações Avançadas

### **Gap de Descontinuidade**
- **Padrão:** 5 minutos
- **Função:** Ignora intervalos maiores que o gap
- **Configuração:** Slider na interface web

### **Formato de Dados InfluxDB**
- **Bucket:** `starlink_data`
- **Medição:** `starlink_data`
- **Campos necessários:** `downlinkThroughputBps`, `uplinkThroughputBps`
- **Tag necessária:** `device` (ID do dispositivo)

## 📊 Exemplos de Saída

### **Consumo Diário (GB)**
```
Data         | Download (GB) | Upload (GB) | Total (GB)
2025-08-21   | 1.234         | 0.567       | 1.801
2025-08-22   | 2.145         | 0.789       | 2.934
```

### **Estatísticas**
- **Maior consumo diário:** 2.934 GB
- **Menor consumo diário:** 0.123 GB
- **Média diária:** 1.456 GB

## 🆘 Solução de Problemas

### **Erro: "Token do InfluxDB não configurado"**
- Configure a variável `INFLUXDB_TOKEN`
- Execute: `$env:INFLUXDB_TOKEN="seu_token"`

### **Erro: "Nenhum dispositivo encontrado"**
- Verifique se há dados no bucket `starlink_data`
- Confirme se a tag `device` está presente nos dados
- Verifique se há dados nos últimos 7 dias

### **Aplicação não inicia**
- Execute `pip install -r requirements.txt` para instalar dependências
- Verifique se Python 3.12+ está instalado

### **Gráficos não aparecem**
- Aguarde o processamento dos dados
- Verifique se há dados válidos no arquivo

## 📞 Suporte

- **Documentação:** Este README.md
- **Scripts de teste:** Execute os comandos de exemplo
- **Logs de erro:** Verifique a saída do terminal

## 🔌 Integração InfluxDB

### ✅ **Funcionalidades Implementadas**
- [x] Conexão direta com InfluxDB
- [x] Queries Flux otimizadas para dados Starlink
- [x] Seleção múltipla de dispositivos Bit Star
- [x] Períodos flexíveis (hora até mês + personalizado)
- [x] Comparação entre múltiplos dispositivos
- [x] Relatórios PDF com dados do InfluxDB
- [x] Teste de conexão automatizado

### 📊 **Detecção Dinâmica de Dispositivos**
- ✅ **Detecção automática** de Bit Stars disponíveis no InfluxDB
- ✅ **Nomes dinâmicos** baseados nos IDs dos dispositivos
- ✅ **Atualização em tempo real** da lista de dispositivos
- ✅ **Suporte a novos dispositivos** sem necessidade de modificação do código

### ⏰ **Períodos Disponíveis**
- Última hora
- Últimas 6 horas
- Últimas 12 horas
- Último dia
- Últimos 3 dias
- Última semana
- Últimos 15 dias
- Último mês
- **Personalizado** (data início e fim)

### 🔍 **Queries Flux Utilizadas**
```flux
# Query principal para throughput
from(bucket: "starlink_data")
|> range(start: -24h)
|> filter(fn: (r) => r._measurement == "starlink_data")
|> filter(fn: (r) => r.device == "bit1015star" or r.device == "bit1087star")
|> filter(fn: (r) => r._field == "downlinkThroughputBps" or r._field == "uplinkThroughputBps")
|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
|> sort(columns: ["_time"])
```

## 🐳 Deploy Docker

Para hospedar na VPS, consulte o guia completo:
- **[DOCKER_DEPLOY.md](docs/DOCKER_DEPLOY.md)** - Deploy completo com Docker

### Comandos Rápidos Docker
```bash
# Deploy automático
./scripts/deploy.sh

# Iniciar containers
./scripts/start.sh

# Parar containers
./scripts/stop.sh

# Ver logs
./scripts/logs.sh
```

## 🎯 Próximas Funcionalidades

- [x] Exportação de relatórios em PDF
- [x] Integração com InfluxDB
- [x] Comparação entre dispositivos
- [x] Deploy Docker para VPS
- [ ] Análise de tendências temporais
- [ ] Alertas de consumo excessivo
- [ ] Integração com APIs do Starlink
- [ ] Dashboard em tempo real
- [ ] Executáveis standalone

---

**🚀 Starlink Data Analyzer** - Desenvolvido para análise precisa de consumo de dados de antenas Starlink
# consumo_dados_starlink
# consumo_dados_starlink
