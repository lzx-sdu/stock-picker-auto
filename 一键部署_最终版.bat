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

REM 显示当前目录
echo 当前工作目录: %CD%
echo.

REM 检查Python是否安装
echo 检查Python安装...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：Python未安装
    echo 请先安装Python: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python已安装
echo.

REM 检查必要文件 - 使用更智能的检查方式
echo 检查必要文件...

REM 检查bollinger_strategy_runner.py - 尝试多个可能的位置
set "found_bollinger="
if exist "stock_picker\bollinger_strategy_runner.py" (
    echo ✅ stock_picker\bollinger_strategy_runner.py 存在
    set "found_bollinger=1"
) else if exist "bollinger_strategy_runner.py" (
    echo ✅ bollinger_strategy_runner.py 存在（根目录）
    set "found_bollinger=1"
) else (
    echo ❌ 错误：找不到 bollinger_strategy_runner.py 文件
    echo 尝试查找文件...
    dir /s /b bollinger_strategy_runner.py 2>nul
    if errorlevel 1 (
        echo 未找到 bollinger_strategy_runner.py 文件
    )
    pause
    exit /b 1
)

REM 检查requirements.txt
set "found_requirements="
if exist "requirements.txt" (
    echo ✅ requirements.txt 存在
    set "found_requirements=1"
) else if exist "stock_picker\requirements.txt" (
    echo ✅ stock_picker\requirements.txt 存在
    set "found_requirements=1"
) else (
    echo ❌ 错误：找不到 requirements.txt 文件
    pause
    exit /b 1
)

REM 检查GitHub Actions文件
if exist ".github\workflows\daily_stock_screening.yml" (
    echo ✅ .github\workflows\daily_stock_screening.yml 存在
) else (
    echo ❌ 错误：找不到 .github\workflows\daily_stock_screening.yml 文件
    pause
    exit /b 1
)

REM 检查deploy_to_github.py
if exist "deploy_to_github.py" (
    echo ✅ deploy_to_github.py 存在
) else (
    echo ❌ 错误：找不到 deploy_to_github.py 文件
    pause
    exit /b 1
)

echo.
echo ✅ 所有必要文件已就绪
echo.

REM 显示文件列表（调试信息）
echo 当前目录文件列表:
dir /b
echo.
echo stock_picker目录文件列表:
dir /b stock_picker
echo.

REM 运行部署脚本
echo 开始运行部署脚本...
python deploy_to_github.py

echo.
echo 按任意键退出...
pause >nul

