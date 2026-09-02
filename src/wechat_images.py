#!/usr/bin/env python3
"""
wechat_images.py — 微信文章图片下载 + OCR（wechat-article 技能用）.

背景: wechat_article.py 提取正文时只保留 qpic.cn 图片链接, 不下载不识别.
微信表格/幻灯片常以图片形式存在(内容 = 图片里的字), 且 qpic 链接带时效参数——
因此需要: 提取链接 → 保序下载到本地 images/ → OCR 兜底 → 输出本地路径改写的 md.

用法:
  python3 wechat_images.py <文章.md> --out <工作目录> [--ocr] [--rewrite-out 改写.md]

流程:
  1) 从 md 按出现顺序提取 qpic.cn 图片 URL
  2) 逐个下载到 <out>/images/img_XX.jpg (保序, 需浏览器 UA + Referer)
  3) (可选 --ocr) 共享模块 img_ocr 逐张 OCR → <out>/ocr_raw.txt
  4) (可选 --rewrite-out) 输出图片链接改写为本地相对路径的 md
      (改写后 Claude 在此基础上编辑: 看图收尾、转写表格图内容)

输出目录结构:
  <out>/
  ├── images/img_00.jpg ...   ← 下载的图片（与文章出现顺序一致）
  └── ocr_raw.txt             ← OCR 原始文本（--ocr 时）

依赖: requests（与 wechat_article.py 相同）
"""

import argparse
import os
import re
import sys
from pathlib import Path

from img_ocr import ocr_images

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
# qpic.cn 防盗链: 带浏览器 UA + 微信 Referer 才能下到原图
HEADERS = {
    "User-Agent": UA,
    "Referer": "https://mp.weixin.qq.com/",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
}

IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def sniff_ext(data: bytes) -> str:
    """按内容嗅探图片真实格式（微信 qpic 图实际多为 PNG/GIF，不能一律写 .jpg）。"""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    if data[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return ".jpg"  # 兜底


def extract_image_urls(md: str) -> list[str]:
    """按出现顺序提取 md 里的 qpic.cn 图片链接（与 wechat_article.py 的 qpic 过滤一致）。"""
    urls = []
    for m in IMG_RE.finditer(md):
        url = m.group(1).strip()
        if "qpic.cn" in url:
            urls.append(url)
    return urls


def _existing(img_dir: Path) -> dict[int, Path]:
    """已有下载：{编号: 文件路径}（幂等复用，扩展名以真实格式为准）。"""
    found = {}
    for fp in img_dir.glob("img_*.???"):
        try:
            found[int(fp.stem.split("_")[1])] = fp
        except (ValueError, IndexError):
            continue
    return found


def download_images(urls: list[str], img_dir: Path) -> list[Path | None]:
    """保序下载；返回与 urls 等长的列表，失败项为 None（供改写时保留原链接）。"""
    import requests

    img_dir.mkdir(parents=True, exist_ok=True)
    existing = _existing(img_dir)
    paths: list[Path | None] = []
    for i, url in enumerate(urls):
        if i in existing:  # 幂等：已下载则复用
            paths.append(existing[i])
            continue
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            # qpic 防盗链偶尔要求无 Referer，失败时降级重试一次
            if resp.status_code != 200:
                resp = requests.get(url, headers={"User-Agent": UA}, timeout=30)
            resp.raise_for_status()
            fp = img_dir / f"img_{i:02d}{sniff_ext(resp.content)}"
            fp.write_bytes(resp.content)
            paths.append(fp)
        except Exception as e:  # noqa: BLE001
            print(f"[warn] 下载图片 {i} 失败: {e}", file=sys.stderr)
            paths.append(None)
    return paths


def rewrite_links(md: str, paths: list[Path | None]) -> str:
    """把 md 里的 qpic.cn 远程链接改写为 images/ 下的本地相对路径。

    paths 与 md 中 qpic 链接一一对应（同序），失败项(None)保留原链接不静默丢失。
    """
    counter = {"n": 0}

    def repl(m):
        url = m.group(1)
        if "qpic.cn" not in url:
            return m.group(0)
        fp = paths[counter["n"]] if counter["n"] < len(paths) else None
        counter["n"] += 1
        if fp is None:
            return m.group(0)
        return f"![{fp.name}](images/{fp.name})"

    return IMG_RE.sub(repl, md)


def main():
    ap = argparse.ArgumentParser(description="微信文章图片下载 + OCR")
    ap.add_argument("md_file", help="wechat_article.py 提取出的文章 md")
    ap.add_argument("--out", default="wechat_images", help="输出工作目录（images/ 与 ocr_raw.txt 放这里）")
    ap.add_argument("--ocr", action="store_true", help="下载后对图片做 OCR（共享模块 img_ocr）")
    # model=视觉模型 API（默认，结构还原最好，失败自动回退 vision→tesseract）
    ap.add_argument("--ocr-engine", choices=["model", "vision", "tesseract"], default="model")
    ap.add_argument("--rewrite-out", help="把链接改写为本地相对路径的 md 写到该文件")
    args = ap.parse_args()

    md = Path(args.md_file).read_text(encoding="utf-8")
    urls = extract_image_urls(md)
    if not urls:
        print("未找到 qpic.cn 图片链接（文章可能无图，或全部是装饰 gif）", file=sys.stderr)
        sys.exit(0)

    outdir = Path(args.out)
    img_dir = outdir / "images"
    print(f"发现 {len(urls)} 张图，下载到 {img_dir}", file=sys.stderr)
    paths = download_images(urls, img_dir)
    ok = [p for p in paths if p is not None]
    print(f"下载成功 {len(ok)}/{len(urls)}", file=sys.stderr)

    if args.ocr and ok:
        text = ocr_images([str(p) for p in ok], engine=args.ocr_engine)
        (outdir / "ocr_raw.txt").write_text(text, encoding="utf-8")
        print(f"OCR 完成: {outdir / 'ocr_raw.txt'}", file=sys.stderr)

    if args.rewrite_out:
        out = rewrite_links(md, paths)
        Path(args.rewrite_out).write_text(out, encoding="utf-8")
        print(f"改写后 md（图片链接 → images/ 本地路径）: {args.rewrite_out}", file=sys.stderr)


if __name__ == "__main__":
    main()
