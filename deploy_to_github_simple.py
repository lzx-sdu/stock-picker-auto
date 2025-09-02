#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的GitHub部署脚本
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(command, description):
    """运行命令"""
    print(f"🔄 {description}...")
    print(f"执行命令: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print(f"✅ {description}成功")
            if result.stdout:
                print(f"输出: {result.stdout}")
        else:
            print(f"❌ {description}失败")
            print(f"错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ {description}异常: {e}")
        return False
    
    return True

def check_git_status():
    """检查Git状态"""
    print("🔍 检查Git状态...")
    
    # 检查是否在Git仓库中
    if not os.path.exists('.git'):
        print("❌ 当前目录不是Git仓库")
        return False
    
    # 检查Git配置
    if not run_command("git config --get user.name", "检查Git用户名"):
        return False
    
    if not run_command("git config --get user.email", "检查Git邮箱"):
        return False
    
    return True

def setup_git_config():
    """设置Git配置"""
    print("⚙️ 设置Git配置...")
    
    # 获取用户输入
    username = input("请输入您的GitHub用户名: ").strip()
    email = input("请输入您的邮箱地址: ").strip()
    
    if not username or not email:
        print("❌ 用户名和邮箱不能为空")
        return False
    
    # 设置Git配置
    if not run_command(f'git config user.name "{username}"', "设置Git用户名"):
        return False
    
    if not run_command(f'git config user.email "{email}"', "设置Git邮箱"):
        return False
    
    return True

def create_github_repo():
    """创建GitHub仓库"""
    print("🌐 创建GitHub仓库...")
    
    print("请按以下步骤在GitHub网页上创建仓库：")
    print("1. 访问: https://github.com/new")
    print("2. 仓库名称: stock-picker-auto")
    print("3. 描述: 股票筛选自动化系统")
    print("4. 选择 Public")
    print("5. 不要勾选任何选项")
    print("6. 点击 'Create repository'")
    
    repo_url = input("请输入新创建的仓库URL (例如: https://github.com/用户名/stock-picker-auto.git): ").strip()
    
    if not repo_url:
        print("❌ 仓库URL不能为空")
        return False
    
    return repo_url

def deploy_to_github(repo_url):
    """部署到GitHub"""
    print("🚀 开始部署到GitHub...")
    
    # 添加远程仓库
    if not run_command(f'git remote add origin "{repo_url}"', "添加远程仓库"):
        return False
    
    # 添加所有文件
    if not run_command("git add .", "添加所有文件"):
        return False
    
    # 提交更改
    commit_message = f"Initial commit - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    if not run_command(f'git commit -m "{commit_message}"', "提交更改"):
        return False
    
    # 推送到main分支
    if not run_command("git push -u origin main", "推送到GitHub"):
        return False
    
    print("✅ 部署完成！")
    return True

def main():
    """主函数"""
    print("🚀 GitHub自动化部署脚本")
    print("=" * 50)
    
    # 检查Git状态
    if not check_git_status():
        print("❌ Git状态检查失败")
        return
    
    # 设置Git配置
    if not setup_git_config():
        print("❌ Git配置设置失败")
        return
    
    # 创建GitHub仓库
    repo_url = create_github_repo()
    if not repo_url:
        print("❌ 无法获取仓库URL")
        return
    
    # 部署到GitHub
    if not deploy_to_github(repo_url):
        print("❌ 部署失败")
        return
    
    print("\n🎉 部署成功！")
    print("=" * 50)
    print("接下来需要手动启用GitHub功能：")
    print("1. 进入GitHub仓库页面")
    print("2. 点击 Settings -> Pages")
    print("3. Source选择 'Deploy from a branch'")
    print("4. Branch选择 'gh-pages'")
    print("5. 点击 Save")
    print("6. 等待几分钟让GitHub Pages部署完成")
    print("7. 访问: https://您的用户名.github.io/stock-picker-auto/")

if __name__ == "__main__":
    main()
