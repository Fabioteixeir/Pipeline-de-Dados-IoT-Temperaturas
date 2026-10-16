@echo off
cd /d "%~dp0"
echo ============================================
echo  Pipeline IoT - com PostgreSQL no Docker
echo  (abra o Docker Desktop antes)
echo ============================================
rem O ambiente Python fica numa pasta curta para evitar o erro WinError 206 (caminho muito longo)
set "VENV=%LOCALAPPDATA%\pipeline-iot-venv"
set "PY=%VENV%\Scripts\python.exe"
if exist "%PY%" goto instalar
python -m venv "%VENV%"
if errorlevel 1 py -m venv "%VENV%"
if not exist "%PY%" goto erro
:instalar
"%PY%" -m pip install -r requirements.txt
if errorlevel 1 goto erro
if exist "%USERPROFILE%\.streamlit\credentials.toml" goto semcred
mkdir "%USERPROFILE%\.streamlit" 2>nul
> "%USERPROFILE%\.streamlit\credentials.toml" echo [general]
>> "%USERPROFILE%\.streamlit\credentials.toml" echo email = ""
:semcred
docker compose up -d
if errorlevel 1 goto erro
echo Aguardando o banco iniciar...
timeout /t 10 /nobreak >nul
"%PY%" src\pipeline.py
if errorlevel 1 goto erro
"%PY%" -m streamlit run src\dashboard.py
goto fim
:erro
echo.
echo ERRO: copie a mensagem acima e envie para o suporte.
:fim
pause
