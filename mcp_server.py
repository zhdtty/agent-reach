#!/usr/bin/env python3
"""
Agent-Reach MCP Server
让 OpenClaw 能直接调用 Agent-Reach 功能
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 添加 modules 到路径
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from github import GitHubClient
from twitter import TwitterClient
from xiaohongshu import XiaoHongShuClient


class MCPServer:
    """MCP 服务器实现"""
    
    def __init__(self):
        self.cookies_dir = Path(__file__).parent / "cookies"
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[Dict]:
        """定义可用工具"""
        return [
            {
                "name": "github_search",
                "description": "搜索 GitHub 仓库",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "搜索关键词"},
                        "limit": {"type": "integer", "description": "返回数量", "default": 10}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "github_view_repo",
                "description": "查看 GitHub 仓库详情",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "repo": {"type": "string", "description": "仓库名 (格式: owner/repo)"}
                    },
                    "required": ["repo"]
                }
            },
            {
                "name": "twitter_search",
                "description": "搜索 Twitter/X 推文",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "搜索关键词"},
                        "limit": {"type": "integer", "description": "返回数量", "default": 5}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "twitter_timeline",
                "description": "获取 Twitter/X 用户时间线",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user": {"type": "string", "description": "用户名（不含@）"},
                        "limit": {"type": "integer", "description": "返回数量", "default": 5}
                    },
                    "required": ["user"]
                }
            },
            {
                "name": "twitter_post",
                "description": "发布 Twitter/X 推文",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "推文内容"}
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "xiaohongshu_search",
                "description": "搜索小红书笔记",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string", "description": "搜索关键词"},
                        "limit": {"type": "integer", "description": "返回数量", "default": 5}
                    },
                    "required": ["keyword"]
                }
            },
            {
                "name": "xiaohongshu_note_detail",
                "description": "获取小红书笔记详情",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "note_id": {"type": "string", "description": "笔记 ID"}
                    },
                    "required": ["note_id"]
                }
            },
            {
                "name": "xiaohongshu_like",
                "description": "点赞小红书笔记",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "note_id": {"type": "string", "description": "笔记 ID"}
                    },
                    "required": ["note_id"]
                }
            }
        ]
    
    def run(self):
        """运行 MCP 服务器"""
        for line in sys.stdin:
            try:
                request = json.loads(line)
                response = self._handle_request(request)
                if response:
                    print(json.dumps(response, ensure_ascii=False), flush=True)
            except json.JSONDecodeError:
                continue
    
    def _handle_request(self, request: Dict) -> Optional[Dict]:
        """处理请求"""
        method = request.get("method")
        request_id = request.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "agent-reach-mcp",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": self.tools}
            }
        
        elif method == "tools/call":
            return self._handle_tool_call(request)
        
        return None
    
    def _handle_tool_call(self, request: Dict) -> Dict:
        """处理工具调用"""
        request_id = request.get("id")
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            result = self._execute_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"工具执行失败: {str(e)}"
                }
            }
    
    def _execute_tool(self, name: str, args: Dict) -> Dict:
        """执行具体工具"""
        
        # GitHub 工具
        if name == "github_search":
            client = GitHubClient()
            return {"repositories": client.search_repos(args["query"], args.get("limit", 10))}
        
        elif name == "github_view_repo":
            client = GitHubClient()
            return {"repository": client.get_repo(args["repo"])}
        
        # Twitter 工具
        elif name == "twitter_search":
            cookie_file = self.cookies_dir / "twitter.json"
            client = TwitterClient(cookie_file)
            return {"tweets": client.search(args["query"], args.get("limit", 5))}
        
        elif name == "twitter_timeline":
            cookie_file = self.cookies_dir / "twitter.json"
            client = TwitterClient(cookie_file)
            return {"tweets": client.get_timeline(args["user"], args.get("limit", 5))}
        
        elif name == "twitter_post":
            cookie_file = self.cookies_dir / "twitter.json"
            client = TwitterClient(cookie_file)
            return client.post_tweet(args["text"])
        
        # 小红书工具
        elif name == "xiaohongshu_search":
            cookie_file = self.cookies_dir / "xiaohongshu.json"
            client = XiaoHongShuClient(cookie_file)
            return {"notes": client.search(args["keyword"], args.get("limit", 5))}
        
        elif name == "xiaohongshu_note_detail":
            cookie_file = self.cookies_dir / "xiaohongshu.json"
            client = XiaoHongShuClient(cookie_file)
            return {"note": client.get_note_detail(args["note_id"])}
        
        elif name == "xiaohongshu_like":
            cookie_file = self.cookies_dir / "xiaohongshu.json"
            client = XiaoHongShuClient(cookie_file)
            return client.like_note(args["note_id"])
        
        else:
            raise ValueError(f"未知工具: {name}")


if __name__ == "__main__":
    server = MCPServer()
    server.run()
