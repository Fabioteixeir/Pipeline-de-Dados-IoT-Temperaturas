@echo off
cd /d "%~dp0"
echo ============================================
echo  Pipeline IoT - modo simples (sem Docker)
echo ============================================
rem O ambiente Python fica numa pasta curta para evitar o erro WinError 206 (caminho muito longo)
set "VENV=%LOCALAPPDATA%\pipeline-iot-venv"
set "PY=%VENV%\Scripts\python.exe"
if exist "%PY%" goto instalar
echo Criando ambiente Python...
python -m venv "%VENV%"
if errorlevel 1 py -m venv "%VENV%"
if not exist "%PY%" goto erro
:instalar
echo Instalando bibliotecas (pode demorar na primeira vez)...
"%PY%" -m pip install -r requirements.txt
if errorlevel 1 goto erro
if exist "%USERPROFILE%\.streamlit\credentials.toml" goto semcred
mkdir "%USERPROFILE%\.streamlit" 2>nul
> "%USERPROFILE%\.streamlit\credentials.toml" echo [general]
>> "%USERPROFILE%\.streamlit\credentials.toml" echo email = ""
:semcred
set "DATABASE_URL=sqlite:///iot.db"
echo Importando dados do CSV...
"%PY%" src\pipeline.py
if errorlevel 1 goto erro
echo Abrindo o dashboard. Se o navegador nao abrir, acesse http://localhost:8501
"%PY%" -m streamlit run src\dashboard.py
goto fim
:erro
echo.
echo ERRO: copie a mensagem acima e envie para o suporte.
:fim
pause
