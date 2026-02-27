#!/usr/bin/env python3
"""
Agent-Reach - 东哥的午夜码魂网络工具
无需 Docker，本地直跑！
支持多账号 + Stealth 模式 + AI 内容生成
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
        "[dim]GitHub ✓ | Twitter/X ✓ | 小红书 ✓ | 无需 Docker[/dim]\n"
        "[green]✨ 多账号 | 🥷 Stealth | 🤖 AI 生成[/green]",
        border_style="green"
    ))


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="详细输出")
def cli(verbose):
    """Agent-Reach - AI Agent 网络访问工具"""
    print_banner()
    if verbose:
        console.print("[dim]详细模式已开启[/dim]")


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
@click.option("--account", "-a", default="default", help="账号名称 (默认: default)")
@click.option("--no-stealth", is_flag=True, help="关闭 Stealth 模式")
@click.pass_context
def twitter(ctx, account: str, no_stealth: bool):
    """Twitter/X 操作（支持多账号）"""
    ctx.ensure_object(dict)
    ctx.obj["account"] = account
    ctx.obj["stealth"] = not no_stealth


@twitter.command()
@click.pass_context
def config(ctx):
    """配置 Twitter Cookie（支持多账号）"""
    account = ctx.obj["account"]
    console.print(f"\n[bold yellow]🔐 Twitter Cookie 配置 - 账号: {account}[/bold yellow]\n")
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

    cookie_file = COOKIES_DIR / f"twitter_{account}.json"
    with open(cookie_file, "w") as f:
        json.dump(cookie_data, f, indent=2)

    console.print(f"\n[green]✓ Cookie 已保存到: {cookie_file}[/green]")
    console.print(f"[dim]使用: python agent-reach.py twitter -a {account} search ...[/dim]")


@twitter.command()
@click.argument("query")
@click.option("--limit", "-l", default=10, help="返回推文数量")
@click.pass_context
def search(ctx, query: str, limit: int):
    """搜索推文"""
    account = ctx.obj["account"]
    stealth = ctx.obj["stealth"]
    cookie_file = COOKIES_DIR / f"twitter_{account}.json"

    client = TwitterClient(cookie_file, account=account, stealth=stealth)
    tweets = client.search(query, limit)

    for i, tweet in enumerate(tweets, 1):
        console.print(f"\n[bold cyan]@{tweet['user']}[/bold cyan]")
        console.print(f"{tweet['text']}")
        console.print(f"[dim]♥ {tweet.get('likes', 0)} | 🔄 {tweet.get('retweets', 0)} | {tweet['time']}[/dim]")


@twitter.command()
@click.option("--text", "-t", help="推文内容（可选，与 --ai 二选一）")
@click.option("--topic", help="AI 生成主题（可选）")
@click.option("--ai", is_flag=True, help="使用 AI 生成推文")
@click.pass_context
def post(ctx, text: str, topic: str, ai: bool):
    """发布推文（支持 AI 生成）"""
    account = ctx.obj["account"]
    stealth = ctx.obj["stealth"]
    cookie_file = COOKIES_DIR / f"twitter_{account}.json"

    client = TwitterClient(cookie_file, account=account, stealth=stealth)
    result = client.post_tweet(text=text, topic=topic, use_ai=ai)

    if result.get("success"):
        console.print(f"\n[green]✓ 推文已发布![/green]")
        if result.get("text"):
            console.print(f"[dim]内容: {result['text'][:100]}...[/dim]")
    else:
        console.print(f"\n[red]✗ 发布失败: {result.get('error', '未知错误')}[/red]")


@twitter.command()
@click.option("--user", "-u", help="查看指定用户的时间线")
@click.option("--limit", "-l", default=10, help="返回推文数量")
@click.pass_context
def timeline(ctx, user: Optional[str], limit: int):
    """查看时间线"""
    account = ctx.obj["account"]
    stealth = ctx.obj["stealth"]
    cookie_file = COOKIES_DIR / f"twitter_{account}.json"

    client = TwitterClient(cookie_file, account=account, stealth=stealth)
    tweets = client.get_timeline(user, limit)

    for tweet in tweets:
        console.print(f"\n[bold cyan]@{tweet['user']}[/bold cyan]")
        console.print(f"{tweet['text']}")
        console.print(f"[dim]{tweet['time']}[/dim]")


@twitter.command()
@click.argument("url")
@click.option("--text", "-t", help="回复内容（可选，与 --ai 二选一）")
@click.option("--ai", is_flag=True, help="使用 AI 生成回复")
@click.pass_context
def reply(ctx, url: str, text: str, ai: bool):
    """回复推文"""
    account = ctx.obj["account"]
    stealth = ctx.obj["stealth"]
    cookie_file = COOKIES_DIR / f"twitter_{account}.json"

    client = TwitterClient(cookie_file, account=account, stealth=stealth)
    result = client.reply_to_tweet(url, text=text, use_ai=ai)

    if result.get("success"):
        console.print(f"\n[green]✓ 回复已发布![/green]")
        if result.get("text"):
            console.print(f"[dim]内容: {result['text'][:100]}...[/dim]")
    else:
        console.print(f"\n[red]✗ 回复失败: {result.get('error', '未知错误')}[/red]")


# ==================== 小红书 ====================
@cli.group()
@click.option("--account", "-a", default="default", help="账号名称 (默认: default)")
@click.option("--no-stealth", is_flag=True, help="关闭 Stealth 模式")
@click.pass_context
def xiaohongshu(ctx, account: str, no_stealth: bool):
    """小红书操作（支持多账号）"""
    ctx.ensure_object(dict)
    ctx.obj["account"] = account
    ctx.obj["stealth"] = not no_stealth


@xiaohongshu.command()
@click.pass_context
def config(ctx):
    """配置小红书 Cookie（支持多账号）"""
    account = ctx.obj["account"]
    console.print(f"\n[bold red]📕 小红书 Cookie 配置 - 账号: {account}[/bold red]\n")
    console.print("1. 用浏览器登录 https://www.xiaohongshu.com")
    console.print("2. 按 F12 打开开发者工具")
    console.print("3. 切换到 Network/网络 标签")
    console.print("4. 刷新页面，找到任意请求（如 me 或 user）")
    console.print("5. 右键请求 → Copy → Copy as cURL")
    console.print("6. 从 cURL 中提取完整的 Cookie 字符串\n")

    cookie_str = click.prompt("Cookie 字符串", hide_input=True)

    cookie_file = COOKIES_DIR / f"xiaohongshu_{account}.json"
    with open(cookie_file, "w") as f:
        json.dump({"cookie": cookie_str}, f, indent=2)

    console.print(f"\n[green]✓ Cookie 已保存到: {cookie_file}[/green]")
    console.print(f"[dim]使用: python agent-reach.py xiaohongshu -a {account} search ...[/dim]")


@xiaohongshu.command()
@click.argument("keyword")
@click.option("--limit", "-l", default=10, help="返回结果数量")
@click.pass_context
def search(ctx, keyword: str, limit: int):
    """搜索笔记"""
    account = ctx.obj["account"]
    stealth = ctx.obj["stealth"]
    cookie_file = COOKIES_DIR / f"xiaohongshu_{account}.json"

    client = XiaoHongShuClient(cookie_file, account=account, stealth=stealth)
    notes = client.search(keyword, limit)

    for i, note in enumerate(notes, 1):
        console.print(f"\n[bold red]{i}. {note['title']}[/bold red]")
        console.print(f"   [dim]作者: @{note['user']}[/dim]")
        console.print(f"   ♥ {note.get('likes', 0)}")
        console.print(f"   [blue]{note['url']}[/blue]")


@xiaohongshu.command()
@click.argument("note_id")
@click.pass_context
def like(ctx, note_id: str):
    """点赞笔记"""
    account = ctx.obj["account"]
    stealth = ctx.obj["stealth"]
    cookie_file = COOKIES_DIR / f"xiaohongshu_{account}.json"

    client = XiaoHongShuClient(cookie_file, account=account, stealth=stealth)
    result = client.like_note(note_id)

    if result.get("success"):
        console.print(f"\n[green]✓ 已点赞笔记 {note_id}[/green]")
    else:
        console.print(f"\n[red]✗ 点赞失败: {result.get('error', '未知错误')}[/red]")


@xiaohongshu.command()
@click.option("--topic", "-t", required=True, help="笔记主题（AI 生成）")
@click.option("--style", default="干货", help="笔记风格")
@click.pass_context
def generate(ctx, topic: str, style: str):
    """AI 生成小红书笔记"""
    from content_generator import ContentGenerator

    console.print(f"\n[yellow]🤖 AI 正在生成小红书笔记...[/yellow]")
    console.print(f"[dim]主题: {topic} | 风格: {style}[/dim]\n")

    generator = ContentGenerator()
    note = generator.generate_xiaohongshu_note(topic, style)

    console.print(f"[bold red]标题: {note['title']}[/bold red]")
    console.print(f"\n{note['content']}")
    console.print(f"\n[dim]💡 提示: 复制以上内容到小红书发布[/dim]")


# ==================== AI 生成工具 ====================
@cli.group()
def ai():
    """AI 内容生成工具"""
    pass


@ai.command()
@click.argument("topic")
@click.option("--platform", "-p", default="twitter", type=click.Choice(["twitter", "xiaohongshu"]), help="目标平台")
@click.option("--tone", default="casual", help="语气风格")
def content(topic: str, platform: str, tone: str):
    """生成社交媒体内容"""
    from content_generator import ContentGenerator

    generator = ContentGenerator()

    console.print(f"\n[yellow]🤖 正在生成 {platform} 内容...[/yellow]\n")

    if platform == "twitter":
        text = generator.generate_tweet(topic, tone)
        console.print(f"[bold cyan]推文内容:[/bold cyan]")
        console.print(f"{text}")
        console.print(f"\n[dim]长度: {len(text)}/280[/dim]")
    else:
        note = generator.generate_xiaohongshu_note(topic, tone)
        console.print(f"[bold red]标题: {note['title']}[/bold red]")
        console.print(f"\n{note['content']}")


@ai.command()
@click.argument("content_text")
@click.option("--platform", "-p", default="twitter", type=click.Choice(["twitter", "xiaohongshu"]), help="目标平台")
def hashtags(content_text: str, platform: str):
    """生成 Hashtag"""
    from content_generator import ContentGenerator

    generator = ContentGenerator()
    tags = generator.generate_hashtags(content_text, platform)

    console.print(f"\n[bold green]推荐 Hashtag:[/bold green]")
    console.print(f"{tags}")


if __name__ == "__main__":
    cli()
