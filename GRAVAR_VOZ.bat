@echo off
cd /d "%~dp0"
echo Gravador de voz em http://localhost:8080/gravador.html
echo Deixe esta janela aberta enquanto grava. Para parar, feche-a.
start "" "http://localhost:8080/gravador.html"
python servidor_vendas.py || py servidor_vendas.py
pause
