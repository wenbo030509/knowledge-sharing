---
name: wechat-article
description: 抓取并提取微信公众号（mp.weixin.qq.com）文章正文为 Markdown，按知识库规范落盘。当用户分享微信文章链接并要求总结/记录/精读时使用。注意 WebFetch 对微信域名会被安全策略拦截，必须走 curl + 提取脚本链路。
---

# 微信公众号文章处理

用户分享 `mp.weixin.qq.com` 链接时的标准链路。目标：拿到干净的正文 Markdown，按知识库规范落盘成「原文 + 笔记」。

## 为什么需要这条链路（先读）

```text
WebFetch(mp.weixin.qq.com)  → ❌ 被 claude.ai 域名安全策略拦截（"Unable to verify if
                              domain is safe to fetch"），不要尝试
html_to_md.py                → ❌ 只认 <article> 标签，微信文章没有，不要用
src/wechat_article.py        → ✅ 专为微信结构写的提取脚本（正文在 div#js_content，
                              图片 data-src 懒加载，域名 qpic.cn）
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

### 第 3 步：通读全文并人工检查

提取后必须完整读一遍（Read 脚本输出的 md），确认：
- 结构完整（章节标题、段落是否齐全）
- 表格内容是否在（微信编辑器表格有时以图片形式存在，此时图片链接就是内容本身）
- 尾部噪音是否已清理

### 第 4 步：落盘（遵循知识库文档体系）

```text
papers/NN-来源-主题/
├── 原文.md    ← 清理后的全文（忠实原文，不增删内容）
└── 笔记.md    ← 精读笔记（见下方格式）
```

- NN 是下一可用编号（01.anthropic-agent-evals → 02.meituan-agent-evals）
- 来源是机构名（如 meituan、openai、deepseek）
- 主题简洁（如 agent-evals、data-pipeline）
- 如果文章属于已有专题（如美团技术视频系列），也可以放 notebook/ 对应专题文件下，用判断力

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
4. 文章表格常以图片形式存在 → 表格列空是正常的，图片链接才是内容
5. 尾部"推荐阅读"/"点赞引导"/二维码是噪音 → 脚本自动清理，但输出后仍要目检
6. 微信图片链接带时效参数 → 笔记里不要依赖图片长期有效，关键内容要转述成文字
```
