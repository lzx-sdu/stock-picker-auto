@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    股票筛选系统 - GitHub部署脚本
echo ========================================
echo.

echo 正在检查文件...
if not exist "bollinger_strategy_runner.py" (
    echo 错误：缺少 bollinger_strategy_runner.py 文件
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo 错误：缺少 requirements.txt 文件
    pause
    exit /b 1
)

if not exist ".github\workflows\daily_stock_screening.yml" (
    echo 错误：缺少 GitHub Actions 配置文件
    pause
    exit /b 1
)

echo 所有必需文件都存在！
echo.

echo 正在运行部署脚本...
python deploy_to_github_simple.py

echo.
echo 部署完成！请按任意键退出...
pause >nul
