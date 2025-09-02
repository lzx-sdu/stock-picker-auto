@echo off
chcp 65001 >nul
echo.
echo ========================================
echo 🚀 GitHub自动化股票筛选系统部署工具
echo ========================================
echo.
echo 这个工具将帮助您:
echo ✅ 自动部署项目到GitHub
echo ✅ 设置GitHub Actions自动运行
echo ✅ 启用GitHub Pages手机访问
echo ✅ 实现每天自动更新
echo.
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：Python未安装
    echo 请先安装Python: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查必要文件
if not exist "stock_picker\bollinger_strategy_runner.py" (
    echo ❌ 错误：缺少 stock_picker\bollinger_strategy_runner.py 文件
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ❌ 错误：缺少 requirements.txt 文件
    pause
    exit /b 1
)

if not exist ".github\workflows\daily_stock_screening.yml" (
    echo ❌ 错误：缺少 .github\workflows\daily_stock_screening.yml 文件
    pause
    exit /b 1
)

echo ✅ 所有必要文件已就绪
echo.

REM 运行部署脚本
python deploy_to_github.py

echo.
echo 按任意键退出...
pause >nul
