@echo off
setlocal enabledelayedexpansion

:: Obtener la ruta del directorio actual
set "dir=%cd%"

:: Verificar y crear el entorno virtual si no existe
if not exist "venv\Scripts\activate.bat" (
    echo Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo Error: No se pudo crear el entorno virtual.
        echo Por favor, asegúrate de tener Python instalado correctamente.
        pause
        exit /b 1
    )
)

:: Activar el entorno virtual
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: No se pudo activar el entorno virtual.
    pause
    exit /b 1
)

:: Cambiar al directorio del script
cd /d "%dir%"

:: Actualizar pip
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Error: No se pudo actualizar pip.
    pause
    exit /b 1
)

:: Instalar setuptools y wheel
pip install setuptools wheel
if errorlevel 1 (
    echo Error: No se pudieron instalar setuptools y wheel.
    pause
    exit /b 1
)

:: Instalar dependencias básicas
pip install --only-binary :all: customtkinter==5.2.2
pip install --only-binary :all: pdfplumber==0.10.3
pip install --only-binary :all: google-generativeai==0.3.2

:: Instalar el resto de dependencias
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: No se pudieron instalar las dependencias.
    pause
    exit /b 1
)

:: Verificar si existe el script principal
if not exist "src\Codigo.py" (
    echo Error: No se encontró el archivo src\Codigo.py
    pause
    exit /b 1
)

:: Ejecutar el script Python
python src\Codigo.py
if errorlevel 1 (
    echo Error: El script Python falló.
    pause
    exit /b 1
)

:: Pausa para ver la salida
pause