# AI Learning System — 知识学习体系


> 既是知识库，也是一套**学习操作系统**——四视角思维框架 + Technical Anatomy 八层解剖 + 知识树持续生长。

---

## 这是什么？

一套以学习 模型训练、模型评测、Agent应用及相关技术为目标的系统化学习体系。

-  `CLAUDE.md` — Claude 行为规范：知识学习目标 + 四视角思维框架 + 执行流程
-  `notebook/` — 学习资料与指南
  - `0.knowledge-tree.md` — 知识树：AI Learning System 的完整骨架
  - `learning-manifesto.md` — 学习宣言：10 条核心原则
  - `python-learning-guide.md` — Python 学习指南（30 关键词 + 四层架构）
  - `pandas-csv-excel-guide.md` — 结构化数据处理指南（读取列/新增列/保存/批量）
  - `精读拆解方法论：事实-过程-方法三层法.md` — 学习拆解框架（每篇精读必用）
  - 专题文章：Workflow vs Agent、Agent Runtime、行业认知
-  `daily/` — 每日学习记录：工作汇报 + 技术解剖 + 讲述故事 + 知识树生长
-  `projects/` — 项目文档：每个项目独立记录，持续填充
-  `interview-prep/` — 面试准备：差距分析、简历、故事库、模拟面试
-  `papers/` — 论文与外部资料精读笔记

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
│   ├── knowledge-tree.md              ← AI Learning System 知识树（持续生长）
│   ├── learning-manifesto.md          ← 学习宣言（10 条原则）
│   ├── python-learning-guide.md       ← Python 学习指南（30 关键词 + 四层架构）
│   ├── pandas-csv-excel-guide.md      ← 结构化数据处理指南（4 大核心操作）
│   ├── Workflow vs Agent：概念梳理与工程实践.md
│   ├── Claude Code、OpenClaw 与 Agent Runtime 的本质关系.md
│   ├── AI Agent 时代的几个核心认知与行业判断.md
│   ├── 搜索系统全景：召回、排序、评测与数据闭环.md ← 搜索方向地图
│   ├── 搜索工程到Agent的迁移地图.md ← 工业项目 → Agent 构建/评测方法论
│   ├── VLM训练演进与数据难度升级.md ← VLM 演进史 + 数据难度定位
│   └── VLM课程规划：多模态大模型的训练历程与发展.md ← VLM 课程大纲 + 自动化提效路线
│
├── projects/                          ← 按项目独立记录
│   ├── README.md                      ← 项目索引
│   ├── cot-compressed-evalset.md       ← CoT 质检项目（核心讲述故事）
│   ├── baidu-agent-migration.md        ← 百度物料迁移 Agent
│   └── fourth-paradigm-maas.md         ← 第四范式航空机务 MaaS
│
├── interview-prep/                    ← 面试准备
│   └── gap-analysis.md                ← 岗位差距分析 + 弥补计划（执行手册）
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
│   └── 07.meituan-search-llm-repr/    ← 美团搜索 LLM 语义表征（与 price-agent 对标）
│       ├── 原文.md                    ← 文章原文（中文）
│       └── 笔记.md                    ← 三期实践 + price-agent 对比 + 面试故事
│
└── src/                               ← 工具脚本
    ├── html_to_md.py                  ← HTML 转 Markdown 工具（通用，需 <article>）
    └── wechat_article.py              ← 微信文章正文提取（curl 抓取 + js_content 解析）
```

---

> 连接数 > 知识量。深度 > 广度。可讲的故事 > 读过的论文。
