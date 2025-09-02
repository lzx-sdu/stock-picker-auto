#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub自动化部署脚本
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description}成功")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description}失败")
            print(f"错误信息: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ {description}出错: {str(e)}")
        return False

def check_git_installed():
    """检查Git是否已安装"""
    return run_command("git --version", "检查Git安装")

def check_git_configured():
    """检查Git配置"""
    print("🔍 检查Git配置...")
    
    # 检查用户名
    result = subprocess.run("git config user.name", shell=True, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        print("⚠️  Git用户名未配置")
        username = input("请输入您的Git用户名: ")
        run_command(f'git config --global user.name "{username}"', "设置Git用户名")
    
    # 检查邮箱
    result = subprocess.run("git config user.email", shell=True, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        print("⚠️  Git邮箱未配置")
        email = input("请输入您的Git邮箱: ")
        run_command(f'git config --global user.email "{email}"', "设置Git邮箱")

def create_github_repo():
    """创建GitHub仓库"""
    print("\n📋 创建GitHub仓库步骤:")
    print("1. 访问 https://github.com/new")
    print("2. 仓库名称: stock-picker-auto")
    print("3. 选择 Public (公开)")
    print("4. 点击 Create repository")
    print("5. 复制仓库URL")
    
    repo_url = input("\n请输入您的GitHub仓库URL (例如: https://github.com/用户名/stock-picker-auto.git): ")
    return repo_url.strip()

def deploy_to_github():
    """部署到GitHub"""
    print("🚀 开始部署到GitHub...")
    print("=" * 50)
    
    # 检查Git安装
    if not check_git_installed():
        print("❌ 请先安装Git: https://git-scm.com/downloads")
        return False
    
    # 检查Git配置
    check_git_configured()
    
    # 获取仓库URL
    repo_url = create_github_repo()
    if not repo_url:
        print("❌ 未提供仓库URL")
        return False
    
    # 初始化Git仓库
    if not run_command("git init", "初始化Git仓库"):
        return False
    
    # 添加所有文件
    if not run_command("git add .", "添加文件到Git"):
        return False
    
    # 提交更改
    commit_message = f"Initial commit - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    if not run_command(f'git commit -m "{commit_message}"', "提交更改"):
        return False
    
    # 设置主分支
    if not run_command("git branch -M main", "设置主分支"):
        return False
    
    # 添加远程仓库
    if not run_command(f'git remote add origin "{repo_url}"', "添加远程仓库"):
        return False
    
    # 推送到GitHub
    if not run_command("git push -u origin main", "推送到GitHub"):
        return False
    
    print("\n🎉 部署成功！")
    print("=" * 50)
    
    # 提取用户名和仓库名
    try:
        parts = repo_url.split('/')
        username = parts[-2]
        repo_name = parts[-1].replace('.git', '')
        github_pages_url = f"https://{username}.github.io/{repo_name}/"
        
        print(f"📱 您的手机访问地址: {github_pages_url}")
        print("\n📋 接下来的步骤:")
        print("1. 进入GitHub仓库设置")
        print("2. 找到 Pages 选项")
        print("3. Source选择 'Deploy from a branch'")
        print("4. Branch选择 'gh-pages'")
        print("5. 点击 Save")
        print("6. 等待几分钟后即可访问")
        
    except:
        print("📱 请在GitHub仓库设置中启用Pages功能")
    
    return True

def main():
    """主函数"""
    print("🚀 GitHub自动化股票筛选系统部署工具")
    print("=" * 50)
    print("这个工具将帮助您:")
    print("✅ 自动部署项目到GitHub")
    print("✅ 设置GitHub Actions自动运行")
    print("✅ 启用GitHub Pages手机访问")
    print("✅ 实现每天自动更新")
    print("=" * 50)
    
    # 检查必要文件
    required_files = [
        "bollinger_strategy_runner.py",
        "requirements.txt",
        ".github/workflows/daily_stock_screening.yml"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ 缺少必要文件:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n请确保所有文件都已创建")
        return
    
    print("✅ 所有必要文件已就绪")
    
    # 确认部署
    confirm = input("\n是否开始部署到GitHub? (y/n): ")
    if confirm.lower() != 'y':
        print("部署已取消")
        return
    
    # 执行部署
    if deploy_to_github():
        print("\n🎊 恭喜！您的自动化股票筛选系统已成功部署到GitHub！")
        print("📱 现在您可以在手机上随时查看选股结果了！")
    else:
        print("\n❌ 部署失败，请检查错误信息并重试")

if __name__ == "__main__":
    main()
