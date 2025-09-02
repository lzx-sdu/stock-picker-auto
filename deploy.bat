@echo off
echo.
echo ========================================
echo GitHub Auto Stock Screening System
echo ========================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed
    echo Please install Python: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo Python is installed
echo.

REM Check required files
echo Checking required files...

REM Check bollinger_strategy_runner.py
if exist "bollinger_strategy_runner.py" (
    echo bollinger_strategy_runner.py - OK
) else (
    echo ERROR: bollinger_strategy_runner.py not found
    pause
    exit /b 1
)

REM Check requirements.txt
if exist "requirements.txt" (
    echo requirements.txt - OK
) else (
    echo ERROR: requirements.txt not found
    pause
    exit /b 1
)

REM Check GitHub Actions file
if exist ".github\workflows\daily_stock_screening.yml" (
    echo .github\workflows\daily_stock_screening.yml - OK
) else (
    echo ERROR: .github\workflows\daily_stock_screening.yml not found
    pause
    exit /b 1
)

REM Check deploy_to_github.py
if exist "deploy_to_github.py" (
    echo deploy_to_github.py - OK
) else (
    echo ERROR: deploy_to_github.py not found
    pause
    exit /b 1
)

echo.
echo All required files are ready
echo.

REM Run deployment script
echo Starting deployment script...
python deploy_to_github.py

echo.
echo Press any key to exit...
pause >nul

