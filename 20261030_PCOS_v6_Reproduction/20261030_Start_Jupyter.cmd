@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run 20261030_Setup_Windows.ps1 first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m jupyterlab .
