@echo off
REM Script de deploy para Windows - Starlink Data Analyzer
REM Uso: scripts\deploy.bat

echo 🚀 Iniciando deploy do Starlink Data Analyzer...

REM Verifica se Docker está instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker não está instalado.
    echo Baixe e instale o Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Verifica se Docker Compose está instalado
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose não está instalado.
    echo Instale o Docker Desktop que inclui o Docker Compose.
    pause
    exit /b 1
)

REM Verifica se arquivo .env existe
if not exist .env (
    echo ❌ Arquivo .env não encontrado. Copiando env.example...
    copy env.example .env
    echo ⚠️ Configure o arquivo .env com suas credenciais antes de continuar.
    echo Edite: notepad .env
    pause
    exit /b 1
)

REM Para containers existentes
echo 🛑 Parando containers existentes...
docker-compose down

REM Remove imagens antigas
echo 🧹 Limpando imagens antigas...
docker-compose down --rmi all

REM Build e start dos containers
echo 🔨 Fazendo build das imagens...
docker-compose build --no-cache

echo 🚀 Iniciando containers...
docker-compose up -d

REM Verifica status dos containers
echo 📊 Verificando status dos containers...
docker-compose ps

REM Mostra logs
echo 📋 Logs dos containers:
docker-compose logs --tail=20

echo.
echo ✅ Deploy concluído!
echo 🌐 Aplicação principal: http://localhost:8501
echo 📊 Visualizador diário: http://localhost:8502
echo.
echo Para ver logs em tempo real:
echo docker-compose logs -f
echo.
echo Para parar os containers:
echo docker-compose down

pause
