@echo off
cd /d "%~dp0"
echo Pagina de vendas em http://localhost:8080/pagina-de-vendas.html
echo Deixe esta janela aberta. Para parar, feche-a.
start "" "http://localhost:8080/pagina-de-vendas.html"
python servidor_vendas.py || py servidor_vendas.py
pause
