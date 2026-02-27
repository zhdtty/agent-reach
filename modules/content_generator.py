"""
AI 内容生成模块
集成 LLM 生成推文、笔记内容
"""

import os
from typing import Optional
from base import logger


class ContentGenerator:
    """内容生成器 - 使用 AI 生成社交媒体内容"""
    
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "openai")  # openai, gemini, local
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    def generate_tweet(self, topic: str, tone: str = "casual", max_length: int = 280) -> str:
        """生成推文"""
        prompt = f"""写一条关于"{topic}"的推文。
风格：{tone}
限制：{max_length} 字符以内
要求：吸引人、有互动性、可加 emoji

直接返回推文内容，不要解释。"""
        
        return self._call_llm(prompt)
    
    def generate_xiaohongshu_note(self, topic: str, style: str = "干货") -> dict:
        """生成小红书笔记"""
        prompt = f"""写一篇关于"{topic}"的小红书笔记。
风格：{style}
格式：JSON，包含 title 和 content

要求：
- 标题吸引人，带 emoji
- 内容有干货，分点说明
- 语气亲切像朋友分享

只返回 JSON 格式：{{"title": "...", "content": "..."}}"""
        
        response = self._call_llm(prompt)
        try:
            import json
            return json.loads(response)
        except:
            # 解析失败，手动分割
            lines = response.split("\n")
            title = lines[0].replace("标题：", "").strip() if lines else topic
            content = "\n".join(lines[1:]).strip()
            return {"title": title, "content": content}
    
    def generate_reply(self, original_text: str, context: str = "") -> str:
        """生成回复"""
        prompt = f"""针对以下推文写一条回复：

原推文：{original_text}
上下文：{context}

要求：
- 真诚、有见地
- 可以提问或补充观点
- 自然不做作

直接返回回复内容。"""
        
        return self._call_llm(prompt)
    
    def generate_hashtags(self, content: str, platform: str = "twitter") -> str:
        """生成标签"""
        count = 3 if platform == "twitter" else 5
        
        prompt = f"""为以下内容生成 {count} 个合适的 hashtag：

内容：{content}
平台：{platform}

要求：
- 相关度高
- 热度适中（不要太泛也不要太冷门）
- 直接返回 hashtag 列表，用空格分隔

例如：#AI #科技 #创新"""
        
        return self._call_llm(prompt)
    
    def _call_llm(self, prompt: str) -> str:
        """调用 LLM"""
        if not self.api_key:
            logger.warning("未配置 AI API Key，使用模拟响应")
            return self._mock_response(prompt)
        
        try:
            if self.provider == "openai":
                return self._call_openai(prompt)
            elif self.provider == "gemini":
                return self._call_gemini(prompt)
            else:
                return self._mock_response(prompt)
        except Exception as e:
            logger.error(f"AI 调用失败: {e}")
            return self._mock_response(prompt)
    
    def _call_openai(self, prompt: str) -> str:
        """调用 OpenAI"""
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个社交媒体内容创作专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except ImportError:
            logger.error("openai 库未安装，运行: pip install openai")
            return self._mock_response(prompt)
    
    def _call_gemini(self, prompt: str) -> str:
        """调用 Gemini"""
        logger.warning("Gemini 支持开发中，使用模拟响应")
        return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """模拟响应（无 AI Key 时用）"""
        # 简单的模板回复
        if "推文" in prompt or "tweet" in prompt.lower():
            topics = ["AI", "科技", "生活", "工作"]
            for t in topics:
                if t in prompt:
                    return f"刚发现了一个超棒的{t}小技巧！🚀 真的能提升效率，你们试过吗？ #分享 #{t}"
            return "今天学到了新东西，分享一下！💡 保持好奇心真的很重要。"
        
        elif "小红书" in prompt:
            return '{"title": "💡 这个技巧真的绝了！", "content": "姐妹们，今天分享一个我发现的神仙技巧！\n\n✅ 第一点：简单易上手\n✅ 第二点：效果立竿见影\n✅ 第三点：零成本\n\n快去试试吧，真的有用！记得收藏～"}'
        
        elif "回复" in prompt:
            return "说得太对了！我也有类似的经历，感谢分享 🙏"
        
        elif "hashtag" in prompt.lower() or "标签" in prompt:
            return "#分享 #干货 #生活小技巧"
        
        return "（AI 内容生成需要配置 OPENAI_API_KEY 环境变量）"
