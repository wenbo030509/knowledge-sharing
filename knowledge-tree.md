# AI Learning System — 知识树

> 这是你的个人知识图谱。每一个节点不是"学完了"，而是"正在生长中"。
>
> 标记说明：
> - 🌱 已建立节点，待深入
> - 🌿 正在深挖中
> - 🌳 已形成系统理解
> - ⭐ 核心研究方向

---

## 根：AI Learning System

```text
AI Learning System
│
├── Mathematics
├── Data              ← 你的核心壁垒
├── Learning
├── Decision
├── Evaluation
└── System
```

---

## 一、Mathematics（数学基础）

```text
Mathematics
│
├── Linear Algebra 🌱
├── Probability & Statistics 🌱
├── Information Theory 🌿
│   ├── Entropy
│   ├── Mutual Information
│   ├── KL Divergence
│   └── Information Bottleneck 🌿 ⭐ (CoT 压缩的数学本质)
├── Optimization 🌱
│   ├── Gradient Descent
│   ├── SGD / Adam
│   └── Convergence Theory
└── Graph Theory 🌱
```

---

## 二、Data（数据）⭐ 核心主线

### 2.1 Foundational Data（基础数据）

```text
Foundational Data
│
├── Data Source 🌿
│   ├── Crowdsourcing
│   ├── Expert Annotation
│   ├── Web Crawling
│   ├── Synthetic Generation
│   └── User Behavior Logs
│
├── Collection 🌿
│   ├── Pipeline Design
│   ├── API Integration
│   └── Streaming vs Batch
│
├── Sampling 🌿
│   ├── Uniform Sampling
│   ├── Stratified Sampling
│   ├── Importance Sampling
│   ├── Active Sampling
│   ├── Curriculum Sampling
│   ├── Data Mixture
│   └── Scaling Law
│
├── Cleaning 🌿
│   ├── Deduplication
│   ├── Noise Detection
│   ├── Outlier Removal
│   ├── Format Normalization
│   └── LLM Repair (LLM 驱动的数据修复)
│
├── Validation 🌿
│   ├── Format Validation (Gate 1: 格式完整性)
│   ├── Schema Validation (Gate 2: 字段合规)
│   ├── Constraint Validation
│   ├── Semantic Validation (Gate 3: 内容一致性)
│   ├── Consistency Check
│   ├── Statistical Validation
│   ├── Distribution Check (Gate 5: 黑盒配比)
│   ├── Quality Gate System (Cascading Classification) 🌿
│   └── Learnability Check ⭐
│
├── Transformation 🌿
│   ├── Schema Mapping
│   ├── Format Conversion
│   ├── Label Correction (Rule + LLM 两步漏斗)
│   ├── Feature Engineering
│   └── Tokenization
│
├── Versioning 🌱
│   ├── Dataset Lineage
│   ├── Diff Tracking
│   └── Rollback Strategy
│
├── Storage 🌱
│   ├── Parquet / Arrow
│   ├── Data Lake
│   └── Indexing
│
├── Serving 🌱
│   ├── Data Loader
│   ├── Streaming Serving
│   └── Caching
│
├── Learnability ⭐ 🌿  ← 核心方向
    ├── Learning Signal (CoT 压缩 = 信号提纯)
    ├── State Transition
    ├── Information Bottleneck 🌿
    ├── Compressed CoT 🌿 (5497 条质检实践)
    ├── Data Efficiency
    ├── Curriculum Design
    └── Sample Difficulty
```

### 2.2 Evaluation（评测与洞察）

```text
Evaluation
│
├── Judge Model 🌱
├── Reward Model 🌱
├── Benchmark Design 🌿 (Eval Set 建设实践中)
│   ├── Train/Test Split 策略
│   ├── Black-box / White-box 配比 (20%/80%)
│   └── 长尾知识 + Reasoning 覆盖
├── Insight & Analytics 🌿 (SQL + 数据分析 = 基础能力)
├── A/B Testing 🌿 ← 策略 PM 核心技能，与 AI Data 高度通用
│   ├── 实验设计（实验组 vs 对照组）
│   ├── 样本量计算（统计功效）
│   ├── 假设检验（t-test, chi-square）
│   ├── 指标设计（核心指标 + 护栏指标）
│   └── 因果推断（进阶）
└── Causal Inference 🌱
```

### 2.3 Frontier Data（前沿数据）

```text
Frontier Data
│
├── RL Data 🌱
│   ├── Preference Data
│   ├── Trajectory Data
│   └── Reward Signal
├── Synthetic Data 🌱
├── Curriculum Data 🌱
└── Multi-modal Data 🌱
```

### 2.4 Data Strategy（数据策略）

```text
Strategy 🌿 ← 策略 PM 核心技能直接映射
│
├── Data Mixture 🌿 (黑盒 20% 配比实践)
├── Scaling Law 🌱
├── Active Learning 🌱
├── Data Ablation 🌱
├── Metric Design 🌱 ← 新增：指标定义是策略制定的起点
└── ROI Estimation 🌱 ← 新增：策略价值量化
```

---

## 三、Learning（学习机制）

```text
Learning
│
├── Deep Learning 🌱
│   ├── Transformer
│   ├── Attention Mechanism
│   └── Next-Token Prediction
│
├── Reinforcement Learning 🌱
│   ├── Policy Gradient
│   ├── PPO
│   ├── DPO
│   └── GRPO
│
├── World Model 🌱
│   ├── State Representation
│   ├── Dynamics Prediction
│   └── Latent Space
│
├── Representation Learning 🌱
│   ├── Embedding
│   ├── Contrastive Learning
│   └── Manifold Learning
│
└── Optimization Theory 🌱
    ├── Loss Landscape
    ├── Grokking
    └── Phase Transition
```

---

## 四、Decision（决策系统）

```text
Decision
│
├── RL 🌱
│   ├── MDP
│   ├── Value Function
│   └── Policy Optimization
│
├── Recommendation 🌱
│   ├── Collaborative Filtering
│   ├── Two-Tower Model
│   └── Ranking
│
├── Search 🌱
│   ├── Retrieval
│   ├── Reranking
│   └── Hybrid Search
│
└── Planning 🌱
    ├── Tree Search
    ├── MCTS
    └── Hierarchical Planning
```

---

## 五、Evaluation（评测体系）

```text
Evaluation
│
├── Judge Model 🌱
│   ├── LLM-as-Judge
│   ├── Pairwise Comparison
│   └── Rubric Design
│
├── Reward Model 🌱
│   ├── Bradley-Terry
│   ├── Preference Modeling
│   └── Reward Hacking
│
├── Benchmark Design 🌱
│   ├── Metric Selection
│   ├── Test Set Construction
│   └── Contamination Detection
│
├── Insight & Analytics 🌱
│   ├── Error Analysis
│   ├── Case Study
│   └── Pattern Discovery
│
└── A/B Testing 🌱
```

---

## 六、System（系统工程）

```text
System
│
├── Infrastructure 🌱
│   ├── GPU Cluster
│   ├── Distributed Training
│   └── Inference Serving
│
├── Data Pipeline 🌿
│   ├── ETL
│   ├── Stream Processing
│   ├── Batch Processing
│   ├── Async / Concurrency
│   ├── Queue System
│   └── Monitoring
│
├── Workflow Engine 🌿
│   ├── DAG Orchestration
│   ├── Retry & Backoff
│   ├── State Management
│   ├── Versioning
│   └── Error Handling
│
├── Agent Runtime 🌿
│   ├── Agentic Loop
│   ├── Tool Calling 🌿 (LLM Repair = LLM-as-Tool)
│   ├── Context Management
│   └── Memory System
│
├── MLOps 🌱
│   ├── Experiment Tracking
│   ├── Model Registry
│   └── CI/CD for ML
│
└── Serving 🌱
    ├── Model Deployment
    ├── Load Balancing
    └── Latency Optimization
```

---

## 知识连接记录

> 记录每天新建立的连接。格式：`[日期] 节点A ← → 节点B：连接说明`

### 2026-07-10

**A. 学习系统初始化（10条）：**

- `Compressed CoT` ← → `Information Bottleneck`：压缩的本质是保留学习信号，丢弃冗余信息
- `Data Quality` ← → `Learnability`：数据质量的终极标准是"模型能不能从中学到东西"
- `Workflow` ← → `Data Pipeline`：Workflow 是 Pipeline 的控制层
- `Prompt Engineering` ← → `LLM Repair`：Prompt 是修复工具的接口设计
- `Schema Mapping` ← → `Transformation`：Schema 映射是数据转换的一种形式
- `Crowdsourcing` ← → `Sampling`：众包标注天然带有采样偏差问题
- `SFT Data` ← → `RL Data`：SFT 教模型"说什么"，RL 教模型"怎么想"
- `Python Concurrency` ← → `Data Pipeline`：并发是 Pipeline 吞吐的工程基础
- `Verification` ← → `Evaluation`：验证是评测体系的前置关卡
- `Post-training` ← → `Learnability`：后训练的效果上限由数据的可学习性决定

**B. 个人背景分析（8条）：**

- `Badcase 分类` ← → `Validation 反馈回路`：Badcase 处理本质是 Validation 的闭环
- `Function Calling` ← → `Agent Runtime 工具层`：FC 是 Agent 与外部系统交互的接口
- `Dify Workflow` ← → `DAG Orchestration`：Dify 可视化编排 = DAG 的有向无环图执行
- `LoRA 微调无 Evals` ← → `Evaluation 不可或缺`：没有评测的微调 = 没有方向的训练
- `Vibecoding` ← → `工程实现层`：自然语言→代码 = 当前工程能力的补充路径
- `Schema Mapping` ← → `Data Transformation 特化`：Schema 映射是数据转换的具体形式
- `Seed 模型数据供给` ← → `Data ↔ Learning 交界`：你在 Pipeline 和模型训练的接口处
- `三段经历的共性缺失` ← → `Evaluation 体系`：从行至到百度到字节，Evals 始终缺失

### 2026-07-11

- `CoT 质检` ← → `Learnability`：质检的终极标准不是格式对不对，而是压缩后模型还能不能学到
- `Rule + LLM + Human` ← → `Cascading Classification`：确定性层→概率层→人类层，你独立设计出了这个经典 ML 工程模式
- `黑盒 20%` ← → `Train/Test Split`：Eval Set 设计中的防过拟合策略，20% 是统计显著性与可分析性的平衡点
- `质检规则` ← → `Eval Set 有效性`：Garbage in, garbage out — 数据质量决定了评测的可靠性
- `学科标签纠错` ← → `Rule + LLM 双通道`：硬规则兜底覆盖确定性 case，LLM 覆盖模糊 case，人工仲裁分歧
- `Pipeline 修复` ← → `LLM-as-Tool`：将 LLM 作为修复工具嵌入 Pipeline，是 Agent 模式的工程化应用
- `众包 → 质检 → 修复` ← → `AI Data Pipeline 闭环`：完整的数据生产-质检-修复-交付链路
- `CoT 压缩` ← → `Information Bottleneck`：数学公式 min I(X;T) - β·I(T;Y)，压缩保留的是 Y 相关信息
- `Quality Gate` ← → `Cascading Classification`：多层关卡的每一层都在做分类决策：通过/修复/废弃
- `Eval Set 建设` ← → `Benchmark Design`：你正在实践的正是 ML 评测体系的基础设施建设
- `SQL + 数据分析` ← → `策略PM 生存技能`：不会取数跑数，数据和算法方向都走不远
- `A/B Test` ← → `Evaluation 体系`：实验设计是评测的工程化表达
- `策略PM 技能栈` ← → `AI Data 技能栈`：SQL/分析/实验/指标四件套完全通用
- `百度 Badcase 循环` ← → `策略迭代框架`：假设→实验→数据→迭代，同一个模式
- `字节 Pipeline 优化` ← → `策略指标提升`：合格率、修复成功率的优化 = 策略指标优化
