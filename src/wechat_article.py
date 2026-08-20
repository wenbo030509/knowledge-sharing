#!/usr/bin/env python3
"""
微信公众号（mp.weixin.qq.com）文章正文提取工具。

背景：微信文章 HTML 结构与普通博客不同（无 <article> 标签，正文在
<div id="js_content"> 内，大量嵌套 <section>/<p>/<br>，图片为 data-src 懒加载），
因此 html_to_md.py 不适用，需要专门的提取逻辑。

用法:
  python3 wechat_article.py <url>                  # 直接抓取 URL 并提取
  python3 wechat_article.py -f input.html          # 处理本地已抓取的 HTML
  python3 wechat_article.py <url> -o output.md     # 指定输出文件（默认 文章标题.md）
  python3 wechat_article.py <url> --stdout         # 输出到标准输出

依赖: requests, beautifulsoup4
"""

import argparse
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Tag

# 公众号页面底部/顶部噪音：以这些内容开头或包含的块会被剔除
NOISE_PATTERNS = [
    r"点亮.*星标",          # 顶部引导关注
    r"推荐阅读",            # 底部推荐文章
    r"点赞.*在看.*分享",    # 点赞引导
    r"长按识别二维码",      # 二维码引导
    r"----------\s*END\s*----------",  # 分隔线
    r"^❤️",                # 爱心表情引导
]


def fetch_html(url: str) -> str:
    """抓取微信文章 HTML。微信对无 UA 的请求可能返回验证页，需要浏览器 UA。"""
    import requests

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    return resp.text


def extract(html_str: str) -> tuple[str, str]:
    """提取 (标题, 正文 Markdown)。返回空标题说明可能拿到了验证页/文章不存在。"""
    soup = BeautifulSoup(html_str, "html.parser")

    # 标题：<h1 class="rich_media_title">，文章被删/需验证时拿不到
    title_el = soup.find("h1", id="activity-name") or soup.find("h1", class_="rich_media_title")
    title = title_el.get_text(strip=True) if title_el else ""

    # 正文
    content = soup.find("div", id="js_content")
    if content is None:
        return title, ""

    md = render_content(content)
    md = clean_noise(md)
    return title, md.strip()


def render_content(content: Tag) -> str:
    """把 js_content 里的块级结构转成 Markdown，保留段落、表格、图片。"""
    lines: list[str] = []

    def flush():
        # 去掉连续空行
        while lines and lines[-1].strip() == "":
            lines.pop()
        if lines and lines[-1].strip() != "":
            lines.append("")

    def render_table(table: Tag) -> str:
        rows = []
        for tr in table.find_all("tr"):
            cells = [" ".join(td.get_text(" ", strip=True).split()) for td in tr.find_all(["td", "th"])]
            if cells:
                rows.append(cells)
        if not rows:
            return ""
        out = []
        for i, row in enumerate(rows):
            out.append("| " + " | ".join(c or " " for c in row) + " |")
            if i == 0:
                out.append("| " + " | ".join("---" for _ in row) + " |")
        return "\n".join(out)

    def render_image(img: Tag) -> str:
        # 微信图片懒加载：真实地址在 data-src（域名有 mmbiz/mmecoa 等 qpic.cn 子域）
        src = img.get("data-src") or img.get("src") or ""
        if not src or "qpic.cn" not in src:
            return ""
        alt = img.get("alt") or ""
        return f"![{alt}]({src})"

    def walk(node):
        # 块级元素 → 段落；行内 → 文本拼接；表格/图片单独处理
        if isinstance(node, Tag):
            name = node.name
            if name == "table":
                t = render_table(node)
                if t:
                    flush()
                    lines.append(t)
                    flush()
                return
            if name == "img":
                img = render_image(node)
                if img:
                    lines.append(img)
                return
            if name in ("p", "section", "div", "li", "h1", "h2", "h3", "h4", "ul", "ol", "blockquote"):
                inner = []
                for child in node.children:
                    if isinstance(child, Tag) and child.name == "table":
                        # 段落里的表格：先 flush 段内文字再渲染表格
                        text = " ".join("".join(inner).split())
                        if text:
                            lines.append(text)
                        render_table_inline(child)
                        inner = []
                    elif isinstance(child, Tag) and child.name == "img":
                        img = render_image(child)
                        if img:
                            inner.append(img)
                    else:
                        inner.append(get_text_recursive(child))
                text = " ".join("".join(inner).split())
                if text:
                    flush()
                    lines.append(text)
                    flush()
                return
            if name == "br":
                return
            # 其他标签递归
            for child in node.children:
                walk(child)
        else:  # NavigableString
            pass

    def render_table_inline(table: Tag):
        flush()
        t = render_table(table)
        if t:
            lines.append(t)
            flush()

    def get_text_recursive(node):
        if isinstance(node, Tag):
            if node.name == "img":
                return render_image(node)
            return "".join(get_text_recursive(c) for c in node.children)
        return str(node)

    for child in content.children:
        walk(child)

    # 结尾清理
    while lines and lines[-1].strip() == "":
        lines.pop()
    return "\n".join(lines)


def clean_noise(md: str) -> str:
    """剔除公众号固定的引导/推荐噪音块。"""
    blocks = re.split(r"\n\s*\n", md)
    kept = []
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        if any(re.search(p, b) for p in NOISE_PATTERNS):
            continue
        kept.append(b)
    return "\n\n".join(kept)


def main():
    parser = argparse.ArgumentParser(description="微信公众号文章正文提取")
    parser.add_argument("url_or_file", help="微信文章 URL，或 -f 指定本地 HTML 文件")
    parser.add_argument("-f", "--file", action="store_true", help="输入是本地 HTML 文件")
    parser.add_argument("-o", "--output", help="输出 markdown 路径（默认: ./<标题>.md）")
    parser.add_argument("--stdout", action="store_true", help="输出到标准输出")
    args = parser.parse_args()

    if args.file:
        html_str = Path(args.url_or_file).read_text(encoding="utf-8")
    else:
        print(f"抓取中: {args.url_or_file}", file=sys.stderr)
        html_str = fetch_html(args.url_or_file)

    title, md = extract(html_str)
    if not title:
        print("错误: 未能提取到标题——页面可能是验证页/文章已删除/需要登录", file=sys.stderr)
        sys.exit(1)
    if not md:
        print("错误: 未能提取到正文 (js_content 为空)", file=sys.stderr)
        sys.exit(1)

    print(f"标题: {title}", file=sys.stderr)
    if args.stdout:
        print(f"# {title}\n\n{md}")
        return

    out = Path(args.output) if args.output else Path(f"{title}.md")
    out.write_text(f"# {title}\n\n{md}\n", encoding="utf-8")
    print(f"已保存: {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
