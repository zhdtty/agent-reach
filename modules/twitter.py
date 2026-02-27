#!/usr/bin/env python3
"""
Twitter/X 模块 - 基于 Playwright 浏览器自动化
更稳定，绕过 API 限制
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

from base import BaseClient, logger


class TwitterClient(BaseClient):
    """Twitter/X 客户端 - 使用 Playwright 浏览器自动化"""
    
    def __init__(self, cookie_file: Path):
        super().__init__(cookie_file)
        self.base_url = "https://x.com"
        self.cookies_loaded = bool(self.cookies)
        
        if not self.cookies_loaded:
            logger.warning("Twitter Cookie 未配置")
    
    def _get_playwright(self):
        """延迟导入 playwright"""
        try:
            from playwright.sync_api import sync_playwright
            return sync_playwright
        except ImportError:
            logger.error("Playwright 未安装，运行: pip install playwright && playwright install chromium")
            raise
    
    def _build_cookies_for_playwright(self) -> List[Dict]:
        """构建 Playwright 格式的 cookies"""
        cookies = []
        
        # 从 cookie 文件读取
        auth_token = self.cookies.get("auth_token", "")
        ct0 = self.cookies.get("ct0", "")
        twid = self.cookies.get("twid", "")
        
        if auth_token:
            cookies.append({
                "name": "auth_token",
                "value": auth_token,
                "domain": ".x.com",
                "path": "/"
            })
        if ct0:
            cookies.append({
                "name": "ct0",
                "value": ct0,
                "domain": ".x.com",
                "path": "/"
            })
        if twid:
            cookies.append({
                "name": "twid",
                "value": twid,
                "domain": ".x.com",
                "path": "/"
            })
        
        return cookies
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索推文 - 使用 Playwright"""
        logger.info(f"搜索 Twitter: {query}")
        
        if not self.cookies_loaded:
            logger.error("Twitter 未配置，请先运行: python agent-reach.py twitter config")
            return []
        
        try:
            sync_playwright = self._get_playwright()
            tweets = []
            
            with sync_playwright() as p:
                # 启动浏览器
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
                search_url = f"https://x.com/search?q={query}&src=typed_query&f=live"
                logger.info(f"访问: {search_url}")
                
                page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(3000)  # 等待内容加载
                
                # 提取推文数据
                tweet_elements = page.query_selector_all('article[data-testid="tweet"]')
                
                for i, tweet_el in enumerate(tweet_elements[:limit], 1):
                    try:
                        tweet_data = self._extract_tweet_data(page, tweet_el)
                        if tweet_data:
                            tweets.append(tweet_data)
                    except Exception as e:
                        logger.debug(f"提取推文 {i} 失败: {e}")
                        continue
                
                browser.close()
            
            logger.info(f"找到 {len(tweets)} 条推文")
            return tweets
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def _extract_tweet_data(self, page, tweet_el) -> Optional[Dict[str, Any]]:
        """从推文元素提取数据"""
        try:
            # 用户名
            user_el = tweet_el.query_selector('a[role="link"] div[dir="ltr"] span')
            user = ""
            if user_el:
                user = user_el.inner_text().replace("@", "")
            
            # 推文内容
            text_el = tweet_el.query_selector('[data-testid="tweetText"]')
            text = ""
            if text_el:
                text = text_el.inner_text()
            
            # 时间
            time_el = tweet_el.query_selector('time')
            time_str = ""
            if time_el:
                time_str = time_el.get_attribute('datetime') or ""
            
            # 点赞数
            likes = 0
            like_el = tweet_el.query_selector('[data-testid="like"]')
            if like_el:
                like_text = like_el.inner_text()
                likes = self._parse_count(like_text)
            
            # 转发数
            retweets = 0
            retweet_el = tweet_el.query_selector('[data-testid="retweet"]')
            if retweet_el:
                retweet_text = retweet_el.inner_text()
                retweets = self._parse_count(retweet_text)
            
            # 评论数
            replies = 0
            reply_el = tweet_el.query_selector('[data-testid="reply"]')
            if reply_el:
                reply_text = reply_el.inner_text()
                replies = self._parse_count(reply_text)
            
            return {
                "user": user,
                "text": text,
                "time": time_str,
                "likes": likes,
                "retweets": retweets,
                "replies": replies
            }
        except Exception as e:
            logger.debug(f"提取推文数据失败: {e}")
            return None
    
    def _parse_count(self, text: str) -> int:
        """解析计数文本"""
        text = text.strip()
        if not text or text == "":
            return 0
        
        # 处理 K/M 格式
        if "K" in text:
            num = float(text.replace("K", "").replace(",", ""))
            return int(num * 1000)
        elif "M" in text:
            num = float(text.replace("M", "").replace(",", ""))
            return int(num * 1000000)
        
        try:
            return int(text.replace(",", ""))
        except ValueError:
            return 0
    
    def get_timeline(self, user: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """获取时间线"""
        if user:
            logger.info(f"获取用户 @{user} 的时间线")
            url = f"https://x.com/{user}"
        else:
            logger.info("获取首页时间线")
            url = "https://x.com/home"
        
        try:
            sync_playwright = self._get_playwright()
            tweets = []
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                )
                
                cookies = self._build_cookies_for_playwright()
                if cookies:
                    context.add_cookies(cookies)
                
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(3000)
                
                tweet_elements = page.query_selector_all('article[data-testid="tweet"]')
                
                for tweet_el in tweet_elements[:limit]:
                    tweet_data = self._extract_tweet_data(page, tweet_el)
                    if tweet_data:
                        tweets.append(tweet_data)
                
                browser.close()
            
            return tweets
            
        except Exception as e:
            logger.error(f"获取时间线失败: {e}")
            return []
    
    def post_tweet(self, text: str) -> Dict[str, Any]:
        """发布推文"""
        logger.info(f"发布推文: {text[:30]}...")
        
        if not self.cookies_loaded:
            return {"success": False, "error": "Cookie 未配置"}
        
        try:
            sync_playwright = self._get_playwright()
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)  # 发布用有头模式更稳定
                context = browser.new_context(
                    viewport={"width": 1920, "height": 1080}
                )
                
                cookies = self._build_cookies_for_playwright()
                if cookies:
                    context.add_cookies(cookies)
                
                page = context.new_page()
                page.goto("https://x.com/compose/tweet", timeout=30000)
                page.wait_for_timeout(2000)
                
                # 找到文本框并输入
                textbox = page.query_selector('[data-testid="tweetTextarea_0"]')
                if not textbox:
                    textbox = page.query_selector('div[contenteditable="true"]')
                
                if textbox:
                    textbox.fill(text)
                    page.wait_for_timeout(500)
                    
                    # 点击发布按钮
                    post_btn = page.query_selector('[data-testid="tweetButton"]')
                    if post_btn:
                        post_btn.click()
                        page.wait_for_timeout(2000)
                        
                        browser.close()
                        return {"success": True, "message": "推文已发布"}
                
                browser.close()
                return {"success": False, "error": "未找到发布按钮"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_user_info(self, username: str) -> Dict[str, Any]:
        """获取用户信息"""
        logger.info(f"获取用户信息: @{username}")
        
        try:
            sync_playwright = self._get_playwright()
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(viewport={"width": 1920, "height": 1080})
                
                cookies = self._build_cookies_for_playwright()
                if cookies:
                    context.add_cookies(cookies)
                
                page = context.new_page()
                page.goto(f"https://x.com/{username}", timeout=30000)
                page.wait_for_timeout(2000)
                
                # 提取用户信息
                name_el = page.query_selector('[data-testid="UserName"]')
                name = ""
                if name_el:
                    name = name_el.inner_text().split("\n")[0]
                
                bio_el = page.query_selector('[data-testid="UserDescription"]')
                bio = ""
                if bio_el:
                    bio = bio_el.inner_text()
                
                # 统计信息
                stats = page.query_selector_all('[role="group"] a')
                followers = 0
                following = 0
                
                for stat in stats:
                    href = stat.get_attribute("href") or ""
                    if "followers" in href:
                        text = stat.inner_text()
                        followers = self._parse_count(text.split(" ")[0])
                    elif "following" in href:
                        text = stat.inner_text()
                        following = self._parse_count(text.split(" ")[0])
                
                browser.close()
                
                return {
                    "name": name,
                    "screen_name": username,
                    "description": bio,
                    "followers": followers,
                    "following": following
                }
                
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return {}
