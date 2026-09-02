#!/usr/bin/env python3
"""
img_ocr.py — 共享图片识别模块（xiaohongshu-knowledge / wechat-article 两个技能共用）.

职责: 给定一批本地图片路径, 返回逐张的识别文本.
引擎链（按 `engine` 参数选择, 自动回退）:
  "model"     → 多模态模型 API（视觉转写, 保留结构）→ 回退 vision → 回退 tesseract
  "vision"    → macOS Vision（本地, 质量好, 带坐标） → 回退 tesseract
  "tesseract" → tesseract chi_sim+eng

model 引擎从环境变量读配置（与 Claude Code 同源）:
  ANTHROPIC_BASE_URL（默认 https://api.anthropic.com）
  ANTHROPIC_AUTH_TOKEN 或 ANTHROPIC_API_KEY
  ANTHROPIC_MODEL（默认 claude-sonnet-4-5）

与平台无关: 只接收"已下载到本地的图片路径", 不负责抓取/下载——
小红书用 xhs_fetch.py 下载, 微信文章用 wechat_images.py 下载, 都调用本模块.
"""

import os
import subprocess

TOOL_NAME = "img_ocr"  # 编译产物名（swift 源码 img_ocr.swift，被 .gitignore 忽略）

# ---- 模型引擎（视觉 API, 默认为主引擎） ----

PROMPT = (
    "逐字转写图片里的全部文字。规则：只输出文字内容，不要解释、不要总结、不要翻译、"
    "不要加标题或额外说明；保留原有换行与段落；表格/流程图等结构化内容用 Markdown 或 "
    "→ 箭头还原；看不清的字用 [?] 标注，绝不猜测补全。"
)


def _api_config() -> tuple[str, str, dict[str, str]] | None:
    """从环境变量读取视觉 API 配置: (url, model, headers)。无配置返回 None。

    与 Claude Code 同源：ANTHROPIC_BASE_URL / ANTHROPIC_AUTH_TOKEN(或 API_KEY) / ANTHROPIC_MODEL。
    """
    base = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/")
    token = os.environ.get("ANTHROPIC_AUTH_TOKEN") or os.environ.get("ANTHROPIC_API_KEY")
    if not token:
        return None
    # Claude Code 约定：AUTH_TOKEN 走 Bearer，API_KEY 走 x-api-key
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        **({"Authorization": f"Bearer {token}"}
           if os.environ.get("ANTHROPIC_AUTH_TOKEN") else {"x-api-key": token}),
    }
    model = os.environ.get("ANTHROPIC_MODEL") or "claude-sonnet-4-5"
    return base + "/v1/messages", model, headers


def _media_type(path: str) -> str:
    """按扩展名粗判图片媒体类型（qpic 实际多为 png/gif，不能一律 jpeg）。"""
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    return {"png": "image/png", "gif": "image/gif", "webp": "image/webp"}.get(ext, "image/jpeg")


def _ssl_context() -> "ssl.SSLContext":
    """证书校验上下文。优先 certifi 的 Mozilla CA：macOS 的 Python 系统默认 CA
    加载不全（framework 版），会导致 api.deepseek.com 等端点校验失败；
    而 certifi 纯净 CA bundule 校验通过。仅当显式设置 IMG_OCR_NO_SSL_VERIFY=1
    （企业代理/自签证书环境）才关闭校验——默认为安全优先，不做静默降级。
    """
    import ssl

    if os.environ.get("IMG_OCR_NO_SSL_VERIFY") == "1":
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _transcribe_one(path: str, url: str, model: str, headers: dict[str, str]) -> str | None:
    """对单张图调用视觉 API 转写。失败返回 None。"""
    import base64
    import json
    import urllib.request

    b64 = base64.b64encode(open(path, "rb").read()).decode()
    payload = {
        "model": model,
        "max_tokens": 4000,
        # 转写是确定性任务，禁用思考：默认思考会吞掉整个 max_tokens 预算——
        # 大图 + 长 PROMPT 时实测出现"只有 thinking 块、无 text 块"的静默失败，
        # 且 disabled 输出 token 数与耗时都大幅降低
        "thinking": {"type": "disabled"},
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image",
                 "source": {"type": "base64", "media_type": _media_type(path), "data": b64}},
                {"type": "text", "text": PROMPT},
            ],
        }],
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(req, context=_ssl_context(), timeout=90) as r:
        data = json.loads(r.read().decode())
    if data.get("error"):
        raise RuntimeError(f"API error: {data['error']}")
    for block in data.get("content", []):
        if block.get("type") == "text":
            return block["text"]
    import sys
    print(f"[warn] 响应无 text 块: {json.dumps(data, ensure_ascii=False)[:200]}", file=sys.stderr)
    return None


def model_ocr(paths: list[str]) -> str | None:
    """视觉 API 转写（逐张，保留结构，无坐标噪声）。无配置或全部失败返回 None（供回退）。

    单张失败时保留占位标记（layer-2 看图时优先复核该张），不静默丢失。
    """
    cfg = _api_config()
    if cfg is None:
        print("[warn] 未配置 ANTHROPIC_* 环境变量，跳过模型引擎", file=__import__("sys").stderr)
        return None
    url, model, headers = cfg
    chunks = []
    for p in paths:
        try:
            text = _transcribe_one(p, url, model, headers)
        except Exception as e:  # noqa: BLE001
            text = None
            print(f"[warn] 模型识别失败 {p}: {e}", file=__import__("sys").stderr)  # noqa: SIM117
        if text is None:
            return None  # 单张失败 → 整批回退本地引擎（确定性优先）
        chunks.append(f"=== {p} ===\n{text.strip()}")
    return "\n\n".join(chunks)


# ---- 本地确定性引擎（macOS Vision → tesseract） ----

def _tool_path() -> str:
    return os.path.join(os.path.dirname(__file__), TOOL_NAME)


def ensure_tool() -> str | None:
    """确保 OCR 二进制已编译。首次运行自动 swiftc 编译 img_ocr.swift。"""
    tool = _tool_path()
    if not os.path.exists(tool):
        src = os.path.join(os.path.dirname(__file__), TOOL_NAME + ".swift")
        subprocess.run(["swiftc", "-O", src, "-o", tool], check=False)
    return tool if os.path.exists(tool) else None


def vision_ocr(paths: list[str]) -> str | None:
    """macOS Vision OCR（逐张，带坐标，按阅读顺序排序）。无工具/失败返回 None。"""
    tool = ensure_tool()
    if tool is None:
        return None
    out = subprocess.run([tool] + paths, capture_output=True, text=True).stdout
    return out


def tesseract_ocr(paths: list[str]) -> str:
    """回退引擎：tesseract chi_sim+eng。"""
    chunks = []
    for p in paths:
        r = subprocess.run(
            ["tesseract", p, "stdout", "-l", "chi_sim+eng", "--psm", "6"],
            capture_output=True, text=True)
        chunks.append(f"=== {os.path.basename(p)} ===\n{r.stdout.strip()}")
    return "\n\n".join(chunks)


def ocr_images(paths: list[str], engine: str = "model") -> str:
    """对一批图片做识别，返回统一文本。

    引擎链: model → vision → tesseract（逐级自动回退，保证不丢字）。
    返回的文本为 layer-2 逐字复核的对照物，绝不直接交付。
    """
    if engine == "model":
        text = model_ocr(paths)
        if text is not None:
            return text
        print("[info] 模型引擎不可用，回退 macOS Vision", file=__import__("sys").stderr)
    if engine in ("model", "vision"):
        text = vision_ocr(paths)
        if text is not None:
            return text
    return tesseract_ocr(paths)
