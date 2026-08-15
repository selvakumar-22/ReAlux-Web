@echo off
cd /d "%~dp0backend"
call venv\Scripts\activate
uvicorn app:app --reload --port 8000
pause
