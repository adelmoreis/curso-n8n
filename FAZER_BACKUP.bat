@echo off
chcp 65001 >nul
cd /d "%~dp0"
set D=%date:~-4%-%date:~3,2%-%date:~0,2%
if not exist "dados" ( echo Nao encontrei a pasta dados. Rode o INICIAR.bat primeiro. & pause & exit /b )
robocopy "dados" "Backup-dados\%D%" /E /NFL /NDL /NJH /NJS >nul
echo Copia feita em: Backup-dados\%D%
pause
