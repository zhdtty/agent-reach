# Agent-Reach

🦞 东哥的 Agent 网络访问工具 - 无需 Docker，本地直跑！

解决 Agent 访问小红书、Twitter 等平台的限制问题。免 API Key，仅需 Cookie 即可授权访问。

## ✨ 核心功能

| 平台 | 能力 | 状态 |
|------|------|------|
| **GitHub** | 仓库搜索、查看详情 | ✅ 可用 |
| **Twitter/X** | 推文搜索、时间线、发帖、AI 生成 | ✅ 可用 |
| **小红书** | 笔记搜索、点赞、详情、AI 生成 | ✅ 可用 |

### 🚀 新增特性

- ✨ **多账号支持** - 可同时管理多个 Twitter/小红书账号
- 🥷 **Stealth 模式** - 浏览器反检测，降低被封风险
- 🤖 **AI 内容生成** - 自动生成推文、小红书笔记（支持 OpenAI/Gemini）

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

# 可选：配置 AI 生成
export OPENAI_API_KEY="your-key-here"    # 用于 AI 内容生成
```

## 📖 使用方法

### GitHub
```bash
python3 agent-reach.py github search "openai" --limit 5
```

### Twitter
```bash
# 搜索推文
python3 agent-reach.py twitter search "AI" --limit 5

# 发布推文（AI 生成）
python3 agent-reach.py twitter post --topic "AI 编程" --ai

# 多账号切换
python3 agent-reach.py twitter -a work config    # 配置工作账号
python3 agent-reach.py twitter -a work post --text "Hello"

# 关闭 Stealth 模式（调试用）
python3 agent-reach.py twitter --no-stealth search "test"
```

### 小红书
```bash
# 搜索笔记
python3 agent-reach.py xiaohongshu search "穿搭" --limit 5

# AI 生成笔记
python3 agent-reach.py xiaohongshu generate --topic "学习效率"
```

### AI 内容生成（独立工具）
```bash
# 生成推文
python3 agent-reach.py ai content "编程技巧" -p twitter

# 生成小红书笔记
python3 agent-reach.py ai content "护肤心得" -p xiaohongshu

# 生成 Hashtag
python3 agent-reach.py ai hashtags "AI 编程教程" -p twitter
```

## 🔐 安全说明

- Cookie **仅本地存储**，不上传任何服务器
- 代码完全开源可审查
- 使用 Playwright + Stealth 技术，模拟真实用户行为
- 支持多账号隔离，账号间 Cookie 互不干扰

## 🛠️ 技术架构

| 功能 | 技术方案 |
|------|----------|
| **GitHub** | 官方 CLI (`gh`) |
| **Twitter/X** | Playwright + Stealth 脚本 |
| **小红书** | Playwright + Stealth 脚本 |
| **AI 生成** | OpenAI GPT / Google Gemini |

## 📚 详细文档

- [USAGE.md](./USAGE.md) - 完整使用指南

## 📝 License

MIT License - 由小码哥为东哥打造 🦞

---

**GitHub**: https://github.com/zhdtty/agent-reach
