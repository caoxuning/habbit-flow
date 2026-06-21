@echo off
title HabitFlow Backend
cd /d "%~dp0backend_fastapi"

if not exist ".venv\Scripts\python.exe" (
  echo [HabitFlow] backend_fastapi\.venv\Scripts\python.exe not found.
  echo Please create the backend virtual environment and install requirements first.
  pause
  exit /b 1
)

echo [HabitFlow] Starting FastAPI backend on http://localhost:8081
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8081
pause
