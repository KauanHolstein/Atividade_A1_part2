@echo off
REM Abre a interface grafica do Algoritmo Genetico.
REM Tenta o Python instalado, depois 'py', depois 'python'.

cd /d "%~dp0"

set "PY_REAL=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"

if exist "%PY_REAL%" (
    "%PY_REAL%" interface_ag.py
    goto fim
)

where py >nul 2>nul
if %errorlevel%==0 (
    py interface_ag.py
    goto fim
)

where python >nul 2>nul
if %errorlevel%==0 (
    python interface_ag.py
    goto fim
)

echo.
echo Python nao foi encontrado.
echo Instale em https://www.python.org/downloads/ marcando "Add Python to PATH".
echo.
pause

:fim
