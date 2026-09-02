---
name: wechat-article
description: 抓取并提取微信公众号（mp.weixin.qq.com）文章正文与图片内容为 Markdown，按知识库规范落盘。当用户分享微信文章链接并要求总结/记录/精读时使用。注意 WebFetch 对微信域名会被安全策略拦截，必须走 curl + 提取脚本链路；图片内容复用 src/img_ocr.py 共享 OCR 模块。
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
src/wechat_images.py         → ✅ 文章图片下载 + OCR（表格/幻灯片图里的内容必须走这步，
                              复用 xiaohongshu-knowledge 的共享 OCR 模块 src/img_ocr.py）
```

## 标准流程

### 第 1 步：抓取 HTML

```bash
curl -sL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" "<文章URL>" -o /tmp/wechat_article.html
```

必须带浏览器 UA，否则微信可能返回验证页。输出到 `/tmp/` 即可（临时文件）。

### 第 2 步：提取正文

```bash
python3 src/wechat_article.py -f /tmp/wechat_article.html -o /tmp/wechat_article.md
```

脚本会自动：提取标题（`h1#activity-name`）、正文（`div#js_content`）、转表格为 Markdown、保留图片链接（懒加载 `data-src`）、剔除噪音（"点亮星标"/"推荐阅读"/"END" 等）。

**失败排查：**
- 报错"未能提取到标题"→ 页面是验证页/文章已删除/需要登录，告知用户，不要硬编
- 提取结果没有图片链接 → 文章图片可能是纯装饰 gif，正常

### 第 3 步：图片识别（复用 xiaohongshu-knowledge 的两层识图能力）★

**先判断是否要走**：md 里出现 qpic.cn 链接且可能是内容载体 → 走本步；只有装饰 gif/无图 → 跳过。

微信编辑器里**表格、幻灯片、长截图常以图片形式存在——图片里的字就是内容**，且 qpic 链接带时效参数。所以内容性图片必须：下载到本地 → 识别（模型优先，本地兜底）→ 看图转写。和 xiaohongshu-knowledge 同一套两层模式。

**第一层：确定性兜底（脚本，可复现）**

```bash
python3 src/wechat_images.py /tmp/wechat_article.md \
  --out /tmp/wechat_work --ocr --rewrite-out /tmp/wechat_article.local.md
```

产物（`/tmp/wechat_work/`）：
- `images/img_00.jpg ...` — 保序下载的图片（与文章出现顺序一致）
- `ocr_raw.txt` — 逐张识别原始文本（默认 model 引擎 = 视觉模型 API 转写，结构还原最好；失败自动回退 macOS Vision → tesseract，保证不丢字）
- `wechat_article.local.md` — 图片链接改写为 `images/img_XX.jpg` 本地路径的 md（下载失败的图保留原链接）

**第二层：看图收尾（你，多模态模型，只有你来做才可靠）**

OCR 原始文本很脏（断行、切词、丢表格/箭头结构），**绝不能直接当结果交付**——它只是不丢字的兜底对照物：

**看图前提**：本层需要当前会话模型支持视觉，当前会话模型已验证支持视觉（Read 图片正常）。若未来切换模型后 Read 图片返回 Unsupported，**降级执行**：以识别文本为唯一依据做清理与还原；把疑似识别退化、必须看图确认的段落（如手写、密集表格图）标注「⚠ 待视觉会话复核」，绝不编造内容。恢复视觉能力后按下方 1-4 复核。

1. **清理噪点**：合并被切断的行、修被切开的词、纠正明显错字、去坐标噪声。
2. **还原结构**：表格图还原成 Markdown 表格；跨行段落拼回整段；恢复 `→` 流程步骤；保留列表层级。
3. **OCR 退化处直接看图**：排版密集、手写、艺术字体、表格/流程图，OCR 明显不可靠时用 Read 读 `images/img_XX.jpg`，以你的视觉为准更正。
4. **交叉核对**：OCR 与你看图不一致时，结构类问题以视觉为准，纯字符串以 OCR 里明显正确的那份为准。

**判断"图片是否有意义"**（视觉判断，别只看 OCR 是否出字）：
- **无关图**：纯装饰背景/logo/二维码/表情包/风景，无有效文字 → 丢弃，不要转写。
- **有效图**：表格图、幻灯片截图、笔记截图、带文字说明的图 → 保留并转写。

**转写进正文**：在 `/tmp/wechat_article.local.md` 上编辑——每个内容性图片位置，用转写文字替换图片链接（表格图 → Markdown 表格），并在下方保留一行 `![img_XX.jpg](images/img_XX.jpg)` 供核对；装饰图直接移除。忠实图里内容，不要为了让文字顺滑而改写知识点。

### 第 4 步：通读全文并人工检查

转写后必须完整读一遍，确认：
- 结构完整（章节标题、段落是否齐全）
- 图片转写内容与图一致（尤其表格图还原成表格后，行列没有错位）
- 尾部噪音是否已清理

### 第 5 步：落盘（遵循知识库文档体系）

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

### 第 6 步：同步文档体系（三个文件）

每次新增精读后必须同步，否则索引会过时：

1. `README.md` — papers/ 目录树加新目录
2. `CLAUDE.md` — 第七节文档体系加新目录
3. `notebook/0.knowledge-tree.md` — 相关节点加新连接（格式：`节点A ← → 节点B：连接说明`）

### 第 7 步：向用户汇报

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
8. OCR 输出绝不直接交付 → 断行/切词/丢表格结构是常态，必须由你（模型）
   看图收尾：清理、还原、交叉核对，OCR 只是兜底对照物
```
