@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Set up Curve Studio first:
    echo   python -m venv .venv
    echo   .venv\Scripts\python -m pip install -r requirements-studio.txt
    exit /b 1
)
.venv\Scripts\python -m mechagremlin.studio
exit /b %errorlevel%
