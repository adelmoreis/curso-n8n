@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Curso n8n - Agente3D
set IP=
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do if not defined IP set IP=%%a
set IP=%IP: =%
echo.
echo  ==========================================
echo   CURSO N8N - Agente3D  (deixe esta janela aberta)
echo  ==========================================
echo   No seu PC:            http://localhost:8080
echo   Em outros aparelhos:  http://%IP%:8080
echo   Gestor:               http://localhost:8080/gestor.html
echo   Dados protegidos em:  pasta "dados" (nao apague)
echo  ==========================================
echo.
start "" cmd /c "timeout /t 2 >nul & start http://localhost:8080"
python --version >nul 2>nul
if %errorlevel%==0 ( python servidor_dados.py & goto fim )
py --version >nul 2>nul
if %errorlevel%==0 ( py servidor_dados.py & goto fim )
echo.
echo  ATENCAO: o Python nao foi encontrado. O curso abre, mas SEM o banco de dados protegido.
echo  Instale o Python (python.org) para guardar alunos e progresso em arquivo.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0servidor.ps1"
:fim
pause
