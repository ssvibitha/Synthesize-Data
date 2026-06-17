@echo off
:: Navigate to the directory of this batch file to ensure relative paths work correctly
cd /d "%~dp0"

:: Check if Python is installed and available in the environment variables
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your system's PATH.
    echo Please install Python and check the option "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [INFO] Starting ml_pipeline in lead.py...
python crm\lead.py

:: Check if execution was successful
if %errorlevel% neq 0 (
    echo [ERROR] lead.py execution failed with exit code %errorlevel%.
) else (
    echo [SUCCESS] lead.py executed successfully.
)

pause
