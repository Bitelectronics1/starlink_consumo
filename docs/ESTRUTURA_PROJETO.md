# 📁 Estrutura do Projeto Starlink_Consumo

## 🎯 Organização por Funcionalidade

O projeto foi reorganizado seguindo uma estrutura modular e clara, separando as responsabilidades por pastas:

### 🌐 **src/web/** - Interfaces Web
- **app_simple.py** - Aplicação principal Streamlit com análise completa
- **daily_gb_viewer.py** - Visualizador focado em consumo diário

### 🔌 **src/database/** - Integração com InfluxDB
- **influx_client.py** - Cliente para conexão e consultas no InfluxDB
- **test_influx_connection.py** - Script de teste de conexão

### 📊 **src/reports/** - Geradores de Relatórios
- **pdf_generator.py** - Gerador de relatórios PDF com gráficos

### ⚙️ **src/config/** - Configurações
- **influx_config.py** - Configurações do InfluxDB e queries Flux

### 🚀 **scripts/** - Scripts de Execução
- **run_app.cmd** - Executa a aplicação principal
- **run_daily_viewer.cmd** - Executa o visualizador diário

### 📚 **docs/** - Documentação
- **README.md** - Documentação principal
- **CONFIGURACAO_INFLUXDB.md** - Guia de configuração
- **DETECCAO_DINAMICA_DISPOSITIVOS.md** - Funcionalidades
- **ESTRUTURA_PROJETO.md** - Este arquivo

## 🔄 Fluxo de Dados

```
InfluxDB → src/database/influx_client.py → src/web/app_simple.py → Interface
                ↓
        src/config/influx_config.py (configurações)
                ↓
        src/reports/pdf_generator.py (relatórios)
```

## 🎯 Benefícios da Nova Estrutura

1. **Separação de Responsabilidades** - Cada pasta tem uma função específica
2. **Manutenibilidade** - Código mais fácil de manter e modificar
3. **Escalabilidade** - Estrutura preparada para crescimento
4. **Organização** - Arquivos relacionados agrupados logicamente
5. **Imports Limpos** - Estrutura de pacotes Python adequada

## 🚀 Como Executar

```bash
# Aplicação principal
scripts/run_app.cmd

# Visualizador diário
scripts/run_daily_viewer.cmd

# Teste de conexão
python src/database/test_influx_connection.py
```
