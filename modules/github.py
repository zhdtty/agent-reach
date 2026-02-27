"""
GitHub 模块 - 基于 gh CLI
"""

import json
import subprocess
from typing import List, Dict, Any, Optional

from base import BaseClient, logger


class GitHubClient(BaseClient):
    """GitHub 客户端 - 使用官方 CLI"""
    
    def __init__(self):
        super().__init__(None)
        self._check_auth()
    
    def _check_auth(self):
        """检查是否已登录"""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                logger.warning("GitHub CLI 未登录，请先运行: gh auth login")
        except FileNotFoundError:
            logger.error("未找到 gh CLI，请先安装: brew install gh")
    
    def _run_gh_command(self, args: List[str]) -> Dict[str, Any]:
        """运行 gh 命令"""
        cmd = ["gh"] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            if result.stdout:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return {"output": result.stdout}
            return {}
        except subprocess.CalledProcessError as e:
            logger.error(f"gh 命令失败: {e.stderr}")
            return {"error": e.stderr}
    
    def search_repos(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索仓库"""
        logger.info(f"搜索 GitHub 仓库: {query}")
        
        result = self._run_gh_command([
            "search", "repos",
            query,
            "--limit", str(limit),
            "--json", "name,fullName,description,url,stargazersCount,forksCount,language"
        ])
        
        if isinstance(result, list):
            # 转换字段名
            repos = []
            for item in result:
                repos.append({
                    "name": item.get("name"),
                    "full_name": item.get("fullName"),
                    "description": item.get("description"),
                    "html_url": item.get("url"),
                    "stargazers_count": item.get("stargazersCount", 0),
                    "forks_count": item.get("forksCount", 0),
                    "language": item.get("language")
                })
            return repos
        
        return []
    
    def get_repo(self, repo: str) -> Dict[str, Any]:
        """获取仓库详情"""
        logger.info(f"获取仓库信息: {repo}")
        
        result = self._run_gh_command([
            "repo", "view", repo,
            "--json", "name,fullName,description,url,stargazersCount,forksCount,topics,defaultBranch"
        ])
        
        return {
            "name": result.get("name"),
            "full_name": result.get("fullName"),
            "description": result.get("description"),
            "html_url": result.get("url"),
            "stargazers_count": result.get("stargazersCount", 0),
            "forks_count": result.get("forksCount", 0),
            "topics": result.get("topics", []),
            "default_branch": result.get("defaultBranch")
        }
    
    def create_issue(self, repo: str, title: str, body: str = "") -> Dict[str, Any]:
        """创建 Issue"""
        logger.info(f"创建 Issue: {title}")
        
        cmd = ["issue", "create", "--repo", repo, "--title", title]
        if body:
            cmd.extend(["--body", body])
        
        result = self._run_gh_command(cmd)
        return result
    
    def list_issues(self, repo: str, limit: int = 10) -> List[Dict[str, Any]]:
        """列出仓库 Issues"""
        result = self._run_gh_command([
            "issue", "list",
            "--repo", repo,
            "--limit", str(limit),
            "--json", "number,title,state,author,url"
        ])
        
        return result if isinstance(result, list) else []
