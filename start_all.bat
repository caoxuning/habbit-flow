@echo off
title HabitFlow Starter

echo [HabitFlow] Starting backend and frontend...
start "HabitFlow Backend" cmd /k ""%~dp0start_backend.bat""
start "HabitFlow Frontend" cmd /k ""%~dp0start_frontend.bat""

echo.
echo [HabitFlow] Backend:  http://localhost:8081
echo [HabitFlow] Frontend: http://localhost:5173
echo.
echo Two terminal windows have been opened. Close those windows to stop the services.
pause
