@echo off
title St. Gregorios Church Accounting Portal
echo ==================================================
echo   ST. GREGORIOS CHURCH ACCOUNTING PORTAL
echo   Launching Local Accounting Portal...
echo ==================================================

:: Start local web server background process
start /min py start_server.py

:: Wait 1 second for server initialization
timeout /t 1 /nobreak >nul

:: Launch Microsoft Edge in App Mode (Signed system browser, bypassing Smart App Control)
set EDGE_PATH="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not exist %EDGE_PATH% set EDGE_PATH="C:\Program Files\Microsoft\Edge\Application\msedge.exe"

if exist %EDGE_PATH% (
    start "" %EDGE_PATH% --app="http://localhost:8088/"
) else (
    start "" "http://localhost:8088/"
)
