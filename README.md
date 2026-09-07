# AI Learning System — 知识学习体系


> 既是知识库，也是一套**学习操作系统**——四视角思维框架 + Technical Anatomy 八层解剖 + 知识树持续生长。

---

## 这是什么？

一套以学习 模型训练、模型评测、Agent应用及相关技术为目标的系统化学习体系。

-  `CLAUDE.md` — Claude 行为规范：知识学习目标 + 四视角思维框架 + 执行流程
-  `.claude/skills/` — 可复用技能（wechat-article：公众号抓取；xiaohongshu-knowledge：小红书正文+图片 OCR 提取）
-  `notebook/` — 学习资料与指南
  - `0.knowledge-tree.md` — 知识树：AI Learning System 的完整骨架
  - `learning-manifesto.md` — 学习宣言：10 条核心原则
  - `python-learning-guide.md` — Python 学习指南（30 关键词 + 四层架构）
  - `pandas-csv-excel-guide.md` — 结构化数据处理指南（读取列/新增列/保存/批量）
  - `精读拆解方法论：事实-过程-方法三层法.md` — 学习拆解框架（每篇精读必用）
  - 专题文章：Agent（Harness/Workflow/Runtime/行业认知）、评测与数据策略（评测能力地图/算法反馈迭代/数据策略/Reward Model/LLM 数据集全景）、VLM（训练演进/课程规划/评测基准/判分规范）、搜索（系统全景/迁移地图）
-  `daily/` — 每日学习记录：工作汇报 + 技术解剖 + 讲述故事 + 知识树生长
-  `projects/` — 项目文档：每个项目独立记录，持续填充
-  `interview-prep/` — 面试准备：差距分析、简历、故事库、模拟面试（已 gitignore，不入库）
-  `papers/` — 论文与外部资料精读笔记（12 篇，评测方法论为主线）
-  `src/` — 工具脚本（文章抓取、HTML 转 MD、小红书 OCR、简历生成）

---

## 学习输出公式

```text
学习输出 = 项目经验（可讲的故事）× 技术理解（能讨论的深度）× Agent 认知（产品 Sense）
```

---

## 四视角思维框架

| 视角 | 关注什么 | 价值 |
|------|----------|------|
| PM 视角 | 流程设计、交付价值、用户需求 | 定义"什么是好" |
| 算法视角 | 量化指标、数学原理、模型行为 | 能和算法团队深度对话 |
| 工程视角 | 规模化、可靠性、系统设计 | 理解 Pipeline 不只是"写脚本" |
| 策略视角 | 实验设计、指标驱动、因果推断 | 用数据驱动决策 |


---

## 知识的八层标准

任何知识必须讲够八层才算真正理解：

> ① 它是什么？ → ② 为什么出现？ → ③ 数学原理 → ④ 工程实现 → ⑤ 为什么有效？ → ⑥ 为什么不用别的方法？ → ⑦ 工业界实践 → ⑧ 与 AI 系统的连接

---

## 目录结构

```text
knowledge-sharing/
├── README.md                          ← 项目门户
├── CLAUDE.md                          ← Claude 行为规范：知识学习目标 + 四视角思维框架 + 执行流程
│
├── daily/                             ← 每日记录
│   ├── template.md                    ← 模板
│   ├── 2026-07-10.md                  ← Day 0：学习系统的建立
│   ├── 2026-07-11.md                  ← CoT 质检项目深度解剖
│   └── 2026-07-11-study.md            ← 首个学习日：Information Bottleneck + Cascading Classification
│
├── notebook/                          ← 学习资料与指南
│   ├── 0.knowledge-tree.md            ← AI Learning System 知识树（持续生长）
│   ├── learning-manifesto.md          ← 学习宣言（10 条原则）
│   ├── python-learning-guide.md       ← Python 学习指南（30 关键词 + 四层架构）
│   ├── pandas-csv-excel-guide.md      ← 结构化数据处理指南（4 大核心操作）
│   ├── 精读拆解方法论：事实-过程-方法三层法.md ← 学习拆解框架
│   ├── LLM 数据集全景：预训练、后训练、评测集与 Benchmark.md ← 数据集全景
│   ├── Agent Harness 解剖.md          ← Agent Harness 八层解剖
│   ├── Workflow vs Agent：概念梳理与工程实践.md
│   ├── Claude Code、OpenClaw 与 Agent Runtime 的本质关系.md
│   ├── AI Agent 时代的几个核心认知与行业判断.md
│   ├── 美团技术视频专题：评测、训练数据与记忆三条学习路线.md
│   ├── 搜索系统全景：召回、排序、评测与数据闭环.md ← 搜索方向地图
│   ├── 搜索工程到Agent的迁移地图.md ← 工业项目 → Agent 构建/评测方法论
│   ├── VLM训练演进与数据难度升级.md ← VLM 演进史 + 数据难度定位
│   ├── VLM课程规划：多模态大模型的训练历程与发展.md ← VLM 课程大纲 + 自动化提效路线
│   ├── vlm任务2评分标准rubric整理分析.md ← VLM 判分规范解剖
│   ├── VLM 评测基准地图：MMMU、MME、Video-MME 与 MMBench.md ← VLM 评测基准
│   ├── Reward Model 八层解剖：偏好建模、Bradley-Terry 与 reward hacking.md
│   ├── AI策略产品与评测能力地图.md ← 评测四层模型 + 评测×数据交叉定位
│   ├── 算法反馈迭代：从评测结果到数据策略.md ← 评测→数据策略闭环
│   └── AI 数据策略：从 AiMe 到 B 端 Agent 平台.md ← 数据策略五问
│
├── projects/                          ← 按项目独立记录
│   ├── README.md                      ← 项目索引
│   ├── cot-compressed-evalset.md       ← CoT 质检项目（核心讲述故事）
│   ├── vlm-multivideo-capability-loop.md ← VLM 多视频理解能力提升（主线：数据闭环 + 靶向 SFT）
│   ├── vlm-sft-refactor.md             ← VLM 项目重构建议（能力提升重定位论证，保留）
│   ├── vlm-sft-addition.md             ← VLM 能力归因补充（指标→能力映射，已并入主文档，保留）
│   ├── baidu-agent-migration.md        ← 百度物料迁移 Agent
│   ├── fourth-paradigm-maas.md         ← 第四范式航空机务 MaaS
│   ├── fourth-paradigm-multi-agents.md ← 第四范式军事 Multi-Agents
│   ├── price-agent-project-readme.md   ← Price-Agent 商品对比助手
│   ├── price-agent-复盘文档.md         ← Price-Agent 讲述弹药库
│   ├── price-agent-eval-upgrade.md     ← Price-Agent 评测增强方案
│   └── kaggle-talkingdata.md           ← Kaggle 广告欺诈检测
│
├── interview-prep/                    ← 面试准备（已 gitignore，不入库；本地完整）
│   ├── gap-analysis.md                ← 岗位差距分析 + 弥补计划（执行手册）
│   ├── resume.md                      ← 简历当前版本（v2 已完成）
│   ├── story-bank.md                  ← 故事库（已完成）
│   ├── agent-insights.md              ← Agent 产品使用笔记（待创建）
│   └── mock-interviews.md             ← 模拟面试记录（待创建）
│
├── papers/                            ← 论文与外部资料精读
│   ├── 01.anthropic-agent-evals/      ← Anthropic Agent 评测方法论
│   │   ├── 原文.md                    ← 英文原文
│   │   ├── 译文.md                    ← 中文翻译
│   │   └── 笔记.md                    ← 精读笔记（10 观点 + 3 故事）
│   ├── 02.meituan-agent-evals/        ← 美团 Agent 评测（工业界落地视角）
│   │   ├── 原文.md                    ← 文章原文（中文）
│   │   └── 笔记.md                    ← 精读笔记（12 观点 + Anthropic 对比）
│   ├── 03.aihot-real-world-agent-evals/ ← 真实业务场景评测（行业数据）
│   │   ├── 原文.md                    ← 文章原文（中文）
│   │   └── 笔记.md                    ← 精读笔记（RealReplicaBench 数据 + 三文交叉验证）
│   ├── 04.swe-bench-anatomy/          ← SWE-bench 八层解剖（benchmark 事实标准）
│   │   └── 笔记.md                    ← 八层解剖（构建管线/判分机制/演进史/污染教训）
│   ├── 05.llm-judge-reliability/      ← LLM Judge 可靠性（偏差 + 一致性统计）
│   │   └── 笔记.md                    ← 三大偏差/缓解机制/Cohen's Kappa 校准流程
│   ├── 06.eval-to-training-loop/      ← 评测→训练闭环（数据飞轮闭合）
│   │   └── 笔记.md                    ← SWE-smith 合成数据管线 + 行业闭环模式
│   ├── 07.meituan-search-llm-repr/    ← 美团搜索 LLM 语义表征（与 price-agent 对标）
│       ├── 原文.md                    ← 文章原文（中文）
│       ├── 笔记.md                    ← 三期实践 + price-agent 对比 + 面试故事
│       └── 解剖-InfoNCE与Triplet对比学习.md ← 对比学习双损失八层解剖
│   ├── 08.xiaohongshu-algorithm-role-definition/ ← 算法岗位的定义与理解（小红书）
│   │   ├── 原文.md                    ← 正文 + 11 张图片内容
│   │   ├── 笔记.md                    ← 岗位认知 + 面试故事
│   │   └── images/                    ← 11 张原图
│   ├── 09.xiaohongshu-llm-engineer-notes/ ← LLM 算法工程师手记（小红书）
│       ├── 原文.md                    ← 正文（6 条手记）
│       └── 笔记.md                    ← bench/agentic data/reward hacking
│   ├── 10.brench-cold-start-agent-eval/ ← 无线上数据构建 Agent 冷启动评测集（Brench）
│   │   ├── 原文.md                    ← 13 节构建方法
│   │   ├── 笔记.md                    ← 冷启动评测集 + 面试故事
│   │   └── images/                    ← 18 张原图
│   ├── 11.xiaohongshu-from-zero-eval/ ← 从零做评测两份推荐材料（Anthropic + Harbor）
│   │   ├── 原文.md                    ← 两篇材料完整梳理
│   │   ├── 笔记.md                    ← 评测五件套 + 任务落地
│   │   └── images/                    ← 14 张原图
│   └── 12.warren-optima-benchmark/  ← AA 发布 Optima：把业务场景做成 Benchmark（Warren）
│       ├── 原文.md                    ← 正文 + 8 张卡片
│       ├── 笔记.md                    ← 双层评测 + 选型三维 + 评测资产化
│       └── images/                    ← 8 张原图
│   └── 13.aliyun-agentloop-data-flywheel/  ← AgentLoop 数据飞轮实践（共 5 篇 · 已完结）
│       ├── 原文.md                    ← 五篇合并（含 49 张图片转写，图片按篇分目录）
│       ├── 笔记.md                    ← 飞轮七环节 + 评估两层结构 + Rubric + 经验注入五参数
│       └── images/                    ← part1-part5 内容图（装饰图已剔除）
│   └── 14.xiaohongshu-passk-data-selection/  ← 为什么 1T 模型 Agentic RL 不能用 pass@k 筛数据（小red同学）
│       ├── 原文.md                    ← 正文 + 2 张核心信息图转写（pass@k 五缺陷 / 弱点驱动替代方案）
│       ├── 笔记.md                    ← pass@k 五缺陷 + benchmark 缺口驱动定向构造
│       └── images/                    ← 7 张内容图
│
└── src/                               ← 工具脚本
    ├── net_util.py                    ← 跨平台 HTTP 层（纯标准库，无需 requests；wechat/xhs 共用）
    ├── html_to_md.py                  ← HTML 转 Markdown 工具（通用，需 <article>）
    ├── wechat_article.py              ← 微信文章正文提取（net_util 抓取 + js_content 解析）
    ├── wechat_images.py               ← 微信文章图片保序下载（识图交给 agent；--ocr 兜底）
    ├── xhs_fetch.py                   ← 小红书链接抓取 + 图片保序下载（xiaohongshu-knowledge 技能用）
    ├── img_ocr.py                     ← 共享图片识别模块（无视觉会话兜底：视觉模型 API → Vision → tesseract）
    ├── img_ocr.swift                  ← 图片 OCR 引擎（macOS Vision，本地确定性兜底）
    └── build_resume_docx.py           ← 从 resume.md 生成 docx 简历（脚本内路径为旧 macOS 环境）
```

---

> 连接数 > 知识量。深度 > 广度。可讲的故事 > 读过的论文。
