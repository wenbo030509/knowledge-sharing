# CoT Compressed 数据交付

> 项目周期：2026-06 ~ 2026-07（3 周）
>
> 状态：🟢 已完成交付，持续深挖中

---

## 一、项目概览

### 背景

构建新的 Pretrain Eval Set。现有 Eval Set 不足以反映模型在**长尾知识 / Reasoning / Agent 链路**上的表现。本批次聚焦 Reasoning 和长尾知识部分的评测数据建设。

### 你的角色

负责 CoT Compressed 数据的质量保证，独立设计并搭建了端到端的质检和修复 Pipeline。

### 交付数据

| 指标 | 数值 |
|------|------|
| 交付总量 | 5,497 条 |
| 合格数据 | 4,346 条（79.06%） |
| 废弃数据 | 1,151 条（20.94%） |
| 黑盒占比 | 872 条 / 20.06% |

### 学科分布

| 学科 | 合格数量 | 占比 | 黑盒数量 | 黑盒占比 |
|------|----------|------|----------|----------|
| 数学（Math） | 2,911 | 66.98% | 582 | 19.99% |
| 物理（Physics） | 692 | 15.92% | 139 | 20.09% |
| 化学（Chemistry） | 562 | 12.93% | 114 | 20.28% |
| 生物（Biology） | 169 | 3.89% | 34 | 20.12% |
| 其他（Other） | 12 | 0.28% | 3 | 25.00% |

---

## 二、完整数据流

```text
[数据来源]
├── 算法工程师学科竞赛题目 + 合成 CoT（人工修改）
└── RL 训练集抽取 → 初版 CoT 压缩
            │
            ↓
[众包团队] 人工修复 CoT
            │
            ↓
[你的 Quality Gate Pipeline] ←── 你搭建的
    │
    ├── Gate 1: 格式验证
    │   输出：合格 / 简单废弃
    │
    ├── Gate 2: 内容验证
    │   输出：合格 / 不合格（进入修复）
    │
    ├── Gate 3: Pipeline 修复（LLM Repair）
    │   输出：修复成功 → 合格 / 修复失败 → 废弃
    │
    ├── Gate 4: 学科标签纠错
    │   ├── Step 1: 硬规则匹配（query 关键词）
    │   ├── Step 2: LLM 推理生成
    │   └── Step 3: 算法标签 vs 你的标签 → 一致=通过 / 不一致=人工审判
    │
    └── Gate 5: 黑盒数据验证
        输出：各学科黑盒占比 ≈ 20%
            │
            ↓
[交付算法团队] → 纳入 Pretrain Eval Set
```

---

## 三、Technical Anatomy（按主题）

### 主题 1：Quality Gate System — 多层质量关卡设计

你设计的五层 Gate 是一个 **Cascading Classification System**：

```text
Layer 1: Deterministic Rules (确定性规则)
    ├── 做什么：格式校验、字段完整性、数据类型检查
    ├── 特点：零成本、零延迟、100%可复现
    └── 处理：直接通过 / 直接废弃

Layer 2: Semantic Rules (语义规则)
    ├── 做什么：CoT 是否保留关键推理步骤？Answer 与 Reasoning 是否一致？
    ├── 特点：需要理解内容，但仍可写成规则
    └── 处理：通过 / 标记为"不合格"进入修复

Layer 3: Probabilistic Repair (概率性修复)
    ├── 做什么：LLM 驱动的 CoT 修复/补全
    ├── 特点：灵活但不确定，需要验证修复结果
    └── 处理：修复后 → 回到 Gate 2 重新验证

Layer 4: Label Correction with Adjudication (标签纠错 + 仲裁)
    ├── 做什么：两步漏斗（硬规则 → LLM）修正学科标签，分歧 case 人工仲裁
    ├── 特点：跨源交叉验证
    └── 处理：一致→通过 / 不一致→人工审判

Layer 5: Distribution Check (分布校验)
    ├── 做什么：验证各学科黑盒占比稳定在 20%
    ├── 特点：统计层面的质量保证
    └── 处理：偏差过大 → 调整配比
```

### 主题 2：标签纠错的两步漏斗

```text
Step 1: 硬规则匹配
├── 方法：query 中提取学科关键词
│   例："求导数" → Math / "牛顿定律" → Physics
├── 优势：快速、确定、零成本
├── 局限：覆盖不完整、跨学科 case 无法处理
└── 覆盖比例：[待补：你实际走了多少条规则匹配？]

Step 2: LLM 推理生成
├── 方法：规则匹配不上的 → LLM 推理学科归属
├── 优势：灵活、覆盖模糊和跨学科 case
├── 局限：有概率出错、成本高于规则
└── 覆盖比例：[待补：有多少条走了 LLM？]

Step 3: 人工仲裁
├── 触发条件：算法标签 ≠ 你的标签
├── 作用：最终权威判定 + 积累规则优化方向
└── 案例数：[待补：有多少条需要人工介入？]
```

**设计原理：** 这是经典的 ML 工程模式 — 确定性 → 概率性 → 人类。每一层处理自己能确定的部分，不确定的留给下一层。

### 主题 3：黑盒数据 20% 的统计学含义

为什么 20%？

```text
如果黑盒太少（如 5%）：
├── 统计推断不稳定，单个学科的样本量太小
└── 防过拟合能力弱

如果黑盒太多（如 50%）：
├── 白盒不够，无法做细致的 reasoning error analysis
└── 丧失了 Eval Set 的诊断价值

20% 是一个经验平衡点：
├── 足够做统计显著性检验
├── 各学科的子样本量可接受（如数学 582 条 → 95% 置信度下误差约 ±4%）
└── 不牺牲白盒的分析能力
```

### 主题 4：CoT 压缩与 Learnability

```text
CoT 压缩的本质问题：

压缩前          压缩后
Question         Question
  ↓                ↓
[详细推理]  →   [关键推理步骤]
  ↓                ↓
Answer           Answer

核心矛盾：
├── 压缩越多 → Token 越少，但 Learning Signal 可能丢失
└── 压缩越少 → Learning Signal 完整，但成本高、效率低

质检的终极标准：
不是"格式对不对"，而是"压缩后模型还能不能从中学到推理能力"

这直接对应 Information Bottleneck 理论：
min I(X; T) - β · I(T; Y)
    ↑               ↑
  压缩程度      保留的预测能力
```

---

## 四、知识树干节点

本项目涉及的知识树节点及其生长状态：

```text
Data / Foundational Data
├── Validation 🌿 ← 你实现了多层 Quality Gate
├── Cleaning 🌿 ← LLM Repair = LLM 增强版数据清洗
├── Transformation 🌿 ← Label Correction 是数据转换
├── Sampling 🌱 ← 黑盒配比背后的采样策略
└── Learnability 🌿 ← CoT 压缩的核心

Data / Evaluation
├── Benchark Design 🌿 ← 你在建设 Eval Set 的基础设施
└── Insight & Analytics 🌱

Data / Strategy
└── Data Mixture 🌿 ← 20% 黑盒配比

System / Workflow Engine
├── Retry & Backoff 🌱
├── State Management 🌱
└── Error Handling 🌱

Learning / Representation Learning
└── Information Bottleneck 🌿 ← CoT 压缩的数学基础
```

---

## 五、待深挖方向

以下是从 PM 视角需要向算法/工程视角补的方向：

### 算法视角待补

- [ ] 质检规则的有效性如何量化？（Precision / Recall）
- [ ] 两步漏斗每层的 accuracy / confusion matrix
- [ ] 修复后的数据分布 vs 修复前的数据分布有没有偏移？
- [ ] 黑盒 20% 的统计功效（statistical power）计算
- [ ] LLM Repair 的 false positive / false negative 分析
- [ ] CoT 压缩质量的自动化评估指标（如何判断"压缩得好不好"？）

### 工程视角待补

- [ ] Pipeline 的并发处理方案
- [ ] 修复失败的 retry 策略和幂等性设计
- [ ] 数据状态的流转追踪（一条数据从进入到离开经历了哪些状态变化）
- [ ] 质检规则的版本管理（规则改了之后历史数据怎么处理）
- [ ] 大规模化：如果数据量翻 10 倍，Pipeline 瓶颈在哪？

---

## 六、时间线

| 日期 | 进展 |
|------|------|
| 2026-06 | 项目启动，搭建 Pipeline |
| 2026-07-10 | 建立学习系统，Day 0 |
| 2026-07-11 | 完整汇报项目，首次 Technical Anatomy：Quality Gate System + 两步漏斗 + 黑盒 20% |
| 待续 | |

---

## 七、相关链接

- 每日汇报：[2026-07-11](../daily/2026-07-11.md)
- 知识树：[knowledge-tree.md](../knowledge-tree.md)
- 学习宣言：[learning-manifesto.md](../learning-manifesto.md)
