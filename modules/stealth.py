"""
Stealth 工具 - 反检测增强
"""

STEALTH_SCRIPTS = [
    # 隐藏 webdriver 标志
    """
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    """,
    
    # 伪装 Chrome
    """
    window.chrome = {
        runtime: {}
    };
    """,
    
    # 伪装 permissions
    """
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );
    """,
    
    # 伪装 plugins
    """
    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            {
                0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                description: "Portable Document Format",
                filename: "internal-pdf-viewer",
                length: 1,
                name: "Chrome PDF Plugin"
            },
            {
                0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
                description: "Portable Document Format",
                filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                length: 1,
                name: "Chrome PDF Viewer"
            }
        ]
    });
    """,
    
    # 伪装 languages
    """
    Object.defineProperty(navigator, 'languages', {
        get: () => ['zh-CN', 'zh', 'en-US', 'en']
    });
    """,
    
    # 隐藏 automation 标志
    """
    delete navigator.__proto__.webdriver;
    """,
    
    # 伪装 notification
    """
    if (!window.Notification) {
        window.Notification = {
            permission: 'default',
            requestPermission: () => Promise.resolve('default')
        };
    }
    """
]


def get_stealth_script() -> str:
    """获取完整的 stealth 脚本"""
    return ";".join(STEALTH_SCRIPTS)
