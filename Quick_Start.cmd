@echo off
title St. Gregorios Church Accounting Application
echo ==================================================
echo   ST. GREGORIOS CHURCH ACCOUNTING PORTAL
echo   Starting Standalone Application...
echo ==================================================

:: Start local web server background process
start /min py start_server.py

:: Wait 2 seconds for server initialization
timeout /t 2 /nobreak >nul

:: Launch Microsoft Edge in App Mode (Signed system browser, bypassing Smart App Control)
set EDGE_PATH="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not exist %EDGE_PATH% set EDGE_PATH="C:\Program Files\Microsoft\Edge\Application\msedge.exe"

if exist %EDGE_PATH% (
    start "" %EDGE_PATH% --app="http://localhost:8088/"
) else (
    start "" "http://localhost:8088/"
)
