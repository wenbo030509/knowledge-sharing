#!/usr/bin/env python3
"""
将 HTML 正文提取并转换为 Markdown 文档。

用法:
  python3 html_to_md.py                     # 交互式粘贴 HTML 路径
  python3 html_to_md.py input.html           # 命令行直接指定文件
  cat input.html | python3 html_to_md.py -   # 从标准输入读取, 输出到当前目录

输出: 与输入 HTML 同目录同名的 .md 文件

依赖: pip install beautifulsoup4 markdownify
"""

import sys
import re
from pathlib import Path


def convert_html_to_markdown(html_str: str) -> str:
    """使用 BeautifulSoup + markdownify 将 HTML 转为 Markdown。"""
    from bs4 import BeautifulSoup
    from markdownify import markdownify as md

    soup = BeautifulSoup(html_str, "html.parser")

    article = soup.find("article")
    if article is None:
        print("错误: 未找到 <article> 标签", file=sys.stderr)
        sys.exit(1)

    markdown = md(
        str(article),
        heading_style="ATX",
        strip=["img"],
        default_title=True,
    )

    return markdown


def post_process(md_text: str) -> str:
    """后处理: 清理多余空行、修复常见格式问题。"""
    md_text = re.sub(r"\n{4,}", "\n\n\n", md_text)
    md_text = re.sub(r"[ \t]+$", "", md_text, flags=re.MULTILINE)
    md_text = md_text.rstrip() + "\n"
    return md_text


def process_html_file(input_path: Path):
    """读取 HTML 文件, 转换并保存为同目录下的 .md 文件。"""
    if not input_path.exists():
        print(f"错误: 文件不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    html_content = input_path.read_text(encoding="utf-8")

    if not html_content.strip():
        print("错误: 输入内容为空", file=sys.stderr)
        sys.exit(1)

    markdown_content = convert_html_to_markdown(html_content)
    markdown_content = post_process(markdown_content)

    output_path = input_path.with_suffix(".md")
    output_path.write_text(markdown_content, encoding="utf-8")
    print(f"转换完成, 输出文件: {output_path}")


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "-":
            # 从标准输入读取, 输出保存到当前目录
            html_content = sys.stdin.read()
            if not html_content.strip():
                print("错误: 输入内容为空", file=sys.stderr)
                sys.exit(1)
            markdown_content = convert_html_to_markdown(html_content)
            markdown_content = post_process(markdown_content)
            output_path = Path.cwd() / "output.md"
            output_path.write_text(markdown_content, encoding="utf-8")
            print(f"转换完成, 输出文件: {output_path}")
        else:
            process_html_file(Path(arg))
    else:
        # 交互模式: 提示用户粘贴 HTML 文件路径
        html_path = input("请输入 HTML 文件路径: ").strip()
        if not html_path:
            print("错误: 未输入路径", file=sys.stderr)
            sys.exit(1)
        process_html_file(Path(html_path))


if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        print(f"缺少依赖: {e}", file=sys.stderr)
        print("请运行: pip3 install beautifulsoup4 markdownify", file=sys.stderr)
        sys.exit(1)
