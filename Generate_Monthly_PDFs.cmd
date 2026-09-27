@echo off
echo ========================================================
echo ST. GREGORIOS CHURCH - MONTHLY PDF STATEMENT GENERATOR
echo ========================================================
echo.
echo Make sure you have exported the latest backup from the web app
echo into your Downloads folder before running this!
echo.
echo Press any key to start generating...
pause >nul

echo.
echo Starting generator...
python c:\CASHBOOK_APP\Monthly_PDF_Generator.py

echo.
echo Opening the folder for you...
explorer "c:\CASHBOOK_APP"

echo.
echo Done! You can close this window.
pause
