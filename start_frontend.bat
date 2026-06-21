@echo off
title HabitFlow Frontend
cd /d "%~dp0frontend"

if not exist "node_modules" (
  echo [HabitFlow] frontend\node_modules not found.
  echo Please run npm install in the frontend folder first.
  pause
  exit /b 1
)

echo [HabitFlow] Starting Vite frontend on http://localhost:5173
npm.cmd run dev
pause
