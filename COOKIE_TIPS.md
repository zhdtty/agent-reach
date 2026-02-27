# Cookie 持久化指南

## 🔥 延长 Cookie 寿命的方法

### 1️⃣ 获取长期 Cookie（推荐）

**Twitter/X：**
1. 登录时勾选 **"记住我"**（Remember me）
2. 保持账号活跃（每周至少登录一次网页版）
3. 不要频繁切换 IP/设备
4. 导出完整的 Cookie 列表（不只是 auth_token）

```javascript
// 在浏览器 Console 执行，复制完整 Cookie
document.cookie
```

**小红书：**
1. 使用 **扫码登录** 比密码登录更持久
2. 保持 App 和网页同时登录
3. 定期（每周）访问一次网页版

---

### 2️⃣ 自动续期脚本（进阶）

创建定时任务，每周自动刷新 Cookie：

```bash
# 添加到 crontab
crontab -e

# 每周一早上8点刷新
0 8 * * 1 cd ~/.openclaw/workspace-001/agent-reach && source venv/bin/activate && python3 -c "
from modules.twitter import TwitterClient
from modules.xiaohongshu import XiaoHongShuClient
from pathlib import Path

# 访问首页保持活跃
t = TwitterClient(Path('cookies/twitter_default.json'))
t.get_timeline(limit=1)

x = XiaoHongShuClient(Path('cookies/xiaohongshu_default.json'))
x.search('test', limit=1)
print('Cookie 刷新完成')
"
```

---

### 3️⃣ 使用 Playwright 自动登录（终极方案）

如果真的过期了，让程序自动重新登录：

```python
# auto_login.py
from playwright.sync_api import sync_playwright
import json

def auto_login_twitter(username, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 首次需要可见
        context = browser.new_context()
        page = context.new_page()
        
        # 登录流程
        page.goto('https://x.com/login')
        page.fill('input[name="text"]', username)
        page.click('text=Next')
        page.fill('input[name="password"]', password)
        page.click('text=Log in')
        
        # 等待登录成功
        page.wait_for_selector('[data-testid="primaryColumn"]')
        
        # 保存 Cookie
        cookies = context.cookies()
        with open('cookies/twitter_default.json', 'w') as f:
            json.dump({c['name']: c['value'] for c in cookies}, f)
        
        browser.close()
```

---

### 4️⃣ 监控 Cookie 过期

添加检测逻辑：

```python
# 在 agent-reach.py 中添加
def check_cookie_valid(platform):
    """检查 Cookie 是否有效"""
    if platform == 'twitter':
        client = TwitterClient(COOKIES_DIR / 'twitter_default.json')
        result = client.get_timeline(limit=1)
        if not result:
            print('❌ Twitter Cookie 可能已过期')
            return False
    return True
```

---

## ⏱️ 各平台 Cookie 寿命

| 平台 | 通常寿命 | 延长方法 |
|------|----------|----------|
| Twitter/X | 1-3 个月 | 勾选记住我 + 定期访问 |
| 小红书 | 2-4 周 | 扫码登录 + 保持 App 登录 |
| GitHub | 永久（Token）| 使用 gh CLI 授权 |

---

## 💡 东哥的最佳实践

1. **多账号备份** - 配置 2-3 个账号轮换使用
2. **定期导出** - 每月导出一次完整 Cookie 备份
3. **设置提醒** - 日历提醒每月检查一次 Cookie 状态
4. **使用专用账号** - 不要用主力账号，避免频繁重新登录影响日常使用

---

## 🚀 立即可做的

```bash
# 1. 重新获取最新 Cookie（今天）
python3 agent-reach.py twitter -a default config
python3 agent-reach.py xiaohongshu -a default config

# 2. 测试是否有效
python3 agent-reach.py twitter -a default search "test" --limit 1
python3 agent-reach.py xiaohongshu -a default search "test" --limit 1

# 3. 备份 Cookie
cp cookies/twitter_default.json cookies/twitter_default_backup.json
cp cookies/xiaohongshu_default.json cookies/xiaohongshu_default_backup.json
```

---

**总结：** Cookie 过期不可避免，但可以通过定期使用和备份来减少麻烦！
