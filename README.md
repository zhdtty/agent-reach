# Agent-Reach

🦞 东哥的 Agent 网络访问工具 - 无需 Docker，本地直跑！

解决 Agent 访问小红书、Twitter 等平台的限制问题。免 API Key，仅需 Cookie 即可授权访问。

## ✨ 核心功能

| 平台 | 能力 | 状态 |
|------|------|------|
| **GitHub** | 仓库搜索、查看详情 | ✅ 可用 |
| **Twitter/X** | 推文搜索、时间线、发帖 | ✅ 可用 |
| **小红书** | 笔记搜索、点赞、详情 | ✅ 可用 |

## 🚀 快速开始

```bash
# 克隆项目
git clone https://github.com/zhdtty/agent-reach.git
cd agent-reach

# 安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 配置平台（详见 USAGE.md）
gh auth login                              # GitHub
python3 agent-reach.py twitter config      # Twitter
python3 agent-reach.py xiaohongshu config  # 小红书
```

## 📖 使用方法

```bash
# GitHub
python3 agent-reach.py github search "openai" --limit 5

# Twitter
python3 agent-reach.py twitter search "AI" --limit 5
python3 agent-reach.py twitter post "Hello from Agent-Reach 🚀"

# 小红书
python3 agent-reach.py xiaohongshu search "穿搭" --limit 5
```

## 🔐 安全说明

- Cookie **仅本地存储**，不上传任何服务器
- 代码完全开源可审查
- 使用 Playwright 浏览器自动化，模拟真实用户行为

## 🛠️ 技术架构

- **GitHub**: 官方 CLI (`gh`)
- **Twitter/X**: Playwright 浏览器自动化
- **小红书**: Playwright 浏览器自动化

## 📚 详细文档

- [USAGE.md](./USAGE.md) - 完整使用指南

## 📝 License

MIT License - 由小码哥为东哥打造 🦞
