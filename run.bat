@echo off
setlocal

if not exist .env (
  echo .env file not found. Copying from .env.example...
  copy .env.example .env >nul
)

if not exist .venv\Scripts\python.exe (
  python -m venv .venv
  if errorlevel 1 (
    echo Failed to create virtual environment. Is Python installed?
    echo Press any key to close this window...
    pause >nul
    exit /b 1
  )
)

.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 (
  echo Failed to upgrade pip.
  echo Press any key to close this window...
  pause >nul
  exit /b 1
)

.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
  echo Failed to install dependencies.
  echo Press any key to close this window...
  pause >nul
  exit /b 1
)

.venv\Scripts\python.exe app.py
if errorlevel 1 (
  echo App exited with an error.
  echo Press any key to close this window...
  pause >nul
  exit /b 1
)
endlocal
