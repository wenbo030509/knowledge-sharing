---
name: wechat-article
description: 抓取并提取微信公众号（mp.weixin.qq.com）文章正文与图片内容为 Markdown，按知识库规范落盘。当用户分享微信文章链接并要求总结/记录/精读时使用。注意 WebFetch 对微信域名会被安全策略拦截，必须走 curl + 提取脚本链路；图片由脚本保序下载后，当前会话的多模态 agent 直接看图判断与文章相关性（相关保留并转写、无关舍弃），脚本 OCR（src/img_ocr.py）仅作无视觉会话时的兜底。
---

# 微信公众号文章处理

用户分享 `mp.weixin.qq.com` 链接时的标准链路。目标：拿到干净的正文 Markdown（含图片里承载的内容），按知识库规范落盘成「原文 + 笔记」。

## 为什么需要这条链路（先读）

```text
WebFetch(mp.weixin.qq.com)  → ❌ 被 claude.ai 域名安全策略拦截（"Unable to verify if
                              domain is safe to fetch"），不要尝试
html_to_md.py                → ❌ 只认 <article> 标签，微信文章没有，不要用
src/wechat_article.py        → ✅ 专为微信结构写的正文提取脚本（正文在 div#js_content，
                              图片 data-src 懒加载，域名 qpic.cn）
src/wechat_images.py         → ✅ 文章图片保序下载到本地（识图交给当前会话的多模态 agent；
                              可选 --ocr 走共享模块 src/img_ocr.py 做脚本兜底，仅无视觉会话时用）
```

## 标准流程

> **跨平台命令约定**（本 skill 在不同设备/OS 上被调起，下方命令按你的环境适配，不要照抄）：
> - `python3` → Windows 上通常是 `python`；先确认哪个可用（`python --version`）。
> - 脚本网络层已用纯标准库（`src/net_util.py`），**无需 requests**；只有 `wechat_article.py` 的
>   HTML 解析依赖 `beautifulsoup4`，缺失时脚本会提示 `python -m pip install beautifulsoup4`。
> - `/tmp/xxx` → 非类 Unix 环境用系统临时目录（Windows PowerShell: `$env:TEMP`）。
> - `curl` → **Windows PowerShell 里 `curl` 是 `Invoke-WebRequest` 的别名，不认 `-sL`**，
>   必须用 `curl.exe`；**更省事的做法：直接 `python wechat_article.py <url>` 让脚本自己抓**
>   （net_util 跨平台，自动处理 UA/gzip/证书，无需手动 curl）。
> - 路径分隔与引号按当前 shell 语法处理；含中文/空格的路径加引号。

### 第 1 步：抓取 + 提取正文（推荐一步到位）

脚本网络层跨平台（net_util，自动处理浏览器 UA / gzip / 证书降级），**直接让脚本抓取即可**：

```bash
python3 src/wechat_article.py "<文章URL>" -o /tmp/wechat_article.md
```

脚本会自动：抓取 HTML → 提取标题（`h1#activity-name`）、正文（`div#js_content`）、转表格为 Markdown、保留图片链接（懒加载 `data-src`）、剔除噪音（"点亮星标"/"推荐阅读"/"END" 等）。

**备选（脚本抓取被风控/需要手动介入时）**：先手动抓 HTML 再喂给脚本处理本地文件——
`curl.exe -sL -A "<浏览器UA>" "<文章URL>" -o /tmp/wechat_article.html`，再
`python3 src/wechat_article.py -f /tmp/wechat_article.html -o /tmp/wechat_article.md`。
（⚠️ WebFetch 对 mp.weixin.qq.com 必被安全策略拦截，不要用；Windows 上 `curl` 是别名，用 `curl.exe`。）

**失败排查：**
- 报错"未能提取到标题"→ 页面是验证页/文章已删除/需要登录，告知用户，不要硬编
- 提取结果没有图片链接 → 文章图片可能是纯装饰 gif，正常

### 第 2 步：图片识别（主路径：agent 直接看图；脚本 OCR 仅兜底）★

**先判断是否要走**：md 里出现 qpic.cn 链接且可能是内容载体 → 走本步；只有装饰 gif/无图 → 跳过。

微信编辑器里**表格、幻灯片、长截图常以图片形式存在——图片里的字就是内容**，且 qpic 链接带时效参数。所以内容性图片必须：下载到本地 → 识别 → 转写进正文。

> **为什么主路径是"agent 看图"而不是"脚本 OCR"（跨设备/跨 agent 的关键）**：
> 本 skill 会被不同设备、不同 agent runtime 调起。脚本 OCR 的 model 引擎依赖宿主注入
> `ANTHROPIC_*` 环境变量、本地回退依赖 macOS `swiftc` / `tesseract`——这些在异构环境
> （不同厂商 key、非 Claude Code runtime、Windows/Linux）**都不保证存在**，一旦缺失就静默降级到空。
> 而"当前会话的 agent 本身就是多模态模型"这个能力，是**任何视觉 agent 都自带**的，零配置、跨平台。
> 所以：**下载靠脚本（确定性），识图靠 agent（普适性）**——这是本 skill 跨设备可用的设计根基。

**第一层（主）：下载图片 → agent 用 Read 逐张看图转写**

先用脚本把图片保序下载到本地（只下载、不 OCR）：

```bash
python3 src/wechat_images.py /tmp/wechat_article.md \
  --out /tmp/wechat_work --rewrite-out /tmp/wechat_article.local.md
```

产物（`/tmp/wechat_work/`）：
- `images/img_00.jpg ...` — 保序下载的图片（与文章出现顺序一致；qpic 防盗链已处理）
- `wechat_article.local.md` — 图片链接改写为 `images/img_XX.jpg` 本地路径的 md（下载失败的图保留原链接）

然后**你（当前会话的多模态模型）用 Read 逐张读 `images/img_XX.jpg`**，对每一张做两件事——这是主识别方式，不依赖任何外部 API/OCR 环境：
- **判断与文章的相关性**（视觉判断，别只看有没有字）：
  - **无关图 → 舍弃**：纯装饰背景/logo/二维码/表情包/风景/公众号引导图，无有效文字且与主题无关 → 不转写、不进 `images/`，交付时用一句话说明已舍弃（不静默丢失）。
  - **有效图 → 保留**：表格图、幻灯片截图、笔记截图、带文字说明的图、与主题相关的示意图 → 保留并转写。
- **对保留的图忠实转写**：表格图 → Markdown 表格（行列不错位）；流程图 → 用 `→` 还原步骤与箭头文字；界面截图 → 转写可见的字段/按钮/数值；看不清的字标 `[?]`，绝不为顺滑而编造知识点。

**第二层（兜底，仅在当前会话无视觉能力时用）：脚本 OCR**

只有当当前会话模型**不支持视觉**（Read 图片返回 Unsupported）时，才降级用脚本 OCR 兜底：

```bash
python3 src/wechat_images.py /tmp/wechat_article.md \
  --out /tmp/wechat_work --ocr --rewrite-out /tmp/wechat_article.local.md
```

- 多加 `--ocr` 会调用 `src/img_ocr.py`（model 引擎=视觉 API，需宿主提供 `ANTHROPIC_*`；失败自动回退 macOS Vision → tesseract）。产物多一个 `ocr_raw.txt`。
- ⚠️ OCR 环境不一定具备（见上方说明），且 OCR 文本很脏（断行/切词/丢表格结构）——**只是不丢字的兜底对照物，绝不直接当结果交付**。
- 用 OCR 兜底时：以识别文本为依据做清理还原，把必须看图确认的段落（手写、密集表格图）标注「⚠ 待视觉会话复核」，恢复视觉能力后再按第一层复核更正。

**转写进正文**：在 `/tmp/wechat_article.local.md` 上编辑——每个内容性图片位置，用转写文字替换图片链接（表格图 → Markdown 表格），并在下方保留一行 `![img_XX.jpg](images/img_XX.jpg)` 供核对；装饰图直接移除。

### 第 3 步：通读全文并人工检查

转写后必须完整读一遍，确认：
- 结构完整（章节标题、段落是否齐全）
- 图片转写内容与图一致（尤其表格图还原成表格后，行列没有错位）
- 尾部噪音是否已清理

### 第 4 步：落盘（遵循知识库文档体系）

```text
papers/NN-来源-主题/
├── 原文.md    ← 清理后的全文（忠实原文，不增删内容；图片转写文字并入对应位置）
├── 笔记.md    ← 精读笔记（见下方格式）
└── images/    ← 内容性图片的本地副本（从下载目录移过来；装饰图不带）
```

- NN 是下一可用编号（01.anthropic-agent-evals → 02.meituan-agent-evals）
- 来源是机构名（如 meituan、openai、deepseek）
- 主题简洁（如 agent-evals、data-pipeline）
- 如果文章属于已有专题（如美团技术视频系列），也可以放 notebook/ 对应专题文件下，用判断力
- 移动 `images/` 目录时保证与 原文.md 的相对位置不变，本地图片链接才能继续生效

**笔记.md 格式**（参考 `papers/01.anthropic-agent-evals/笔记.md` 和 `papers/02.meituan-agent-evals/笔记.md`）：

```text
# 精读笔记：<文章标题>

> 来源 / 阅读日期 / 重要性（⭐⭐⭐ 标准：是否对标 Agent PM 岗位核心能力）

## 一、文章在讲什么（30 秒版本）   ← 一段话

## 二、核心观点（带面试说法）       ← 每个观点配【面试说法】，
                                     技术术语保留英文，树形结构展示层级

## 三、与相关文章的对比（如有）     ← 和已有 papers/ 目录里的文章做重合/差异对比

## 四、面试故事模板                 ← 结合用户项目经验（CoT 质检/评测 Pipeline）

## 五、知识树连接                   ← 记录 knowledge-tree.md 里的节点连接

## 六、待深挖方向                   ← 勾选列表
```

### 第 5 步：同步文档体系（三个文件）

每次新增精读后必须同步，否则索引会过时：

1. `README.md` — papers/ 目录树加新目录
2. `CLAUDE.md` — 第七节文档体系加新目录
3. `notebook/0.knowledge-tree.md` — 相关节点加新连接（格式：`节点A ← → 节点B：连接说明`）

### 第 6 步：向用户汇报

```text
文章主题：<一句话>
核心观点：<2-3 条最有价值的>
落盘位置：<路径>
面试价值：<这篇文章里哪些点能直接进面试故事>
```

## 已知坑（踩过的记录）

```text
1. WebFetch 对 mp.weixin.qq.com 必然被拦 → 第一反应就是 curl，不要浪费一次调用
2. html_to_md.py 不适用（要 <article>）→ 用 src/wechat_article.py
3. 图片域名有 mmbiz.qpic.cn 和 mmecoa.qpic.cn 两个子域 → 过滤条件写 qpic.cn
4. 表格常以图片形式存在 → 图片里的表格就是内容，必须走第 3 步下载 + OCR +
   看图还原成 Markdown 表格；"表格列空"不是正常现象，是还没识图的信号
5. 尾部"推荐阅读"/"点赞引导"/二维码是噪音 → 脚本自动清理，但输出后仍要目检
6. 微信图片链接带时效参数 → 只留链接日后必失效；内容性图必须下载到本地
   images/ 并把转写文字并入 原文.md，不依赖远程链接
7. qpic.cn 防盗链 → 下载要带浏览器 UA + Referer mp.weixin.qq.com
   （wechat_images.py 已处理，失败自动降级无 Referer 重试一次）
8. 图片识别主路径 = agent 用 Read 逐张看图（任何视觉 agent 自带，跨设备零配置）；
   脚本 --ocr 只是无视觉会话时的兜底，且依赖宿主 ANTHROPIC_* / macOS 工具，不保证可用——
   OCR 输出断行/切词/丢表格结构是常态，绝不直接交付
```
