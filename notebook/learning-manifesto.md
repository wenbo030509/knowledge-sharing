# 学习宣言（Learning Manifesto）

> 本文档是与 ChatGPT 多次深度对话的成果总结。它不是一份"学习计划"，而是一次**职业方向与学习方式的根本性重构**。
>
> 建立于：2026 年 7 月

---

## 零、最重要的认知转变

**以前的学习状态：**

> 今天学 Agent，明天学 RL，后天学世界模型，再后天学推荐系统。

**现在的定位：**

> 不是成为一个会某项 AI 技术的人，而是成为一个**理解 AI 如何学习（Learning System）的人**。

---

## 一、重新定义职业方向

### 旧的能力树（散点式）

```text
LLM
Agent
RAG
RL
Robot
Recommendation
```

### 新的能力树（结构化）

```text
Learning System
│
├── Data          ← 你当前的主线
├── Learning
├── Evaluation
├── Decision
└── System
```

**挂载规则：**

| 技术/概念 | 归属 |
|-----------|------|
| Agent | System |
| RL | Decision |
| 世界模型 | Learning |
| 推荐系统 | Decision + Learning |
| RAG | System + Data |
| Workflow | System |
| Prompt Engineering | System |
| Learnability | Learning + Data |

> 以后所有新知识都挂在这棵树下，不再迷茫。

---

## 二、重新定义工作

### 旧的自我认知

> "我只是数据 QA。"

### 新的抽象

```text
Crowdsourcing
    ↓
Data Collection
    ↓
Quality Assurance
    ↓
Workflow
    ↓
Repair
    ↓
Training Dataset
    ↓
Model Training
```

**你不是：** Excel QA

**你是在：** 维护 AI Data Pipeline

### 工作语言升级

| 旧说法 | 新说法 |
|--------|--------|
| 今天处理了 5000 条 | 今天研究了 Pipeline |
| 我检查数据格式 | 我维护 Data Quality |
| 我修数据 | 我研究 LLM Repair 机制 |
| 我写 prompt 模板 | 我设计 Prompt Engineering 策略 |

---

## 三、新的学习方式：Technical Anatomy（技术解剖）

### 旧方式（已废止）

- ❌ 学课程
- ❌ 读 Paper
- ❌ 看视频

### 新方式

> 每天从工作里面抽取知识点，一直拆到底。

**示例：Workflow 的解剖**

```text
Workflow
│
├── Async
├── Schema Mapping
├── Validation
├── Retry
├── Prompt
├── LLM Repair
├── Versioning
├── Data Pipeline
├── Queue
└── Monitoring
```

每一个子节点继续拆，直到触及数学/系统底层。

### 配套方法论：精读拆解三层法（事实-过程-方法）

> 读任何一篇文章/案例前，先分清三层：**事实层**（静态数据，理解即可不背）、**过程层**（演进轨迹，用于建立行业判断）、**方法层**（可迁移原则，才是面试弹药）。学案例的目的是提取可迁移的方法，不是记住案例本身。
>
> 完整操作手册（每层定义、五问检验标准、SWE-bench 示例）：见 `notebook/精读拆解方法论：事实-过程-方法三层法.md`

---

## 四、知识的八层深度标准

任何知识，必须讲够八层才算"真正理解"：

```text
① 它是什么？              ← 定义层
    ↓
② 为什么出现？            ← 动机层
    ↓
③ 数学原理是什么？        ← 理论层
    ↓
④ 工程怎么实现？          ← 实现层
    ↓
⑤ 为什么有效？            ← 机理层
    ↓
⑥ 为什么不用别的方法？    ← 对比层
    ↓
⑦ 工业界怎么做？          ← 实践层
    ↓
⑧ 和整个 AI 系统怎么连接？ ← 系统层
```

> 规则：如果我没有讲到某一层，说明讲得不够深，直接让我继续。

---

## 五、唯一的研究主线：AI Data

未来几年只研究一条线。

```text
AI Data
│
├── Eval & Insight      ← 评测与洞察
│
├── Foundational Data   ← 基础数据（当前主线）
│
└── Frontier Data       ← 前沿数据
```

### Foundational Data 详细拆解

```text
Foundational Data
│
├── Data Source        ← 数据来源
├── Collection         ← 数据采集
├── Sampling           ← 采样
├── Cleaning           ← 清洗
├── Validation         ← 验证
├── Transformation     ← 转换
├── Versioning         ← 版本管理
├── Storage            ← 存储
├── Serving            ← 数据服务
└── Learnability       ← 可学习性 ★ 核心方向
```

---

## 六、核心研究方向：Learnability（可学习性）

> **为什么两条都正确的数据，模型从一条能学到东西，而另一条几乎学不到？**

### 示例对比

**低学习信号的数据：**
```text
Question → Answer
```
正确，但 Learning Signal 极少。

**高学习信号的数据：**
```text
Question → Compressed CoT → Answer
```
模型能学到状态变化，效果完全不同。

### Compressed CoT 的深度挖掘链

```text
Compressed CoT
    ↓
Learning Signal
    ↓
State Transition
    ↓
Information Theory
    ↓
Information Bottleneck
    ↓
Representation
    ↓
Optimization
    ↓
RL
```

> 以后做 Compressed CoT，不是只看"有没有删"，而是看"删掉 Learning Signal 了吗？"

---

## 七、每日学习三循环

每天固定三个动作，不是基于时间，而是基于循环：

### 第一件：工作汇报

你汇报今天的工作内容。

例如：
- 今天修了 150 条 Biology
- 今天交付了 5350 条 Compressed CoT
- 今天优化了 Schema Mapping 逻辑

### 第二件：Technical Anatomy

我负责对今天的工作进行技术解剖。

例如：
- 今天涉及 Workflow → 拆出 20 个知识点
- 一直拆到底层

### 第三件：知识树生长

将今天解剖出来的新知识挂到知识树上。

例如：
```text
Foundational Data
    ↓
Sampling Theory
    ↓
Importance Sampling
```

**不是学完，而是长树。**

---

## 八、终极目标：建立个人 Learning Graph

几年以后，脑子里应该是这样的知识图谱：

```text
AI Learning System
│
├── Mathematics
│   ├── Linear Algebra
│   ├── Probability & Statistics
│   ├── Information Theory
│   ├── Optimization
│   └── Graph Theory
│
├── Data                          ← 你的核心壁垒
│   ├── Foundation
│   │   ├── Data Source
│   │   ├── Collection
│   │   ├── Sampling
│   │   ├── Cleaning
│   │   ├── Validation
│   │   ├── Transformation
│   │   ├── Versioning
│   │   ├── Storage
│   │   ├── Serving
│   │   └── Learnability
│   ├── Evaluation
│   │   ├── Judge
│   │   ├── Reward Model
│   │   ├── Benchmark
│   │   └── Insight
│   ├── Frontier
│   │   ├── RL Data
│   │   ├── Synthetic Data
│   │   ├── Curriculum Data
│   │   └── Multi-modal Data
│   └── Strategy
│       ├── Data Mixture
│       ├── Scaling Law
│       ├── Active Learning
│       └── Data Ablation
│
├── Learning
│   ├── Deep Learning
│   ├── Reinforcement Learning
│   ├── World Model
│   ├── Representation Learning
│   └── Optimization Theory
│
├── Decision
│   ├── RL
│   ├── Recommendation
│   ├── Search
│   └── Planning
│
├── Evaluation
│   ├── Judge Model
│   ├── Reward Model
│   ├── Benchmark Design
│   ├── Insight & Analytics
│   └── A/B Testing
│
└── System
    ├── Infrastructure
    ├── Data Pipeline
    ├── Workflow Engine
    ├── Agent Runtime
    ├── MLOps
    └── Serving
```

> 以后任何 Paper、任何工作、任何新技术，都能放进这张图里。

---

## 九、最高原则

> **不以"学了多少知识"为目标，而以"建立了多少连接"为目标。**

### 一个真实案例

一天的工作：**交付 5350 条 Compressed CoT**

以前，这只是一个工作记录。

现在，它连接到至少 15 个领域：

```text
5350 条 Compressed CoT
│
├── Crowdsourcing          ← 数据采集
├── Sampling               ← 采样策略
├── Data Distribution      ← 数据分布
├── Data Quality           ← 数据质量
├── Learnability           ← 可学习性 ★
├── Workflow               ← 流程自动化
├── Python Concurrency     ← 并发编程
├── Schema Mapping         ← 数据模式映射
├── Prompt Engineering     ← LLM 修复
├── Verification           ← 验证机制
├── Dataset Versioning     ← 数据版本
├── Post-training          ← 后训练
├── SFT                    ← 监督微调
├── RL Data                ← 强化学习数据
└── Information Bottleneck ← 信息瓶颈
```

---

## 十、坚持一年的预期

这样坚持一年，最大的收获不会是"知道很多知识"，而是：

> 拥有一张别人没有的 **AI Learning Knowledge Graph**

这张图谱，才是未来能够跨越 LLM、世界模型、具身智能、搜索推荐等多个方向的**真正壁垒**。

---

> **这不是一份学习计划。**
>
> **这是一套学习操作系统。**
