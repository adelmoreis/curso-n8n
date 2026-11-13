@echo off
chcp 65001 > nul
title Sincronizar Curso N8N do Claude

echo ========================================================
echo       SINCRONIZANDO DO CLAUDE PARA ESTA PASTA
echo ========================================================
echo.
echo Origem : C:\Users\tresd\OneDrive\3Digitos\Claude\Cursos\N8N
echo Destino: C:\Users\tresd\OneDrive\3Digitos\3digitos\cursos\n8n
echo.

robocopy "C:\Users\tresd\OneDrive\3Digitos\Claude\Cursos\N8N" "C:\Users\tresd\OneDrive\3Digitos\3digitos\cursos\n8n" /MIR /XF "ATUALIZAR_DO_CLAUDE.bat" /NDL /NP

if %ERRORLEVEL% LEQ 7 (
    echo.
    echo ========================================================
    echo   [SUCESSO] Curso atualizado com sucesso!
    echo ========================================================
) else (
    echo.
    echo ========================================================
    echo   [ERRO] Ocorreu um problema ao sincronizar os arquivos.
    echo ========================================================
)

echo.
pause
