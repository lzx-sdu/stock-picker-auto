#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Check Script
"""

import os

def check_files():
    """Check all required files"""
    print("Checking required files...")
    print("=" * 50)
    
    # Current directory
    current_dir = os.getcwd()
    print(f"Current working directory: {current_dir}")
    print()
    
    # Files to check
    files_to_check = [
        "bollinger_strategy_runner.py",
        "requirements.txt",
        ".github/workflows/daily_stock_screening.yml",
        "deploy_to_github.py"
    ]
    
    all_exist = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - EXISTS")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            all_exist = False
    
    print()
    
    if all_exist:
        print("🎉 All files exist! Ready to deploy.")
        print()
        print("Next steps:")
        print("1. Run: python deploy_to_github.py")
        print("2. Enter your GitHub repository URL")
        print("3. Wait for deployment to complete")
    else:
        print("⚠️ Some files are missing. Please check the file structure.")
        print()
        print("Current directory files:")
        for item in os.listdir("."):
            if os.path.isfile(item):
                print(f"  📄 {item}")
            elif os.path.isdir(item):
                print(f"  📁 {item}/")

if __name__ == "__main__":
    check_files()

