# 🔧 Configuração do InfluxDB

## 📋 Pré-requisitos

1. **Token do InfluxDB**: Você precisa do token de acesso ao InfluxDB
2. **Python 3.12+**: Instalado e configurado
3. **Bibliotecas**: Instaladas via `pip install -r requirements.txt`

## ⚙️ Configuração

### 1. Configurar Token do InfluxDB

**Opção A: Variável de Ambiente (Recomendado)**
```bash
# Windows PowerShell
$env:INFLUXDB_TOKEN="seu_token_aqui"

# Windows CMD
set INFLUXDB_TOKEN=seu_token_aqui

# Linux/Mac
export INFLUXDB_TOKEN="seu_token_aqui"
```

**Opção B: Arquivo .env**
Crie um arquivo `.env` na raiz do projeto:
```
INFLUXDB_TOKEN=seu_token_aqui
```

### 2. Verificar Conexão

Execute o comando para testar a conexão:
```bash
python -c "from influx_client import StarlinkInfluxClient; client = StarlinkInfluxClient(); print('Conexão OK!' if client.test_connection() else 'Erro de conexão')"
```

## 🚀 Executar Aplicações

### Aplicação Principal
```bash
run_app.cmd
# ou
streamlit run app_simple.py
```

### Visualizador de Consumo Diário
```bash
run_daily_viewer.cmd
# ou
streamlit run daily_gb_viewer.py
```

## 📊 Funcionalidades

### ✅ **Novas Funcionalidades**
- **Conexão direta com InfluxDB**: Sem necessidade de arquivos CSV
- **Seleção múltipla de dispositivos**: Compare múltiplas Bit Stars
- **Períodos flexíveis**: Última hora até último mês + personalizado
- **Gráficos comparativos**: Visualize dados de múltiplos dispositivos
- **Relatórios PDF**: Exportação com dados do InfluxDB

### 📱 **Dispositivos Suportados**
- **Detecção Dinâmica**: Dispositivos são detectados automaticamente do InfluxDB
- **Nomes Personalizados**: Baseados nos IDs dos dispositivos
- **Suporte a Novos Dispositivos**: Adicionados automaticamente sem modificação do código

### ⏰ **Períodos Disponíveis**
- Última hora
- Últimas 6 horas
- Últimas 12 horas
- Último dia
- Últimos 3 dias
- Última semana
- Últimos 15 dias
- Último mês
- Personalizado

## 🔍 Queries Flux Utilizadas

### Query Principal
```flux
from(bucket: "starlink_data")
|> range(start: -24h)
|> filter(fn: (r) => r._measurement == "starlink_data")
|> filter(fn: (r) => r.device == "bit1015star" or r.device == "bit1087star")
|> filter(fn: (r) => r._field == "downlinkThroughputBps" or r._field == "uplinkThroughputBps")
|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
|> sort(columns: ["_time"])
```

### Query de Consumo Diário
```flux
from(bucket: "starlink_data")
|> range(start: -30d)
|> filter(fn: (r) => r._measurement == "starlink_data")
|> filter(fn: (r) => r.device == "bit1015star" or r.device == "bit1087star")
|> filter(fn: (r) => r._field == "downlinkThroughputBps" or r._field == "uplinkThroughputBps")
|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
|> window(every: 1d)
|> reduce(
    identity: {downlinkThroughputBps: 0.0, uplinkThroughputBps: 0.0, count: 0},
    fn: (r, accumulator) => ({
        downlinkThroughputBps: accumulator.downlinkThroughputBps + r.downlinkThroughputBps,
        uplinkThroughputBps: accumulator.uplinkThroughputBps + r.uplinkThroughputBps,
        count: accumulator.count + 1
    })
)
|> map(fn: (r) => ({
    _time: r._time,
    device: r.device,
    downlinkThroughputBps: r.downlinkThroughputBps / float(v: r.count),
    uplinkThroughputBps: r.uplinkThroughputBps / float(v: r.count)
}))
|> sort(columns: ["_time"])
```

## 🛠️ Solução de Problemas

### Erro: "Token do InfluxDB não configurado"
- Verifique se a variável `INFLUXDB_TOKEN` está definida
- Execute: `echo $env:INFLUXDB_TOKEN` (PowerShell) ou `echo $INFLUXDB_TOKEN` (Linux/Mac)

### Erro: "Não foi possível conectar ao InfluxDB"
- Verifique se o token está correto
- Verifique se a URL do InfluxDB está acessível
- Teste a conexão manualmente

### Erro: "Nenhum dispositivo encontrado"
- Verifique se há dados no bucket `starlink_data`
- Verifique se os dispositivos estão sendo enviados com a tag `device`
- Verifique se os dados estão no período selecionado

## 📞 Suporte

Para problemas específicos:
1. Verifique os logs no terminal
2. Teste a conexão com InfluxDB
3. Verifique se os dados existem no período selecionado
4. Consulte a documentação do InfluxDB
