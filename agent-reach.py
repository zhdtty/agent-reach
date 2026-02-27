#!/usr/bin/env python3
"""
Agent-Reach - 东哥的 Agent 网络访问工具
无需 Docker，本地直跑！
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel

# 添加 modules 到路径
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from twitter import TwitterClient
from xiaohongshu import XiaoHongShuClient
from github import GitHubClient

console = Console()

COOKIES_DIR = Path(__file__).parent / "cookies"
COOKIES_DIR.mkdir(exist_ok=True)


def print_banner():
    console.print(Panel.fit(
        "[bold cyan]🦞 Agent-Reach[/bold cyan] - 东哥的午夜码魂网络工具\n"
        "[dim]GitHub ✓ | Twitter/X ✓ | 小红书 ✓ | 无需 Docker[/dim]",
        border_style="green"
    ))


@click.group()
def cli():
    """Agent-Reach - AI Agent 网络访问工具"""
    print_banner()


# ==================== GitHub ====================
@cli.group()
def github():
    """GitHub 操作"""
    pass


@github.command()
@click.argument("query")
@click.option("--limit", "-l", default=10, help="返回结果数量")
def search(query: str, limit: int):
    """搜索 GitHub 仓库"""
    client = GitHubClient()
    results = client.search_repos(query, limit)
    
    for i, repo in enumerate(results, 1):
        console.print(f"\n[bold]{i}. {repo['full_name']}[/bold]")
        console.print(f"   [dim]{repo.get('description', '无描述')}[/dim]")
        console.print(f"   ⭐ {repo.get('stargazers_count', 0)} | 🍴 {repo.get('forks_count', 0)}")
        console.print(f"   [blue]{repo['html_url']}[/blue]")


@github.command()
@click.argument("repo")
def view(repo: str):
    """查看仓库详情 (格式: owner/repo)"""
    client = GitHubClient()
    info = client.get_repo(repo)
    
    console.print(f"\n[bold cyan]{info['full_name']}[/bold cyan]")
    console.print(f"[dim]{info.get('description', '无描述')}[/dim]")
    console.print(f"⭐ Stars: {info.get('stargazers_count', 0)}")
    console.print(f"🌐 {info['html_url']}")


# ==================== Twitter/X ====================
@cli.group()
def twitter():
    """Twitter/X 操作"""
    pass


@twitter.command()
def config():
    """配置 Twitter Cookie"""
    console.print("\n[bold yellow]🔐 Twitter Cookie 配置指南[/bold yellow]\n")
    console.print("1. 用浏览器登录 https://twitter.com 或 https://x.com")
    console.print("2. 按 F12 打开开发者工具 → Application/应用 → Cookies")
    console.print("3. 复制以下字段的值:\n")
    console.print("   - auth_token")
    console.print("   - ct0")
    console.print("   - twid\n")
    
    auth_token = click.prompt("auth_token", hide_input=True)
    ct0 = click.prompt("ct0", hide_input=True)
    twid = click.prompt("twid (u%3D123456... 格式)", hide_input=True)
    
    cookie_data = {
        "auth_token": auth_token,
        "ct0": ct0,
        "twid": twid
    }
    
    cookie_file = COOKIES_DIR / "twitter.json"
    with open(cookie_file, "w") as f:
        json.dump(cookie_data, f, indent=2)
    
    console.print(f"\n[green]✓ Cookie 已保存到: {cookie_file}[/green]")
    console.print("[dim]安全提示: 仅本地存储，不上传任何服务器[/dim]")


@twitter.command()
@click.argument("query")
@click.option("--limit", "-l", default=10, help="返回推文数量")
def search(query: str, limit: int):
    """搜索推文"""
    client = TwitterClient(COOKIES_DIR / "twitter.json")
    tweets = client.search(query, limit)
    
    for i, tweet in enumerate(tweets, 1):
        console.print(f"\n[bold cyan]@{tweet['user']}[/bold cyan]")
        console.print(f"{tweet['text']}")
        console.print(f"[dim]♥ {tweet.get('likes', 0)} | 🔄 {tweet.get('retweets', 0)} | {tweet['time']}[/dim]")


@twitter.command()
@click.argument("text")
def post(text: str):
    """发布推文"""
    client = TwitterClient(COOKIES_DIR / "twitter.json")
    result = client.post_tweet(text)
    
    if result.get("success"):
        console.print(f"\n[green]✓ 推文已发布![/green]")
        console.print(f"[blue]{result.get('url', '')}[/blue]")
    else:
        console.print(f"\n[red]✗ 发布失败: {result.get('error', '未知错误')}[/red]")


@twitter.command()
@click.option("--user", "-u", help="查看指定用户的时间线")
@click.option("--limit", "-l", default=10, help="返回推文数量")
def timeline(user: Optional[str], limit: int):
    """查看时间线"""
    client = TwitterClient(COOKIES_DIR / "twitter.json")
    tweets = client.get_timeline(user, limit)
    
    for tweet in tweets:
        console.print(f"\n[bold cyan]@{tweet['user']}[/bold cyan]")
        console.print(f"{tweet['text']}")
        console.print(f"[dim]{tweet['time']}[/dim]")


# ==================== 小红书 ====================
@cli.group()
def xiaohongshu():
    """小红书操作"""
    pass


@xiaohongshu.command()
def config():
    """配置小红书 Cookie"""
    console.print("\n[bold red]📕 小红书 Cookie 配置指南[/bold red]\n")
    console.print("1. 用浏览器登录 https://www.xiaohongshu.com")
    console.print("2. 按 F12 打开开发者工具")
    console.print("3. 切换到 Network/网络 标签")
    console.print("4. 刷新页面，找到任意请求（如 me 或 user）")
    console.print("5. 右键请求 → Copy → Copy as cURL")
    console.print("6. 从 cURL 中提取完整的 Cookie 字符串\n")
    
    cookie_str = click.prompt("Cookie 字符串", hide_input=True)
    
    cookie_file = COOKIES_DIR / "xiaohongshu.json"
    with open(cookie_file, "w") as f:
        json.dump({"cookie": cookie_str}, f, indent=2)
    
    console.print(f"\n[green]✓ Cookie 已保存到: {cookie_file}[/green]")


@xiaohongshu.command()
@click.argument("keyword")
@click.option("--limit", "-l", default=10, help="返回结果数量")
def search(keyword: str, limit: int):
    """搜索笔记"""
    client = XiaoHongShuClient(COOKIES_DIR / "xiaohongshu.json")
    notes = client.search(keyword, limit)
    
    for i, note in enumerate(notes, 1):
        console.print(f"\n[bold red]{i}. {note['title']}[/bold red]")
        console.print(f"   [dim]作者: @{note['user']}[/dim]")
        console.print(f"   ♥ {note.get('likes', 0)} | 💬 {note.get('comments', 0)}")
        console.print(f"   [blue]https://www.xiaohongshu.com/explore/{note['id']}[/blue]")


@xiaohongshu.command()
@click.argument("note_id")
def like(note_id: str):
    """点赞笔记"""
    client = XiaoHongShuClient(COOKIES_DIR / "xiaohongshu.json")
    result = client.like_note(note_id)
    
    if result.get("success"):
        console.print(f"\n[green]✓ 已点赞笔记 {note_id}[/green]")
    else:
        console.print(f"\n[red]✗ 点赞失败: {result.get('error', '未知错误')}[/red]")


@xiaohongshu.command()
@click.argument("content")
@click.option("--title", "-t", help="笔记标题")
def post(content: str, title: Optional[str]):
    """发布笔记"""
    client = XiaoHongShuClient(COOKIES_DIR / "xiaohongshu.json")
    result = client.post_note(title or "", content)
    
    if result.get("success"):
        console.print(f"\n[green]✓ 笔记已发布![/green]")
        console.print(f"[blue]{result.get('url', '')}[/blue]")
    else:
        console.print(f"\n[red]✗ 发布失败: {result.get('error', '未知错误')}[/red]")


if __name__ == "__main__":
    cli()
