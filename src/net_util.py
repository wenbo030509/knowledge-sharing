#!/usr/bin/env python3
"""
net_util.py — 抓取类脚本共享的跨平台 HTTP 层（wechat_article / wechat_images / xhs_fetch 共用）.

为什么要有它（skill 可用性 / 跨设备通用性）：
  这些脚本是 skill 的第一道关口——每次调用都要跑，跑不起来整个 skill 就废。
  原实现各自依赖第三方 `requests` 且 SSL/编码/gzip 处理不一致，在没装 requests 的新设备、
  或中文 Windows（默认 GBK 编码）上会直接崩。本模块用**纯标准库 urllib** 统一收口，做到：
    - 零第三方依赖（requests 不再是必需；certifi 有则用、没有也能跑）
    - 证书校验用 certifi（修 macOS 系统 CA 不全导致的校验失败），失败自动降级重试
    - 自动 gzip 解压、跟随重定向、防盗链 Referer 回退
    - 全部文本 I/O 显式 UTF-8（不受平台 locale 影响）

环境开关：
  FETCH_NO_SSL_VERIFY=1  → 强制关闭 TLS 校验（企业代理/自签证书环境）；默认安全优先。
"""

import gzip
import os
import ssl
import sys
import urllib.error
import urllib.request

# 统一浏览器 UA：微信/小红书对无 UA 或非浏览器 UA 的请求可能返回验证页/风控页
DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def build_ssl_context(no_verify: bool | None = None) -> ssl.SSLContext:
    """TLS 上下文。默认用 certifi 的 Mozilla CA（macOS framework 版 Python 系统 CA
    加载不全，会导致部分站点校验失败；certifi 纯净 bundle 可通过）。
    no_verify=True 或环境变量 FETCH_NO_SSL_VERIFY=1 时关闭校验（自签/代理环境）。"""
    if no_verify is None:
        no_verify = os.environ.get("FETCH_NO_SSL_VERIFY") == "1"
    if no_verify:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _read(resp) -> bytes:
    """读取响应体，按 Content-Encoding 自动 gzip 解压（urllib 不会自动处理）。"""
    data = resp.read()
    enc = (resp.headers.get("Content-Encoding") or "").lower()
    if "gzip" in enc:
        try:
            return gzip.decompress(data)
        except OSError:
            return data
    return data


def open_url(url: str, headers: dict | None = None, timeout: int = 40,
             referer: str | None = None) -> tuple[bytes, str]:
    """GET 请求，返回 (响应体 bytes, 最终 URL)。跟随重定向；TLS 校验失败自动降级重试一次。"""
    h = {"User-Agent": DEFAULT_UA}
    if referer:
        h["Referer"] = referer
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, context=build_ssl_context(), timeout=timeout) as r:
            return _read(r), r.geturl()
    except ssl.SSLCertVerificationError:
        print(f"[warn] TLS 证书校验失败，降级不校验重试: {url}", file=sys.stderr)
        with urllib.request.urlopen(req, context=build_ssl_context(no_verify=True), timeout=timeout) as r:
            return _read(r), r.geturl()


def get_text(url: str, headers: dict | None = None, timeout: int = 40,
             referer: str | None = None) -> str:
    """抓取文本（HTML）。始终按 UTF-8 解码（replace 兜底，不因个别坏字节整体失败）。"""
    data, _ = open_url(url, headers=headers, timeout=timeout, referer=referer)
    return data.decode("utf-8", "replace")


def resolve(url: str, timeout: int = 40) -> str:
    """跟随跳转拿最终 URL（短链解析，如 xhslink.cn）。校验失败也降级重试。"""
    _, final = open_url(url, timeout=timeout)
    return final


def fetch_image(url: str, referer: str | None = None, timeout: int = 40) -> bytes:
    """下载图片 bytes。带浏览器 UA + 可选 Referer 过防盗链；被拒(HTTPError)时降级去掉 Referer 重试一次。"""
    accept = "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"
    try:
        data, _ = open_url(url, headers={"Accept": accept}, referer=referer, timeout=timeout)
        return data
    except urllib.error.HTTPError:
        # 部分 CDN 防盗链在带 Referer 时反而拒绝 → 无 Referer 重试
        data, _ = open_url(url, headers={"Accept": accept}, timeout=timeout)
        return data
