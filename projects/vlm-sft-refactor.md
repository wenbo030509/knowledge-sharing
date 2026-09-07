对。看完你这 4 份材料之后，我认为这个项目**不应该再包装成“VLM 视频数据生产 / Pipeline 建设”**。那样确实会把你实际做过的东西讲浅了。

你真正参与的是一条已经发生的链路：

> **多视频理解能力定义 → 数据寻源与难度控制 → 质检 → 靶向数据交付 → 模型错误诊断 → Rollout 数据合成 → SFT → Benchmark 对照评测 → Badcase 归因 → 下一轮数据策略**

而且已经有真实的模型结果：

* 内部评测 161 题，当前训练数据覆盖 72 题，约 45%
* 覆盖题子集：**+2.8**
* ClawEval 全量：**+0.5**
* WildClaw：**+2.3** 

这其实已经足够构成一个很好的 **Benchmark-driven VLM Data Strategy 项目**。

我建议你把项目重新定义成下面这个版本。

---

# 一、项目核心定位：不是“数据生产”，而是“靶向提升 VLM 多视频理解能力”

最核心的一句话：

> **针对 VLM 在多视频理解任务上的能力缺口，建立“模型诊断—靶向数据生产—质量控制—SFT—评测归因”的数据闭环，重点提升跨视频对比与推理能力，并通过自动化数据生产提高有效训练数据的供给效率。**

这里的关键词发生了变化：

原来：

> 数据生产 Pipeline

现在：

> **能力提升项目**

Pipeline 只是实现手段。

---

# 二、项目真正的“问题”是什么

你现有材料里其实已经有非常好的问题，只是之前没有把它提炼出来。

你们把多视频能力划成了：

### L1：跨视频感知

例如：

* 空间关系
* 计数
* 事件定位
* 行为识别

### L2：跨视频对比

例如：

* 过程错误检测
* 时间交叉引用
* 实体匹配 / 状态差异
* 模式对比
* 功能步骤对齐

### L3：跨视频推理

例如：

* 因果
* 假设 / 操作迁移
* 综合理解

而且 L1 → L2 → L3 本身就是一个复杂度递进体系。

所以真正的模型问题可以定义成：

> **模型在跨视频“对应—比较—推理”上的能力不足，而现有数据生产又存在难度坍缩、覆盖不足和证据结构不稳定的问题。**

这就比“多视频 VLM 是短板”具体很多。

---

# 三、你这个项目最有价值的技术问题其实是“数据没有真正对齐能力目标”

这是你材料里非常有价值、而且真的来自你一线工作的洞察。

## 问题 1：不是数据少，而是难度失真

你发现两个典型案例：

### 案例 A：空间复杂度坍缩

示例是：

> 真实复杂地铁线路图，多线路、高噪声。

最后标注人员给出来的却是：

> 极简交叉线路图。

结果数据虽然“答案正确”，但是模型实际上只学到了：

> “看到两条线交叉。”

没有学到：

> “在大量干扰信息中识别目标空间关系。”



### 案例 B：时间复杂度坍缩

示例：

> 1 小时长视频。

实际标注：

> 10 秒短视频。

那么模型根本没有获得：

> 长时间跨度的信息检索与整合信号。

你把这个问题定义为：

> **Difficulty Collapse**

而且进一步意识到：

> **数据正确 ≠ 训练信号正确。**

这是这个项目最值得保留的 insight。



---

# 四、所以项目第一阶段不是“建库”，而应该是建立 Ability × Difficulty 的数据坐标系

这是我对你现有项目最大的改造建议。

你的数据 Schema 不应该只是：

```text
video
question
answer
cot
```

而应该增加：

```text
sample_id

能力维度
├── L1 / L2 / L3
├── spatial
├── counting
├── temporal
├── entity_matching
├── state_change
├── causal
└── transfer

难度维度
├── video_duration
├── information_density
├── distractor_level
├── number_of_entities
├── cross_video_dependency
├── reasoning_steps
└── evidence_span

数据属性
├── source
├── video_type
├── paired_video
├── source_quality
├── annotation_quality
└── synthetic / real

训练属性
├── dataset_version
├── sampling_weight
├── SFT / pretrain
└── target_skill
```

于是每一个样本就不是：

> “一个视频问答”

而变成：

> **“针对 L2-实体状态差异、复杂度 4、双视频、跨时间证据的一条训练信号”。**

这样你后面的：

* 数据采集
* QC
* 主动学习
* 数据配比
* Benchmark
* badcase

才能真正连起来。

---

# 五、你参与的“寻源”其实应该重新定义为 Targeted Data Acquisition

你现在文件里写的是：

> 按题目考点设计检索逻辑，从 YouTube / B 站寻找视频，个别任务再切 / 拼 / 合成。

这个本身很好，但面试中不要讲：

> “我负责找视频。”

要讲：

> **我把传统的 keyword-based sourcing 改成 capability-driven sourcing。**

即：

```text
Benchmark 弱项
      ↓
能力维度
      ↓
数据缺口
      ↓
检索策略
      ↓
视频候选
      ↓
配对关系
      ↓
难度验收
```

例如：

```text
L2 / 状态差异
↓
寻找“同一实体不同状态”的视频对

L2 / 步骤对齐
↓
寻找“同一任务不同操作路径”的视频对

L3 / 迁移
↓
寻找“相似任务、不同环境”的视频对
```

因为多视频数据真正的核心不是“视频好不好”，而是：

> **有没有形成有效的 cross-video relation。**

你现有材料已经明确把：

* 同实体不同状态
* 同过程不同视角
* 同场景不同时间
* 同任务不同做法

定义为可配对视频。

这就是一个非常好的**数据策略设计点**。

---

# 六、第二阶段应该讲“Quality Gate”，而不是“我做了质检”

你现在的质检标准其实已经很不错：

```text
格式
唯一性
证据充分
难度对齐
能力匹配
```



但还可以再往上抽一层：

## 你实际上建立的是 Training Signal Quality Gate

因为每一个 QC 都对应训练风险。

| QC   | 训练风险                      |
| ---- | ------------------------- |
| 内容准确 | Label Noise               |
| 回答完整 | Reasoning Path 缺失         |
| 格式一致 | Output Distribution Drift |
| 视频匹配 | Language Shortcut         |
| 难度对齐 | Supervision Strength 不足   |
| 能力匹配 | Wrong Skill Supervision   |

你现有复盘里已经明确把四个质检维度映射到了 SFT 风险：标签噪声、过程缺陷、格式漂移、语言捷径。

这比“质检 400 条视频”高级很多。

---

# 七、第三阶段：项目核心从“数据交付”变成 Model Diagnosis

这一块是你现有材料里面最容易被低估的部分。

你们实际上做了：

> **Base Model Error Mapping**

而不是简单交数据。

具体是：

```text
Base VLM
   ↓
对 161 题全量推理
   ↓
与 Ground Truth 对比
   ↓
结果层 Error
+
过程层 Error
   ↓
Error Taxonomy
```

例如：

```text
Temporal Error
├── 漏看关键时间段
├── 时间顺序颠倒
└── 跨视频时间对应失败

Perception Error
├── object miss
├── state miss
└── relationship miss

Reasoning Error
├── skipped step
├── causal error
└── transfer failure
```

你现有文档已经明确记录了：

> Base 模型先跑全量 prompt，与人工 response 做结果层和过程层对比，再聚合成错误地图，决定数据补哪里以及 Rollout 应该规范什么行为。

**这一块应该成为你的项目主线之一。**

---

# 八、然后你才能自然地解释为什么不是“直接多标一点数据”

因为模型诊断以后会发现：

> 不是所有数据价值相同。

所以：

```text
错误地图
   ↓
数据缺口
   ↓
定向采集
   ↓
定向构造
```

这就是：

> **Targeted Data Strategy**

而不是：

> Scale Data Strategy。

---

# 九、第四阶段：Rollout 应该被定义成“高价值监督信号生成器”

这里尤其要注意，不要把它说成：

> “我们用了 RL。”

你自己材料已经判断得很准确：

> 本项目的 Rollout 最终进入 SFT，所以它本质是 guided data synthesis / rejection sampling，而不是 RL 参数更新。

流程：

```text
Problem Prompt
      ↓
Behavior Instruction
      ↓
Model Sampling
      ↓
N Candidate Responses
      ↓
Answer Correct?
      ↓
Reasoning Correct?
      ↓
Format Correct?
      ↓
Accept / Reject
      ↓
SFT Dataset
```

这个过程的意义是：

> **把模型已经会答但不会“正确解释”的轨迹，转换成可以学习的正向行为样本。**

这和你的 CoT 质检高度统一。

---

# 十、第五阶段：真正的实验结果其实已经给你了

这里千万不要重新编一个：

> “45.7 → 51.0”

因为你的真实项目已经有实际数字。

应该直接用真实结果：

| 评测          |       结果 |
| ----------- | -------: |
| 覆盖题型子集      | **+2.8** |
| ClawEval 全量 | **+0.5** |
| WildClaw    | **+2.3** |



但这三个数必须解释。

---

# 十一、+2.8、+0.5、+2.3 的真正意义是什么

这里其实是你这个项目最好的“实验设计”。

## ① 覆盖题：+2.8

说明：

> **针对性数据本身是有效的。**

也就是说：

$$
Targeted\ Data
\rightarrow
Capability\ Gain
$$

这是最直接的因果证据。

---

## ② ClawEval 全量：+0.5

这个数字小，不应该解释为：

> “模型只提升了一点。”

而应该解释：

> **靶向数据只覆盖了 72 / 161 个评测题，约 45%，所以全量指标被未覆盖题稀释。**

你的文档已经明确把**覆盖率**视为当前收益瓶颈。

所以这里真正的结论是：

$$
TargetedDataQuality
不是最大瓶颈
$$

而：

$$
TargetedDataCoverage
是最大瓶颈
$$

这是一个非常重要的项目判断。

---

# 十二、+2.3 WildClaw 反而特别重要

因为 WildClaw 并不是训练集里的那批视频。

你现有材料把它定义成：

> 训练 / 评测视频严格隔离。

因此：

$$
+2.3
$$

意味着：

> 模型没有简单记住训练视频，而是在野外视频上迁移了能力。

这比 +2.8 更有说服力。

你的材料也是这么归因的。

所以面试官问：

> “你怎么证明不是 overfit？”

你可以非常明确地回答：

> **我没有只看训练覆盖子集，而是同时看了全量内部 Benchmark 和严格隔离的视频集合 WildClaw；覆盖子集 +2.8，WildClaw +2.3，说明收益不仅发生在训练同分布样本上，还有跨视频内容迁移。**

---

# 十三、这里就能把项目提升到“Benchmark Driven Data Loop”

完整逻辑：

```text
             Benchmark
                 ↓
             Badcase
                 ↓
           Error Taxonomy
                 ↓
             Data Gap
                 ↓
        Targeted Acquisition
                 ↓
        Annotation / Rollout
                 ↓
             QC Gate
                 ↓
              SFT
                 ↓
         Benchmark Re-eval
                 ↓
          Gain Attribution
                 ↓
       下一轮数据策略
                 ↺
```

这才是你的真正项目。

---

# 十四、自动化 Pipeline 则作为“第二主线”，不要作为项目标题

你当前实际已经在推进：

```text
关键词爬取
↓
TOS 入库
↓
去重
↓
自动生成 Prompt
↓
自动生成初版 CoT
↓
飞书自动填写
↓
人工终审
↓
交付
```



这非常适合描述成：

> **把靶向数据策略产品化。**

不是：

> 我写了一个爬虫。

而是：

> **把“人工寻源 → 手工出题 → 手工写 CoT → 手工填表”的数据生产过程拆成可自动化 DAG，并保留人工作为最终质量 Gate。**

这里可以展开工程深度：

### 为什么不 100% 自动？

因为：

* 自动生成 Prompt 容易语义漂移；
* CoT 正确 ≠ CoT 可学习；
* 多视频题要求跨视频证据对应；
* 难度对齐很难靠单模型 confidence 判断。

所以：

> **自动化初版 + 人工终版**

是合理的 human-in-the-loop boundary。

你自己的材料已经明确这么设计。

---

# 十五、你还可以增加一个非常强的指标：Data Efficiency

虽然你现在没有完整的长期数据，但项目往这个方向讲是合理的。

不要只说：

> “我们生产了 400 条。”

应该计算：

$$
DataEfficiency =
\frac{\Delta Benchmark}{Effective\ Training\ Samples}
$$

或者：

$$
LabelEfficiency =
\frac{\Delta Benchmark}{HumanHours}
$$

因为最终价值是：

> **少量高质量靶向数据 > 大量无策略的数据。**

你现有实验实际上已经出现了这个信号：

> 只有约 45% benchmark 覆盖，覆盖子集已经 +2.8，而全量只有 +0.5。

这直接说明：

> **数据的“能力命中率”比单纯数据规模重要。**

---

# 十六、我甚至建议你不要把“长尾”定义成传统的 rare video

你这个项目的 long-tail 应该重新定义：

> **Capability Long Tail**

例如：

```text
L1
├── 常规 object understanding
└── complex spatial relation

L2
├── common comparison
├── temporal cross-reference
├── state difference
└── procedure alignment

L3
├── causal reasoning
├── hypothetical transfer
└── cross-video synthesis
```

然后定义：

$$
Coverage_k =
\frac{N(\text{skill bucket } k \text{ 达到最小有效样本量})}
{N(\text{skill buckets})}
$$

最终优化：

$$
\max \Delta Benchmark
$$

而不是：

$$
\max NumberOfVideos
$$

这就和你前面提出的 Active Learning 完全接起来了。

---

# 十七、如果让我把你的真实项目重新包装，我会这样命名

### 最推荐

> **VLM 多视频理解能力提升：Benchmark-driven 数据闭环与靶向 SFT 项目**

英文：

> **Benchmark-driven Data Loop and Targeted SFT for Multi-Video VLM Understanding**

比：

> VLM 多视频数据生产

强很多。

---

# 十八、项目的三个核心 Objective

不要再列十几个 Objective。

就三个。

### O1：提升多视频理解能力

核心：

$$
\text{ClawEval / WildClaw}
$$

真实结果：

$$
+2.8 / +0.5 / +2.3
$$

---

### O2：提高有效训练数据供给效率

通过：

* Targeted sourcing
* 自动 prompt / CoT
* TOS 入库
* 去重
* Human-in-the-loop QC

把数据生产从纯人工流程向半自动 Pipeline 迁移。

---

### O3：建立 Benchmark → Data 的闭环

把：

> 模型错在哪里

转化成：

> 下一轮数据应该生产什么。

你现有的评测反馈机制已经明确采用：

> 四类根因：任务定义、数据源、标注执行、评测规范；每轮选择一个主要变量进行下一轮验证。

这就是闭环的真正核心。

---

# 十九、最终你可以这样讲这个项目

**项目背景**

针对 VLM 在多视频理解场景下的能力缺口，团队需要构建面向 L1 跨视频感知、L2 跨视频对比、L3 跨视频推理的数据体系，并通过训练反馈持续提升模型在内部多视频 Benchmark 上的表现。实际数据生产过程中存在三个核心问题：一是视频素材和题目难度容易发生“难度坍缩”，数据虽然形式正确，但无法提供与目标能力匹配的训练信号；二是多视频任务要求建立实体、状态、时间和步骤之间的跨视频对应关系，传统单视频关键词寻源难以稳定产出可配对素材；三是数据交付与模型训练、评测之间存在断点，缺乏“模型 Badcase → 数据策略”的闭环。

**核心工作**

1. **建立能力维度与数据难度体系。** 将多视频任务拆分为 L1 跨视频感知、L2 跨视频对比、L3 跨视频推理，并进一步从视频时长、信息密度、干扰信息、实体数量、跨视频依赖程度、推理步数等维度定义样本难度。将“能力匹配 + 难度对齐”前置到视频采集阶段，避免标注完成后才发现训练信号失真。

2. **构建 Benchmark-driven 靶向数据采集机制。** 根据已有评测题型和模型错误分布反向定义数据缺口，针对实体状态差异、时间交叉引用、步骤对齐等 L2/L3 能力设计可配对视频检索策略，而不是单纯扩大视频规模。针对高难素材，通过换源、切分、拼接及少量构造补齐目标能力和难度要求。

3. **建立 Training Signal Quality Gate。** 从格式、唯一性、证据充分性、视频与问题匹配度、难度对齐、能力匹配等维度进行数据质检，并将 QC 与下游 SFT 风险建立映射：错误 response 对应标签噪声，跳步回答对应错误推理路径，格式漂移对应输出分布不一致，视频与问题弱相关对应语言捷径。对于多视频 CoT，要求采用“逐视频证据 + 对应关系 + 汇总结论”的结构，提高跨视频证据可追溯性。

4. **推进数据生产自动化。** 将关键词寻源、TOS 入库、视频去重、Prompt/初版 CoT 自动生成、飞书作业表自动填写串联成半自动 Pipeline，机器负责高吞吐的候选生成和预处理，人工保留终版审核和高风险样本兜底，实现数据生产从“人工全流程”向 Human-in-the-loop 模式迁移。

5. **打通模型诊断—数据生成—训练闭环。** 在 SFT 前使用 Base VLM 对评测题和已标注样本进行批量推理，通过结果层和过程层对比生成 Error Map，将模型错误聚合为感知、时序、推理、格式等问题类型，用于确定下一轮需要补充的数据方向及 Rollout 行为约束；随后通过行为引导 Rollout + 拒绝采样生成高质量正向轨迹，与人工三元组共同进入靶向 SFT。

6. **建立分层评测和收益归因机制。** 采用相同 Benchmark、相同题目、相同评测规范进行 SFT 前后对照，并同时观察训练覆盖子集、内部全量评测和严格隔离的 WildClaw 数据，区分“局部学会、全量收益、跨分布泛化”三类结果。当前真实实验中，覆盖题型子集提升 +2.8，ClawEval 全量提升 +0.5，WildClaw 提升 +2.3。覆盖子集与 WildClaw 的提升表明靶向数据能够产生可迁移能力增益，而全量增益较小主要受到当前数据覆盖率约 45% 的限制，因此后续优化重点从“提升单条数据质量”进一步转向“扩大高价值能力覆盖率”。

**项目关键洞察**

项目中发现，VLM 数据质量不能仅以“标签是否正确”衡量。数据难度本身就是训练信号的一部分：例如复杂地铁线路图被简化为单一交叉线路、1 小时长视频被替换成 10 秒片段时，数据表面上仍然正确，但实际上已经无法提供目标能力所需的学习信号。因此将“难度对齐”从质检后置项前移到数据采集 Gate，形成“能力覆盖 × 难度覆盖 × 证据质量”的训练数据评价框架。

**项目结果**

* 内部评测题目共 161 题，当前靶向训练数据覆盖 72 题，覆盖率约 45%；
* 覆盖题型子集：Benchmark **+2.8**；
* ClawEval 全量：**+0.5**；
* WildClaw：**+2.3**；
* 建立了从 Benchmark Badcase → Error Taxonomy → Data Gap → Targeted Data → SFT → Benchmark 的数据闭环；
* 将视频寻源、入库、去重、初版 Prompt/CoT 生成和作业交付逐步自动化，形成 Human-in-the-loop 数据生产流程。

---

# 二十、这个版本和你原来的版本，最大的区别

原来的项目叙事：

> 我负责视频采集、标注、质检、自动化。

现在的叙事：

> **我参与的是一个“模型能力提升项目”，数据生产只是其中一个环节。**

最终因果关系变成：

```text
模型 Benchmark
      ↓
发现能力缺口
      ↓
Error Map
      ↓
定义数据缺口
      ↓
Targeted Sourcing
      ↓
难度控制
      ↓
Quality Gate
      ↓
Rollout / SFT
      ↓
Benchmark
      ↓
+2.8 / +0.5 / +2.3
      ↓
发现真正瓶颈：Coverage
      ↓
下一轮继续扩充能力覆盖
```

这才是真正有“项目深度”的地方。

而且这里有一个我认为你**非常应该保留的反直觉结论**：

> **第一次实验最大的发现不是“我们的数据有效”，而是“数据有效，但覆盖不足”。**

因为：

$$
+2.8\quad(\text{覆盖子集})
$$

而：

$$
+0.5\quad(\text{全量})
$$

同时：

$$
+2.3\quad(\text{WildClaw})
$$

这三组结果组合起来，实际上已经告诉你下一轮应该优化什么：**不是继续无脑提高单条数据质量，而是扩大真正命中模型弱项的题型覆盖。**你现有材料也明确把约 45% 覆盖率视为当前最大瓶颈。

这就是一个非常完整的 **“实验 → 结论 → 资源重新分配 → 下一轮实验”** 的 Data Strategy 项目，而不只是一个数据交付项目。
