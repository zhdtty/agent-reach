"""
Agent-Reach 基类模块
"""

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from rich.logging import RichHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("agent-reach")


class BaseClient(ABC):
    """平台客户端基类"""
    
    def __init__(self, cookie_file: Optional[Path] = None):
        self.cookie_file = cookie_file
        self.cookies = self._load_cookies()
        self.client = httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers=self._get_default_headers()
        )
    
    def _load_cookies(self) -> Dict[str, str]:
        """从文件加载 Cookie"""
        if not self.cookie_file or not self.cookie_file.exists():
            return {}
        
        try:
            with open(self.cookie_file, "r") as f:
                data = json.load(f)
                return data
        except Exception as e:
            logger.error(f"加载 Cookie 失败: {e}")
            return {}
    
    def _get_default_headers(self) -> Dict[str, str]:
        """获取默认请求头"""
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
        }
    
    def _build_cookie_string(self, cookies: Dict[str, str]) -> str:
        """构建 Cookie 字符串"""
        return "; ".join([f"{k}={v}" for k, v in cookies.items()])
    
    def close(self):
        """关闭客户端"""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
