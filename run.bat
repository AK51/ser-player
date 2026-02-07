@echo off
echo Starting SER File Viewer...
python main.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start application
    echo.
    echo Make sure you have run setup.bat first
    echo.
    pause
)
