# Agent-Reach 使用文档

🦞 东哥的午夜码魂网络工具 - 无需 Docker，本地直跑！

## 🚀 快速开始

### 安装

```bash
cd ~/.openclaw/workspace-001/agent-reach
source venv/bin/activate
```

### 配置平台

#### GitHub
```bash
# 浏览器授权登录
gh auth login

# 验证登录状态
gh auth status
```

#### Twitter/X
```bash
# 配置 Cookie
python3 agent-reach.py twitter config

# 按提示输入三个值：
# - auth_token: 从浏览器 Cookie 复制
# - ct0: 从浏览器 Cookie 复制
# - twid: 从浏览器 Cookie 复制（格式 u%3D数字）
```

**Cookie 获取步骤：**
1. Chrome 登录 https://x.com
2. F12 → Application → Cookies → https://x.com
3. 复制 `auth_token`, `ct0`, `twid`

#### 小红书
```bash
# 配置 Cookie
python3 agent-reach.py xiaohongshu config

# 按提示输入完整 Cookie 字符串
```

**Cookie 获取步骤：**
1. Chrome 登录 https://www.xiaohongshu.com
2. F12 → Network 标签
3. 刷新页面，找任意请求（如 `me`）
4. 右键 → Copy → Copy as cURL
5. 提取 `-H 'cookie: ...'` 那一长串

---

## 📖 功能使用

### GitHub

```bash
# 搜索仓库
python3 agent-reach.py github search "machine learning" --limit 10

# 查看仓库详情
python3 agent-reach.py github view "microsoft/vscode"
```

### Twitter/X

```bash
# 搜索推文
python3 agent-reach.py twitter search "OpenAI" --limit 5

# 获取用户时间线
python3 agent-reach.py twitter timeline -u elonmusk -l 5

# 发布推文
python3 agent-reach.py twitter post "Hello World 🚀"

# 获取用户信息
python3 agent-reach.py twitter user-info elonmusk
```

### 小红书

```bash
# 搜索笔记
python3 agent-reach.py xiaohongshu search "穿搭" --limit 5

# 获取笔记详情
python3 agent-reach.py xiaohongshu detail <笔记ID>

# 点赞笔记
python3 agent-reach.py xiaohongshu like <笔记ID>

# 查看当前用户信息
python3 agent-reach.py xiaohongshu profile
```

---

## 🔐 安全说明

- **Cookie 仅本地存储**，不上传任何服务器
- 存储位置：`~/.openclaw/workspace-001/agent-reach/cookies/`
- **代码完全开源**，可自行审查
- 建议定期更新 Cookie（过期后需重新配置）

---

## 🛠️ 技术架构

| 平台 | 技术方案 | 说明 |
|------|----------|------|
| GitHub | 官方 CLI | `gh` 命令行工具 |
| Twitter/X | Playwright | 浏览器自动化，绕过 API 限制 |
| 小红书 | Playwright | 浏览器自动化，绕过签名验证 |

---

## ⚠️ 注意事项

1. **Cookie 会过期**：一般 1-3 个月需重新配置
2. **频率限制**：频繁操作可能触发平台风控
3. **网络要求**：需要能访问目标网站（Twitter 需科学上网）
4. **首次运行**：会自动下载 Chromium（约 100MB）

---

## 🐛 故障排除

### Twitter 返回 404
- 已修复：改用 Playwright 浏览器方案

### 小红书"账号异常"
- 已修复：改用 Playwright 浏览器方案

### GitHub "未登录"
- 运行 `gh auth login` 重新授权

### Playwright 报错
```bash
# 重新安装浏览器
playwright install chromium
```

---

## 📝 更新日志

### v1.0.0 (2026-02-27)
- ✅ GitHub 搜索/查看
- ✅ Twitter 搜索/时间线/发帖
- ✅ 小红书搜索/详情/点赞
- ✅ 本地 Cookie 存储
- ✅ Playwright 浏览器自动化

---

Made with 🦞 by 小码哥 for 东哥
