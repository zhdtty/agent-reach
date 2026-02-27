#!/usr/bin/env python3
"""
小红书模块 - 基于 Playwright 浏览器自动化
绕过 API 签名验证
"""

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import quote

from base import BaseClient, logger


class XiaoHongShuClient(BaseClient):
    """小红书客户端 - 使用 Playwright 浏览器自动化"""
    
    def __init__(self, cookie_file: Path):
        super().__init__(cookie_file)
        self.base_url = "https://www.xiaohongshu.com"
        self.cookies_loaded = bool(self.cookies)
        
        if not self.cookies_loaded:
            logger.warning("小红书 Cookie 未配置")
    
    def _get_playwright(self):
        """延迟导入 playwright"""
        try:
            from playwright.sync_api import sync_playwright
            return sync_playwright
        except ImportError:
            logger.error("Playwright 未安装")
            raise
    
    def _parse_cookie_string(self, cookie_str: str) -> Dict[str, str]:
        """解析 Cookie 字符串为字典"""
        cookies = {}
        for item in cookie_str.split(";"):
            item = item.strip()
            if "=" in item:
                key, value = item.split("=", 1)
                cookies[key.strip()] = value.strip()
        return cookies
    
    def _build_cookies_for_playwright(self) -> List[Dict]:
        """构建 Playwright 格式的 cookies"""
        cookies = []
        cookie_str = self.cookies.get("cookie", "")
        
        if not cookie_str:
            return cookies
        
        parsed = self._parse_cookie_string(cookie_str)
        
        # 关键 cookie 字段
        important_keys = [
            "web_session", "webId", "webId_v2", "xsecappid",
            "a1", "a2", "gid", "unread", "sec_poison_id"
        ]
        
        for key in important_keys:
            if key in parsed:
                cookies.append({
                    "name": key,
                    "value": parsed[key],
                    "domain": ".xiaohongshu.com",
                    "path": "/"
                })
        
        return cookies
    
    def search(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索笔记 - 使用 Playwright"""
        logger.info(f"搜索小红书: {keyword}")
        
        if not self.cookies_loaded:
            logger.error("小红书未配置，请先运行: python agent-reach.py xiaohongshu config")
            return []
        
        try:
            sync_playwright = self._get_playwright()
            notes = []
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                
                # 添加 cookies
                cookies = self._build_cookies_for_playwright()
                if cookies:
                    context.add_cookies(cookies)
                
                page = context.new_page()
                
                # 访问搜索页面
                search_url = f"https://www.xiaohongshu.com/search_result?keyword={quote(keyword)}&type=51"
                logger.info(f"访问: {search_url}")
                
                page.goto(search_url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(3000)  # 等待内容加载
                
                # 等待笔记卡片出现
                page.wait_for_selector('section.note-item, div.feed-card, a.cover', timeout=10000)
                
                # 提取笔记数据
                # 小红书的 DOM 结构多变，尝试多种选择器
                note_selectors = [
                    'section.note-item',
                    'div.feed-card',
                    'div.card-container',
                    'a[href*="/explore/"]'
                ]
                
                note_elements = []
                for selector in note_selectors:
                    note_elements = page.query_selector_all(selector)
                    if note_elements:
                        logger.debug(f"使用选择器: {selector}, 找到 {len(note_elements)} 个")
                        break
                
                for i, note_el in enumerate(note_elements[:limit], 1):
                    try:
                        note_data = self._extract_note_data(page, note_el)
                        if note_data:
                            notes.append(note_data)
                    except Exception as e:
                        logger.debug(f"提取笔记 {i} 失败: {e}")
                        continue
                
                browser.close()
            
            logger.info(f"找到 {len(notes)} 条笔记")
            return notes
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def _extract_note_data(self, page, note_el) -> Optional[Dict[str, Any]]:
        """从笔记元素提取数据"""
        try:
            # 尝试多种方式获取笔记信息
            
            # 1. 获取链接（笔记ID）
            link = ""
            link_el = note_el.query_selector('a[href*="/explore/"]')
            if link_el:
                href = link_el.get_attribute("href") or ""
                link = href if href.startswith("http") else f"https://www.xiaohongshu.com{href}"
            
            # 提取笔记ID
            note_id = ""
            if "/explore/" in link:
                note_id = link.split("/explore/")[-1].split("?")[0]
            
            # 2. 获取标题
            title = ""
            title_selectors = [
                'span.title',
                '.title',
                'div.title',
                'a.title',
                'span[title]'
            ]
            for selector in title_selectors:
                title_el = note_el.query_selector(selector)
                if title_el:
                    title = title_el.inner_text().strip()
                    if title:
                        break
            
            # 3. 获取作者
            author = ""
            author_selectors = [
                'a.author .name',
                '.author-name',
                'span.author',
                '.user-info .name'
            ]
            for selector in author_selectors:
                author_el = note_el.query_selector(selector)
                if author_el:
                    author = author_el.inner_text().strip()
                    if author:
                        break
            
            # 4. 获取点赞数
            likes = 0
            like_selectors = [
                'span.like-count',
                '.like span',
                'span[class*="like"]',
                '.count'
            ]
            for selector in like_selectors:
                like_el = note_el.query_selector(selector)
                if like_el:
                    like_text = like_el.inner_text()
                    likes = self._parse_count(like_text)
                    if likes > 0:
                        break
            
            # 5. 获取图片
            images = []
            img_el = note_el.query_selector('img')
            if img_el:
                img_url = img_el.get_attribute("src")
                if img_url:
                    images.append(img_url)
            
            return {
                "id": note_id,
                "title": title or "无标题",
                "user": author or "未知作者",
                "likes": likes,
                "url": link or f"https://www.xiaohongshu.com/explore/{note_id}",
                "images": images
            }
            
        except Exception as e:
            logger.debug(f"提取笔记数据失败: {e}")
            return None
    
    def _parse_count(self, text: str) -> int:
        """解析计数文本"""
        text = text.strip()
        if not text:
            return 0
        
        # 处理 万 格式
        if "万" in text:
            num = float(text.replace("万", "").replace(",", ""))
            return int(num * 10000)
        
        # 处理 w 格式
        if "w" in text.lower():
            num = float(text.lower().replace("w", "").replace(",", ""))
            return int(num * 10000)
        
        try:
            return int(text.replace(",", "").replace("+", ""))
        except ValueError:
            return 0
    
    def get_note_detail(self, note_id: str) -> Dict[str, Any]:
        """获取笔记详情"""
        logger.info(f"获取笔记详情: {note_id}")
        
        try:
            sync_playwright = self._get_playwright()
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={"width": 1920, "height": 1080}
                )
                
                cookies = self._build_cookies_for_playwright()
                if cookies:
                    context.add_cookies(cookies)
                
                page = context.new_page()
                url = f"https://www.xiaohongshu.com/explore/{note_id}"
                page.goto(url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(2000)
                
                # 提取详情
                title_el = page.query_selector('h1.title, div.title')
                title = title_el.inner_text() if title_el else ""
                
                content_el = page.query_selector('div.content, div.desc')
                content = content_el.inner_text() if content_el else ""
                
                author_el = page.query_selector('a.author div.info div.nickname, .author-name')
                author = author_el.inner_text() if author_el else ""
                
                browser.close()
                
                return {
                    "id": note_id,
                    "title": title,
                    "content": content,
                    "author": author,
                    "url": url
                }
                
        except Exception as e:
            logger.error(f"获取笔记详情失败: {e}")
            return {"error": str(e)}
    
    def like_note(self, note_id: str) -> Dict[str, Any]:
        """点赞笔记"""
        logger.info(f"点赞笔记: {note_id}")
        
        if not self.cookies_loaded:
            return {"success": False, "error": "Cookie 未配置"}
        
        try:
            sync_playwright = self._get_playwright()
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)  # 点赞用有头更稳定
                context = browser.new_context(viewport={"width": 1920, "height": 1080})
                
                cookies = self._build_cookies_for_playwright()
                if cookies:
                    context.add_cookies(cookies)
                
                page = context.new_page()
                url = f"https://www.xiaohongshu.com/explore/{note_id}"
                page.goto(url, timeout=30000)
                page.wait_for_timeout(2000)
                
                # 找点赞按钮
                like_btn = page.query_selector('span.like-icon, .like-btn, button[class*="like"]')
                if like_btn:
                    like_btn.click()
                    page.wait_for_timeout(1000)
                    
                    browser.close()
                    return {"success": True}
                
                browser.close()
                return {"success": False, "error": "未找到点赞按钮"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def post_note(self, title: str, content: str, images: List[str] = None) -> Dict[str, Any]:
        """发布笔记"""
        logger.info(f"发布笔记: {title}")
        
        if not self.cookies_loaded:
            return {"success": False, "error": "Cookie 未配置"}
        
        logger.warning("发布笔记功能需要手动操作，建议直接使用网页版")
        
        return {
            "success": False,
            "error": "发布功能暂未实现，请使用小红书网页版",
            "tip": "访问 https://creator.xiaohongshu.com/publish/publish"
        }
    
    def get_user_profile(self, user_id: str = None) -> Dict[str, Any]:
        """获取用户资料"""
        logger.info("获取用户信息")
        
        try:
            sync_playwright = self._get_playwright()
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(viewport={"width": 1920, "height": 1080})
                
                cookies = self._build_cookies_for_playwright()
                if cookies:
                    context.add_cookies(cookies)
                
                page = context.new_page()
                
                if user_id:
                    page.goto(f"https://www.xiaohongshu.com/user/profile/{user_id}", timeout=30000)
                else:
                    page.goto("https://www.xiaohongshu.com/user/me", timeout=30000)
                
                page.wait_for_timeout(2000)
                
                # 提取用户信息
                name_el = page.query_selector('.user-nickname, .nickname')
                name = name_el.inner_text() if name_el else ""
                
                browser.close()
                
                return {"nickname": name}
                
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return {"error": str(e)}
