@echo off
setlocal

if not exist .env (
  echo .env file not found. Copying from .env.example...
  copy .env.example .env >nul
)

docker build -t wol-app .
if errorlevel 1 (
  echo Docker build failed.
  exit /b 1
)

docker run --rm -p 8200:8200 --env-file .env wol-app
endlocal
