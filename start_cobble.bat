@echo off
cd /d "" REM Colocar o caminho da pasta aqui, exemplo: "C:\Users\lrroc\Desktop\Cobble 2.0"

REM Abrir HTML no navegador Chrome
start chrome "file:///%cd%/cobble2_Frontend.html"

REM Iniciar backend no terminal (fecha junto com ele)
python -m uvicorn cobble2_Backend:app --reload
