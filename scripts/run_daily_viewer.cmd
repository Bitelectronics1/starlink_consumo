@echo off
echo 📊 Iniciando Visualizador de Consumo Diário...
echo.

REM Ativa o ambiente virtual
call .venv\Scripts\activate.bat

REM Instala dependências se necessário
echo 📦 Verificando dependências...
python -m pip install streamlit plotly pandas numpy matplotlib seaborn reportlab kaleido influxdb-client --quiet

REM Inicia a aplicação Streamlit
echo 🌐 Abrindo visualizador de consumo diário...
echo.
echo A aplicação será aberta no seu navegador em: http://localhost:8501
echo.
echo Para parar a aplicação, pressione Ctrl+C
echo.

python -m streamlit run src\web\daily_gb_viewer.py

pause
