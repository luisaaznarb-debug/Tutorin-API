@echo off
echo ================================================
echo   LIMPIANDO CACHE DE PYTHON - TUTORIN
echo ================================================
echo.

echo [1/4] Deteniendo procesos de Python...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2/4] Eliminando carpetas __pycache__...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

echo [3/4] Eliminando archivos .pyc...
del /s /q *.pyc 2>nul

echo [4/4] Eliminando archivos .pyo...
del /s /q *.pyo 2>nul

echo.
echo ================================================
echo   CACHE LIMPIADO CORRECTAMENTE
echo ================================================
echo.
echo Presiona cualquier tecla para reiniciar el servidor...
pause >nul

echo.
echo Iniciando servidor...
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000