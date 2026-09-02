#!/usr/bin/env python3
"""
xhs_fetch.py — 抓取小红书帖子正文与图片, 并对图片做 OCR(文字)提取.

用法:
    python3 xhs_fetch.py <短链或完整链接> [--out DIR] [--ocr] [--ocr-engine vision|tesseract]

流程:
  1) 解析短链(xhslink.cn)得到真实帖子 URL
  2) 抓取页面 HTML, 提取 window.__INITIAL_STATE__ 内嵌数据
  3) 取 title / desc / imageList 图片
  4) (可选 --ocr) 逐张图片识别文字并输出
"""

import argparse
import json
import os
import re
import ssl
import sys
import urllib.request
from datetime import datetime

from img_ocr import ocr_images


UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def http_get(url, binary=False):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Referer": "https://www.xiaohongshu.com/",
    })
    with urllib.request.urlopen(req, context=CTX, timeout=40) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", "replace")


def resolve(url):
    """跟随跳转拿最终 URL."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, context=CTX, timeout=40) as r:
        return r.geturl()


def extract_state(html):
    m = re.search(r"window\.__INITIAL_STATE__\s*=\s*", html)
    if not m:
        raise SystemExit("没有找到 __INITIAL_STATE__ (可能需要登录/风控)")
    payload = re.sub(r'(?<![\w"\\])undefined(?![\w"])', "null", html[m.end():])
    obj, _ = json.JSONDecoder().raw_decode(payload)
    return obj


def grab_note(obj):
    ndm = (obj.get("note") or {}).get("noteDetailMap") or {}
    if not ndm:
        raise SystemExit("no noteDetailMap")
    note_id = next(iter(ndm))
    return note_id, ndm[note_id]["note"]


def download_images(note, outdir):
    os.makedirs(outdir, exist_ok=True)
    paths = []
    for i, im in enumerate(note.get("imageList") or []):
        url = im.get("urlDefault") or im.get("url")
        if not url:
            continue
        url = url.replace("http://", "https://")
        fp = os.path.join(outdir, f"img_{i:02d}.jpg")
        try:
            open(fp, "wb").write(http_get(url, binary=True))
            paths.append(fp)
        except Exception as e:  # noqa: BLE001
            print(f"[warn] 下载图片 {i} 失败: {e}", file=sys.stderr)
    return paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out", default="xhs_download")
    ap.add_argument("--ocr", action="store_true")
    # model=视觉模型 API（默认，结构还原最好，失败自动回退 vision→tesseract）
    ap.add_argument("--ocr-engine", choices=["model", "vision", "tesseract"], default="model")
    args = ap.parse_args()

    final = resolve(args.url)
    print("最终 URL:", final)
    html = http_get(final)
    obj = extract_state(html)
    note_id, note = grab_note(obj)

    paths = download_images(note, args.out)
    ocr_text = ""
    if args.ocr and paths:
        # OCR 编排在共享模块 img_ocr.py（vision 失败自动回退 tesseract）
        ocr_text = ocr_images(paths, engine=args.ocr_engine)

    # 把结果统一落盘，供多模态收尾层使用
    outdir = os.path.abspath(args.out)
    meta = {
        "noteId": note_id,
        "final_url": final,
        "title": note.get("title"),
        "type": note.get("type"),
        "desc": (note.get("desc") or "").strip(),
        "author": ((note.get("user") or {}).get("nickname") or ""),
        "tags": [t.get("name") for t in (note.get("tagList") or [])],
        "image_count": len(note.get("imageList") or []),
        "images": paths,
        "ocr_raw": ocr_text,
        "engine": args.ocr_engine if args.ocr else None,
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
    }
    with open(os.path.join(outdir, "note.json"), "w") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    if ocr_text:
        with open(os.path.join(outdir, "ocr_raw.txt"), "w") as f:
            f.write(ocr_text)

    print("\n=== 帖子 ===")
    print("noteId :", note_id)
    print("标题   :", note.get("title"))
    print("类型   :", note.get("type"))
    print("正文   :", (note.get("desc") or "").strip())
    print("图片数 :", len(note.get("imageList") or []))
    print("图片目录:", outdir)
    print("OCR原始文本:", os.path.join(outdir, "ocr_raw.txt") if ocr_text else "(未启用 --ocr)")


if __name__ == "__main__":
    main()
