# 🚀 GitHub自动化股票筛选系统

## 📱 手机访问方案

这个方案让您可以在手机上查看每天自动更新的股票筛选结果，无需打开电脑！

## ✨ 功能特点

- 🤖 **完全自动化**：每天自动运行股票筛选
- 📱 **手机友好**：响应式设计，完美适配手机
- ⚡ **实时更新**：每天09:30和15:30自动更新
- 🌍 **全球访问**：通过网址即可访问
- 💰 **完全免费**：使用GitHub免费服务

## 🛠️ 设置步骤

### 步骤1：创建GitHub仓库

1. 登录GitHub
2. 点击右上角 "+" → "New repository"
3. 仓库名称：`stock-picker-auto`
4. 选择 "Public"（公开）
5. 点击 "Create repository"

### 步骤2：上传代码

```bash
# 在您的项目目录中执行
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/您的用户名/stock-picker-auto.git
git push -u origin main
```

### 步骤3：启用GitHub Pages

1. 进入您的GitHub仓库
2. 点击 "Settings" 标签
3. 左侧菜单找到 "Pages"
4. Source选择 "Deploy from a branch"
5. Branch选择 "gh-pages"
6. 点击 "Save"

### 步骤4：启用GitHub Actions

1. 在仓库中点击 "Actions" 标签
2. 点击 "Enable Actions"
3. 系统会自动检测到 `.github/workflows/daily_stock_screening.yml` 文件

## 📱 手机访问

设置完成后，您可以通过以下地址访问：

```
https://您的用户名.github.io/stock-picker-auto/
```

## 🔄 自动更新机制

### 更新频率
- **上午9:30**：开盘前更新
- **下午15:30**：收盘后更新

### 更新内容
- 📊 最新股票筛选结果
- 📈 技术指标分析
- 🎯 投资建议
- 📱 手机友好的HTML报告

## 📋 文件结构

```
stock-picker-auto/
├── .github/
│   └── workflows/
│       └── daily_stock_screening.yml  # 自动化工作流
├── src/
│   ├── analysis/
│   ├── data/
│   ├── strategy/
│   └── utils/
├── results/
│   ├── picks/          # CSV筛选结果
│   └── reports/        # HTML报告
├── bollinger_strategy_runner.py
├── requirements.txt
└── README_GitHub_Setup.md
```

## 🎯 使用流程

1. **设置完成后**：系统会自动运行
2. **每天查看**：在手机上打开网址即可
3. **查看结果**：点击"查看今日选股结果"
4. **无需操作**：完全自动化，无需任何手动操作

## 🔧 手动触发

如果需要立即运行（不等到定时时间）：

1. 进入GitHub仓库
2. 点击 "Actions" 标签
3. 选择 "Daily Stock Screening"
4. 点击 "Run workflow"
5. 选择分支（main）
6. 点击 "Run workflow"

## 📊 查看历史记录

1. 进入GitHub仓库
2. 点击 "Actions" 标签
3. 查看运行历史
4. 点击任意运行记录查看详情
5. 下载生成的文件

## 🚨 注意事项

### 免费版限制
- GitHub Actions：每月2000分钟免费
- GitHub Pages：完全免费
- 仓库大小：建议小于1GB

### 数据来源
- 使用Akshare获取股票数据
- 需要网络连接
- 数据可能有延迟

### 时区设置
- 工作流使用UTC时间
- 北京时间 = UTC + 8小时
- 9:30和15:30对应UTC的1:30和7:30

## 🆘 常见问题

### Q: 工作流没有运行？
A: 检查仓库设置中的Actions是否已启用

### Q: 页面显示404？
A: 等待几分钟，GitHub Pages需要时间部署

### Q: 数据更新不及时？
A: 检查网络连接和数据源可用性

### Q: 如何修改更新频率？
A: 编辑 `.github/workflows/daily_stock_screening.yml` 中的cron表达式

## 📞 技术支持

如果遇到问题：
1. 检查GitHub Actions运行日志
2. 查看仓库Issues
3. 确认所有依赖已正确安装

## 🎉 完成！

设置完成后，您就可以：
- 📱 在手机上随时查看选股结果
- 🤖 享受完全自动化的更新
- 💰 无需任何费用
- 🌍 全球任何地方都能访问

**开始享受您的自动化股票筛选系统吧！** 🚀

