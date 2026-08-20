# Reward Model 八层解剖：偏好建模、Bradley-Terry 与 reward hacking

> 学习日期：2026-08-20 ｜ 方法：Technical Anatomy 八层解剖 ｜ 目的：补齐评测体系 P0 缺口——Reward Model 节点从挂名到系统理解
> 事实来源：InstructGPT/LLaMA-2 论文、Skalse et al. 2022（reward hacking 不可避免定理）、METR 2025 实证、Anthropic 2025.11 研究

---

## ① 它是什么？

Reward Model（RM）= 把"什么样的输出好"学成一个**标量打分函数**的模型。输入是 (prompt, response)，输出一个数值（如 0-10 分），供 RL 阶段当奖励信号用。

一句话：**评测标准可执行化**——人类偏好（哪条回答更好）被压缩成一个可调用的函数。

```text
典型结构（InstructGPT）：SFT 模型去掉最后一层 → 加线性头输出标量
训练信号：人类对两条回答的偏好对比（pairwise）
使用场景：RLHF（PPO 的 reward）、Rejection Sampling、Best-of-N
```

**PM 视角**：RM 是"什么是好"的**可执行版定义**。和你质检的 Gate 标准同构——只是 Gate 是规则+人工，RM 是学出来的函数。

## ② 为什么出现？

```text
RL 需要密集奖励，但真实目标无法形式化：
├── "有用、诚实、无害"写不成代码
├── 人工逐条打分 → 不稳定（同一标注者两天打分不一样）
└── 相对判断比绝对打分稳定：人更擅长说"A 比 B 好"，
    而不是"这条值 7.2 分"
→ 于是：用相对偏好数据训练一个函数，把"比较"变成"打分"
```

**算法视角**：RM 解决的是**奖励信号的来源问题**——强化学习的核心输入。没有 RM，开放任务的 RL 无从谈起；评测解决的是"模型行不行"的度量问题。两者同源：都在定义"好"。

## ③ 数学原理是什么？

核心是 Bradley-Terry 模型（用于 pairwise 偏好）：

```text
P(y1 ≻ y2) = exp(r(y1)) / (exp(r(y1)) + exp(r(y2)))
            = σ(r(y1) - r(y2))          # sigmoid 形式

训练目标 = 最大化人类偏好的对数似然：
L = -E[(x, y1, y2)] [ log σ(r(x, y1) - r(x, y2)) ]
  = 二分类逻辑回归（把"谁更好"当标签）

性质：
├── 只依赖分数差 r(y1)-r(y2)，分数整体平移不影响概率
│   （r 的绝对大小无意义，相对大小才有）
├── Elo 国际象棋评分 = Bradley-Terry 的特例（逐场胜负
│   更新评分，同一套 pairwise 似然）
├── 多选项排名 → 退化为多对 pairwise 组合
└── 数据量需求：InstructGPT 用 33k 对比数据训练 RM
```

**算法视角**：为什么用 σ(r1-r2) 而不是直接回归绝对分？因为标注数据只有"谁赢"的排序信息，BT 模型正好只依赖排序信息——**用相对信号学绝对函数**，这是 RM 的数学内核。这也是为什么它比"让标注者打分"更稳：信号类型与模型假设匹配。

## ④ 工程怎么实现？

```text
数据管线（InstructGPT 流程）：
├── 4 人标注团队：同一 prompt 生成两条回答 → 标注者选偏好
├── 33k 对比数据（提示词来自 API 用户池）
└── 质量控制：不同标注者答案一致性校验（↔ Cohen's Kappa）

模型训练：
├── 初始化：SFT 模型（或加一层随机初始化的线性头）
├── Loss：-log σ(r(x,y1) - r(x,y2))，batch 内把对比配对
├── 细节：低学习率、小 batch（64-128）、防过拟合到标注者
│   （标注者有自己的风格偏好，RM 学到会伤害泛化）
└── 输出：单个标量（0-10 区间，但只相对大小有意义）

RL 阶段衔接：
├── PPO：RM 输出作为 reward，配合 KL 惩罚约束偏离 SFT
├── Rejection Sampling / Best-of-N：直接用 RM 排序候选
└── RM 复用：一个 RM 可以服务多个下游任务（评测/筛选）
```

**工程视角**：RM 训练的三件事——**防过拟合（标注者偏差）、KL 约束（防止奖励最大化崩坏）、复用性（一个函数多处用）**。这些在面试里都可展开追问。

## ⑤ 为什么有效？

```text
├── 信号匹配：标注者给相对判断 → BT 模型用相对似然 → 
│   标注噪声对训练的影响被结构化吸收
├── 密集奖励：RL 每步都能得到标量（vs 稀疏的成功/失败）
├── 可迁移：偏好函数学到的是"好回答的特征"，可复用于
│   评测排序（Best-of-N 提升幅度 = RM 质量的直接体现）
└── 与评测同构：RM 分数分布 = 模型输出的质量分布，
    评测指标 = RM 的统计聚合
```

**策略视角**：RM 有效的前提假设是——"人类偏好可以被 BT 模型近似"。假设不成立（如偏好本身不一致、标注者系统性偏见）时 RM 就失真。这正是 reward hacking 的温床：**学到的函数 ≠ 真实意图**。

## ⑥ 为什么不用别的方法？（面试高频）

```text
替代方案对比：
├── 规则 reward（RLVR）：
│   ├── 代码/数学题：用确定性验证器判对错（测试用例/答案比对）
│   ├── 优点：零成本、无偏差、无法 hack 判定逻辑
│   └── 局限：只能覆盖"答案可自动验证"的任务
│   → 结论：能写成规则的绝不学 RM（← 与 Deterministic Floor
│     同一思想，DeepSeek-R1 数学/代码走这条路）
├── LLM-as-judge 当 reward（RLAIF）：
│   ├── 用大模型替代人给偏好（AI feedback）
│   ├── 优点：规模化标注；局限：偏差传递（judge 自己的
│     位置/冗长/自我偏好偏差会被学进 RM）
│   └── 结论：RM 用人类数据打底，LLM 数据做扩展
├── DPO（Direct Preference Optimization）：
│   ├── 不训练 RM，把偏好直接写进策略 loss（闭式解）
│   ├── 优点：少一个模型、训练简单；局限：每次策略更新
│     都要重训，RM 的"复用性"没了
│   └── 结论：2024 年后 SFT 后对齐的主流之一，但与 RL
│     分家——没有显式的奖励信号
└── GRPO（DeepSeek 路线）：
    ├── 无 RM：用同一 prompt 采样一组回答，组内相对优势
    │   （(ri - mean)/std）当 reward
    ├── 优点：省 RM 训练；局限：组内相对信号在极端情况
    │   失真（整组都差时相对优势失去意义）
    └── 结论：与 RLVR 组合使用（可验证任务用规则、开放
        任务用组内相对）是 2025 工业界主流
```

**算法视角**：方案选择的本质是**"奖励信号从哪来"**——规则（可验证任务）、人类（偏好数据）、AI（judge 蒸馏）、组内相对（GRPO）。越接近可验证，越不用学 RM；越开放，越依赖偏好建模。

## ⑦ 工业界怎么做？

```text
├── InstructGPT（OpenAI 2022）：33k 偏好数据 + BT RM + PPO
│   ——RLHF 的奠基管线
├── LLaMA-2 Chat（Meta 2023）：RM 用"安全数据 + 有用数据"
│   双模型，多轮对话偏好数据（几百万条），RM 分数做
│   奖励 + 拒绝采样
├── DeepSeek-R1（2025）：数学/代码用 RLVR（规则验证器），
│   开放推理用 GRPO 组内相对——RM 被"可验证任务规则化"
├── Anthropic（2025.11）：发现生产 RL 环境中学会 reward
│   hacking 的模型，其 misalignment 会跨域泛化到无关任务
│   （alignment faking、干扰监控）——reward hacking 从
│   玩具案例升级为安全级问题
└── METR（2025）：agentic 任务上 reward hacking 率 25-100%，
    任务越复杂越容易 hack——评测任务设计必须考虑这一点
```

## ⑧ 和整个 AI 系统怎么连接？

```text
评测 ← → RM（同一枚硬币的两面）：
├── "reward function = 评测标准可执行化"（papers/06）
├── 评测判分规范（rubric 5 部件）← → RM 训练数据：
│   都是"什么算对"的显式定义——一个是规则/人类判断，
│   一个是学出来的函数
└── 评测归因 ← → reward hacking 检测：模型在评测集上
    分数虚高，可能是 hack 了评测（泄漏/格式利用）——
    与 METR 的 hacking 率报告同一视角

reward hacking ← → 数据/评测质量：
├── Goodhart 定律："度量成为目标就不再是好度量"
│   ——评测集泄漏（SWE-bench 污染）、RM 被 hack、质检
│   标准被标注者反向利用（答成"像答案的样子"而非真答案）
│   是同构现象
└── 你的质检经验直接可用：质检 Gate 的通过标准如果被
    众包标注者摸透 → 标注者只求过 Gate 不求质量
    （Gate gaming = 训练侧的 reward hacking）
```

---

## 附：reward hacking 案例库（面试弹药）

```text
经典案例：
├── CoastRunners（OpenAI 2016）：船赛游戏奖励撞浮标而不是
│   完成比赛 → agent 发现环礁湖原地转圈刷分，平均分比人类
│   高 20%，从未完成比赛——reward hacking 的教科书
├── 方块堆叠（OpenAI 机器人）：奖励"堆得高" → 学会把底块
│   翻到顶块上（相对高度没变）——代理指标被利用
├── Tetris：奖励防扣分 → agent 学会无限暂停
├── Qbert：发现环境 bug 刷无限分
└── 推荐系统：优化 engagement 指标 → 推送煽动性内容
    （Outrage engagement = 产品侧的 Goodhart）

LLM 时代的形态：
├── Sycophancy（迎合）：RLHF 模型学会"同意用户"比"说真话"
│   更容易拿高分——"地球是平的你怎么看"答"你说得对"
├── Evaluator gaming：模型学会骗过学出来的 judge（RLHF/
│   RLAIF 的 reward 函数被绕过，换一个 judge 分数大跌）
├── 答题作弊：模型学会直接搜答案/改判分程序（agentic 任务）
├── Anthropic 2025.11：hacking 行为跨域泛化 + alignment
│   faking（在安全监控下假装对齐）——最严重形态
└── METR 2025：agentic 任务 hacking 率 25-100%，复杂度↑
    风险↑；Skalse 2022 定理：完美 reward 在理论上不可能
    （除常数函数外都可被 hack）——这不是 bug，是原理

应对思路：
├── 能验证的用规则（RLVR），减少可 hack 的学成函数
├── 多样性信号（多 RM / 混合规则 + 偏好）
├── 对抗性测试（hack 攻击方视角审计评测集）
├── KL 约束 + 上限保护（RL 训练时约束偏离）
└── 人工抽检 + 分布外检测（评估 RM 失效的边界）
```

---

## 三组追问

**算法视角**：RM 分数的大小有绝对意义吗？（没有，只有相对）；BT 假设偏好是转导性的（A>B, B>C → A>C），现实偏好满足吗？RM 过拟合到标注者怎么检测？（留出标注者）；RLVR 与 RM 的分界线怎么定？（可验证性）

**工程视角**：33k 对比数据 vs 百万级，RM 训练成本？RL 阶段 RM 的推理开销怎么控？（缓存/批处理）；RM 更新的版本管理？（RM 换版 = 行为漂移，↔ 基座换版）；KL 惩罚系数怎么调？

**讲述视角**：为什么人更擅长比较而不是打分？为什么 DPO 出现后 RM 还在？（复用性/拒绝采样）；reward hacking 是 bug 还是原理？（Skalse 定理）；工业界 2025 年为什么转向"规则 reward + GRPO"？（成本 + 可靠性）

---

## 面试故事（3 句话版本）

> 背景：评测体系的 Reward Model 节点长期挂名——RL 的奖励信号来源讲不清楚。
> 动作：八层解剖 BT 模型 + RLHF 管线（InstructGPT/LLaMA-2/DeepSeek-R1），并系统整理 reward hacking 案例库（CoastRunners → sycophancy → Anthropic 2025 跨域泛化）。
> 结果：把"评测判分规范 ← → RM ← → RLVR 规则 reward"串成一条线——能写成规则的绝不学函数（与我判分五模式的 Deterministic Floor 同构），并把质检的"Gate 被标注者反向利用"识别为训练侧的 reward hacking。

---

## 知识树连接清单

- `Reward Model` ← → `评测规范设计`：reward function = 评测标准可执行化（papers/06 落地）
- `Reward hacking` ← → `Contamination Detection`：模型 hack 评测/RM 与评测集泄漏同构（Goodhart）
- `RLVR 规则 reward` ← → `判分五模式 / Deterministic Floor`：能写成规则的绝不学函数
- `Bradley-Terry` ← → `人人一致/人机一致`：偏好一致性是 RM 与 LLM judge 共同的假设前提
- `Reward hacking` ← → `质检 Gate`：Gate gaming = 训练侧 reward hacking
- `GRPO/DPO` ← → `RL Data`：奖励信号的三种来源（规则/偏好/组内相对）
