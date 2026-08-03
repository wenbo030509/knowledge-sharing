# AI Learning System — Agent PM 秋招备战

> 目标：2026 年秋季招聘拿到 **Agent 产品经理** offer。
>
> 不是知识库，而是一套**学习操作系统**——四视角思维框架 + Technical Anatomy 八层解剖 + 知识树持续生长。

---

## 这是什么？

一套以"找到 Agent PM 工作"为目标的系统化学习体系。

- 📋 `CLAUDE.md` — Claude 行为规范：秋招目标 + 四视角思维框架 + 执行流程
- 📁 `notebook/` — 学习资料与指南
  - `0.knowledge-tree.md` — 知识树：AI Learning System 的完整骨架
  - `learning-manifesto.md` — 学习宣言：10 条核心原则
  - `python-learning-guide.md` — Python 学习指南（30 关键词 + 四层架构）
  - `pandas-csv-excel-guide.md` — 结构化数据处理指南（读取列/新增列/保存/批量）
  - 专题文章：Workflow vs Agent、Agent Runtime、行业认知
- 📅 `daily/` — 每日学习记录：工作汇报 + 技术解剖 + 面试故事 + 知识树生长
- 📁 `projects/` — 项目文档：每个项目独立记录，持续填充
- 🎯 `interview-prep/` — 面试准备：差距分析、简历、故事库、模拟面试
- 📄 `papers/` — 论文与外部资料精读笔记

---

## 面试竞争力公式

```text
面试竞争力 = 项目经验（可讲的故事）× 技术理解（能讨论的深度）× Agent 认知（产品 Sense）
```

---

## 四视角思维框架

| 视角 | 关注什么 | 在面试中的价值 |
|------|----------|--------------|
| PM 视角 | 流程设计、交付价值、用户需求 | 证明你能定义"什么是好" |
| 算法视角 | 量化指标、数学原理、模型行为 | 证明你能和算法团队深度对话 |
| 工程视角 | 规模化、可靠性、系统设计 | 证明你理解 Pipeline 不只是"写脚本" |
| 策略视角 | 实验设计、指标驱动、因果推断 | 证明你能用数据驱动决策 |

---

## 秋招时间线

```text
2026 年 7 月底（现在）
├── 目标明确：Agent PM
├── 知识体系 + 学习工具就位
└── 开始 Agent 产品日常使用 + 记录

2026 年 8 月
├── 投递第一批岗位
├── 自驱项目一：Agent 评测 Pipeline（开发中）
├── Agent 使用笔记积累
└── 简历持续迭代

2026 年 9 月
├── 面试密集期
├── 每周模拟面试
└── 论文阅读 5-8 篇

2026 年 10 月
└── offer 决策
```

---

## 知识的八层标准

任何知识必须讲够八层才算真正理解：

> ① 它是什么？ → ② 为什么出现？ → ③ 数学原理 → ④ 工程实现 → ⑤ 为什么有效？ → ⑥ 为什么不用别的方法？ → ⑦ 工业界实践 → ⑧ 与 AI 系统的连接

---

## 目录结构

```text
knowledge-sharing/
├── README.md                          ← 项目门户（你在这）
├── CLAUDE.md                          ← Claude 行为规范 + 秋招目标
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
│   └── AI Agent 时代的几个核心认知与行业判断.md
│
├── projects/                          ← 按项目独立记录
│   ├── README.md                      ← 项目索引
│   ├── cot-compressed-evalset.md       ← CoT 质检项目（核心面试故事）
│   ├── baidu-agent-migration.md        ← 百度物料迁移 Agent
│   └── xingzhi-finetuning.md           ← 行至 LoRA 微调
│
├── interview-prep/                    ← 面试准备
│   └── gap-analysis.md                ← 岗位差距分析 + 弥补计划（执行手册）
│
├── papers/                            ← 论文与外部资料精读
│   └── 01.anthropic-agent-evals/      ← Anthropic Agent 评测方法论
│       ├── 原文.md                    ← 英文原文
│       ├── 译文.md                    ← 中文翻译
│       └── 笔记.md                    ← 精读笔记（10 观点 + 3 故事）
│
└── src/                               ← 工具脚本
    └── html_to_md.py                  ← HTML 转 Markdown 工具
```

---

> 所有努力指向一个目标：秋季招聘拿到 Agent 产品经理 offer。
>
> 连接数 > 知识量。深度 > 广度。可讲的故事 > 读过的论文。
