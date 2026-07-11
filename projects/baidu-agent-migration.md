# 百度 — 广告物料迁移 Agent 与 B 端 AI 赋能

> 角色：B 端平台 PM（品牌广告投放平台）
>
> 周期：约 3-6 个月（推测）
>
> 状态：🟡 历史项目，知识反刍中

---

## 一、项目概览

### 业务背景

品牌广告投放平台需要支持广告主将物料（创意素材、文案、定向条件等）从一个平台迁移到另一个平台。这是一个典型的 B 端中台场景——两个平台的字段体系不同、数据格式不同、业务规则不同。

### 你做了什么

- 搭建了一个 Function Calling Agent，实现物料跨平台迁移
- 定义了输入 Schema 字段
- 处理了迁移失败的 Badcase，通过分类处理提升迁移成功率
- 用 Vibecoding（自然语言 + 文档 → 代码）驱动开发

### 核心成果

- 将人工物料迁移流程转变为 Agent 自动化处理
- **迁移成功率通过 Badcase 迭代持续提升**
- **大幅提高了物料迁移效率（可量化的效率提升）**

### 值得注意的地方

这是一个典型的 **B 端中台 PM 做 AI 赋能** 的案例。你不是"做了一个 Agent"，而是"用 Agent 替代了一个人工流程，并量化了效率提升"——这是 PM 做 AI 产品的正确姿势。

---

## 二、深度剖析

### 剖析 1：Function Calling 到底是什么？

这是你第二个项目中最核心的技术概念。你在字节做 LLM Repair 时也用到了同样的模式（LLM 作为修复工具被调用）。

#### ① 它是什么？

**Function Calling（函数调用）** 是一种让 LLM 调用外部工具/API 的机制。模型不再只输出文本，而是输出一个结构化的"函数调用请求"，然后外部系统执行这个函数，把结果返回给模型。

```text
没有 Function Calling：
用户: "帮我把这笔物料从 A 平台迁移到 B 平台"
模型: "好的，我已经帮你迁移了" ← 幻觉！模型没法真的操作平台

有 Function Calling：
用户: "帮我把这笔物料从 A 平台迁移到 B 平台"
模型: 分析意图 → 决定需要调用 migrate_material 函数
     ↓
模型输出（不要文本，要 JSON）:
{
  "function": "migrate_material",
  "parameters": {
    "material_id": "M12345",
    "source_platform": "platform_A",
    "target_platform": "platform_B"
  }
}
     ↓
外部系统执行迁移，返回结果: {"status": "success", "new_id": "M67890"}
     ↓
模型: "迁移成功！新物料 ID 是 M67890，你可以在这里查看..."
```

#### ② 为什么出现？

LLM 有两个根本限制：
1. **不能执行操作**：模型只能"说"，不能"做"
2. **知识不是实时的**：模型不知道当前数据库里有什么数据

Function Calling 解决了这两个问题：模型通过调用外部函数获得"动手能力"和"实时信息"。

#### ③ 数学/工程原理

Function Calling 不是魔法。它是这样工作的：

```text
Step 1: 定义函数声明
你告诉模型有哪些函数可用，每个函数的参数结构是什么。

{
  "name": "migrate_material",
  "description": "将一个广告物料从源平台迁移到目标平台",
  "parameters": {
    "type": "object",
    "properties": {
      "material_id": {"type": "string", "description": "物料ID"},
      "source_platform": {"type": "string", "enum": ["A", "B", "C"]},
      "target_platform": {"type": "string", "enum": ["A", "B", "C"]}
    },
    "required": ["material_id", "source_platform", "target_platform"]
  }
}

Step 2: 模型推理
模型根据用户输入 + 函数声明，判断：
- 要不要调用函数？
- 调用哪个函数？
- 填什么参数？

Step 3: 约束采样（Constrained Decoding）
模型生成时，不再是自由生成文本，而是在你定义的 Schema 约束下生成。
这就保证了输出的 JSON 结构一定合法。
```

#### ④ 工程实现

```python
# Function Calling Agent 的核心循环（伪代码）

# 1. 定义你有的工具
tools = [
    {
        "name": "migrate_material",
        "description": "物料迁移",
        "parameters": {...}  # JSON Schema
    },
    {
        "name": "check_migration_status",
        "description": "查询迁移状态",
        "parameters": {...}
    },
    {
        "name": "rollback_migration",
        "description": "回滚失败的迁移",
        "parameters": {...}
    }
]

# 2. Agent 循环
def agent_loop(user_input):
    messages = [{"role": "user", "content": user_input}]
    
    while True:
        # 调用 LLM，传入工具定义
        response = llm.chat(messages, tools=tools)
        
        # 如果模型要调用函数
        if response.has_tool_call():
            tool_call = response.tool_call
            # 执行函数
            result = execute_function(
                tool_call.function_name, 
                tool_call.parameters
            )
            # 把结果追加到对话历史
            messages.append({
                "role": "tool", 
                "content": result
            })
            # 继续循环 → 模型看到结果后决定下一步
        else:
            # 模型返回最终文本 → 结束
            return response.text
```

#### ⑤ 为什么你的 Schema 设计那么重要？

你定义了输入 Schema 字段，这决定了 Agent 能做什么、做得多准。

```text
Schema 定义得好的效果：
├── 模型知道每个字段的类型 → 不会传错格式
├── 字段 description 写得好 → 模型填参数时更准确
├── required 字段标记清楚 → 模型不会漏关键参数
└── enum 约束 → 模型只能在预定义选项中选，不会编造

Schema 定义得差的效果：
├── 模型猜参数含义 → 填错
├── 漏掉非 required 但实际必要的参数 → 函数执行失败
├── 没有 description → 模型乱填
```

**你在百度做的事 — Schema 设计 — 本质上是 Prompt Engineering 的结构化版本**。这是 Agent 工程质量的决定性因素。

#### ⑥ 为什么不用别的方法？

替代方案对比：

| 方案 | 做法 | 优点 | 缺点 |
|------|------|------|------|
| **硬编码 if-else** | 手写所有迁移规则的代码 | 100% 确定 | 两个平台100+字段，规则爆炸 |
| **纯 Prompt** | 让 LLM 输出文本，自己解析 | 简单 | 格式不稳定，解析易出错 |
| **Function Calling** | LLM 输出结构化 JSON，外部执行 | 兼顾灵活性和可靠性 | 需要仔细设计 Schema |
| **Workflow (Dify/n8n)** | 可视化编排固定流程 | 行为确定 | 难以应对边界 case |

在你的场景下，Function Calling 是对的：平台间字段映射有规律但不够规则化，硬编码不够灵活，纯 Prompt 不够可靠。

#### ⑦ 工业界实践

几乎所有主流 LLM 平台都支持 Function Calling：
- OpenAI：原生 Function Calling（2023 年 6 月发布）
- Anthropic：Claude Tool Use
- Google：Gemini Function Calling
- 国内：通义千问、文心一言、GLM 都支持

OpenAI 的 GPT-4 Function Calling 准确率约 85-95%（取决于任务的复杂度和 Schema 设计质量）——这个数字很重要：**Function Calling 不是 100% 可靠的，你需要 Badcase 处理机制**。你在百度做的 Badcase 分类处理，正是这个准确率上限的现实体现。

#### ⑧ 与 AI 系统的连接

```text
Function Calling 在 AI Agent 系统中的位置

[用户输入]
    ↓
[Agent Loop] ← 模型决定"下一步做什么"
    ↓
[Function Calling] ← 本主题：模型调用外部工具
    ↓
[外部系统/API] ← 你的物料迁移平台
    ↓
[结果返回] → Agent Loop 继续 → ... → 最终输出给用户
```

Function Calling 是 Agent 从"聊天机器人"升级为"能做事"的关键机制。你现在在字节做的 LLM Repair（用 LLM 修复数据），本质也是 Function Calling——你把 LLM 当作一个"修复工具"来调用。

---

### 剖析 2：从 Badcase 分类到成功率提升 — 数据驱动的迭代方法论

这是你在百度做得最 Product Manager 的事情，但同时也是最 Engineering 的事情。

#### 迁移失败的可能原因分类

```text
物料迁移失败原因树
│
├── Schema 层面（字段不匹配）
│   ├── 源平台有字段 X，目标平台没有
│   ├── 字段类型不一致（如源平台文本 vs 目标平台枚举）
│   └── 必填字段在源平台缺数据
│
├── 数据层面（数据质量问题）
│   ├── 源数据格式错误（如 URL 拼写）
│   ├── 源数据超长（目标平台字段长度限制）
│   └── 源数据语义冲突（如定向条件互相矛盾）
│
├── 业务规则层面（平台逻辑差异）
│   ├── 目标平台的审核规则与源平台不同
│   ├── 行业资质要求不同
│   └── 投放策略在不同平台有不同的限制
│
└── 系统层面（技术问题）
    ├── API 超时 / 限流
    ├── 并发冲突
    └── 目标平台暂时不可用
```

#### Badcase 驱动的迭代流程

```text
第 1 轮：初始 Agent（V1）
    ├── 迁移成功率：假设 60%
    ├── Badcase 采集：收集所有失败的 case
    │
    ↓ 分类分析
    │
发现：40% 的失败是因为 Schema 字段映射错误
    │
    ↓ 修复
    │
第 2 轮：优化 Schema 映射规则（V2）
    ├── 迁移成功率：假设 75%
    ├── Badcase 采集
    │
    ↓ 分类分析
    │
发现：15% 的失败是因为目标平台审核规则拦截
    │
    ↓ 修复
    │
第 3 轮：增加预检逻辑——迁移前先检查目标平台规则（V3）
    ├── 迁移成功率：假设 85%
    └── ...以此类推
```

**这本质上就是一个 ML 训练循环，不过是人驱动的而不是梯度下降驱动的：**

```text
ML 训练循环              你的 Badcase 循环
───────────              ────────────────
Forward pass →           执行迁移 →
Loss 计算 →              发现失败 →
Backprop →               分析原因 →
参数更新 →               修改规则/Schema →
下一轮                   下一轮
```

---

### 剖析 3：Schema Mapping 的本质

你在做物料迁移时，核心问题其实是 **Schema Mapping（模式映射）**——两个不同数据系统之间的字段对应关系。

#### 为什么 Schema Mapping 是 AI Data Pipeline 的核心问题

```text
平台 A 的物料结构          平台 B 的物料结构
──────────────            ──────────────
material_name: str        creative_title: str   ← 字段名不同
material_type: str        ad_type: enum        ← 类型不同
targeting: json           audience: json       ← 结构不同
budget: float             daily_budget: int    ← 单位不同（元 vs 分）
image_url: str            creative_image: str  ← 同样含义，完全不同的名字
```

**Schema Mapping 不是技术问题，是理解问题：**

> 你需要理解两个平台的业务语义，才能写出正确的映射规则。这是 PM 比纯工程师有优势的地方——你理解业务。

#### 你在当前字节工作的连接

你在字节做的 Label Correction（学科标签纠错），本质上也是 Schema Mapping：
- 源 Schema：算法团队的学科标签体系
- 目标 Schema：你的质检规范中的学科分类标准
- 映射方法：Rule + LLM 两步漏斗

这是一个跨公司、跨项目反复出现的模式。你已经做过两次了。

---

### 剖析 4：Plan-Execute Agent 模式

你提到在百度接触了 Plan-Execute 这种 Agent 模式。这是 Agent 设计中最经典的两种模式之一。

#### Plan-Execute vs ReAct

```text
Plan-Execute（你先遇到的那个）：
用户: "把 M123 从 A 迁移到 B"
    ↓
Plan 阶段：
├── Step 1: 读取物料 M123 在 A 平台的数据
├── Step 2: 检查目标平台 B 的字段要求
├── Step 3: 生成 Schema 映射
├── Step 4: 执行迁移
└── Step 5: 验证迁移结果
    ↓
Execute 阶段：按计划逐步执行
    ↓
如果某步失败 → 重新 Plan → Execute

ReAct（Reasoning + Acting，另一种经典模式）：
用户: "把 M123 从 A 迁移到 B"
    ↓
Thought: "我需要先查 M123 的数据"
Action: read_material("M123")
Observation: "M123 是一个图片素材，size 是 1200×800..."
    ↓
Thought: "目标平台 B 要求 size 不超过 1000×1000，需要先压缩"
Action: resize_image("M123", width=1000)
Observation: "压缩完成"
    ↓
Thought: "现在可以迁移了"
Action: migrate("M123", target="B")
Observation: "迁移成功，新 ID 是 M456"
```

| | Plan-Execute | ReAct |
|---|---|---|
| 思考方式 | 先想好全盘 → 再执行 | 边想边做，每步都观察 |
| 适用场景 | 任务复杂度已知、步骤可预判 | 环境不确定、需要灵活调整 |
| 优点 | Token 效率高（不用每步都输出完整思考） | 灵活、能应对意外 |
| 缺点 | 计划错了全盘重来 | Token 消耗大（每步都输出"思考"） |
| 你的场景 | ✅ 物料迁移的步骤相对确定 | — |

**你在百度的工作用 Plan-Execute 是合理的**——迁移一个物料的流程大致固定（读取 → 映射 → 写入 → 校验），不需要每一步都"重新思考"。

---

## 三、深度 Q&A

**Q1: Function Calling 和 API 调用有什么区别？**

A: API 调用是人写的代码调用 API。Function Calling 是**模型决定**要不要调用、调用哪个、填什么参数。关键区别在于"谁做的决定"——人决定 vs 模型决定。这回到了 Workflow vs Agent 的根本区分。

**Q2: Schema 设计得好不好怎么衡量？**

A: 两个核心指标：
1. **调用成功率**：模型能成功生成合法 Function Call 的比例。Schema 设计得好 → 模型不会生成不合法的参数
2. **参数准确率**：生成的参数中，真正正确的比例。这和 description 写得好不好直接相关

**Q3: Badcase 分类有什么方法论？**

A: 一个简单的框架：
```text
1. 收集足够多的 badcase（至少 50-100 个才能看到 pattern）
2. 先不急着归类，逐个读一遍，找感觉
3. 用"根因分析"归类（不是按表面现象，而是按根本原因）
   ❌ 表面分类："迁移失败"分为"API 报错"和"数据格式错"
   ✅ 根因分类："Schema 映射错误" vs "源数据质量问题" vs "平台规则冲突"
4. 按影响面排序（不是按数量，是按"修复这个类型能救回多少条"）
5. 优先修复影响面最大的那一类
```

**Q4: 你的 Agent 迁移成功率和人工迁移有什么区别？**

A: 假设人工迁移一个物料需要 5 分钟，Agent 需要 10 秒。如果 Agent 成功率是 85%，意味着：
- 85% 的物料完全自动化（效率提升 30 倍）
- 15% 需要人工介入（和原来一样）
- 综合效率提升：约 20 倍

但关键不是"快了多少"，而是：**15% 的失败 case 是持续优化的素材**。每次优化提升 1% 的成功率，乘以物料总量，就是巨大的效率收益。

**Q5: 为什么用 Vibecoding 而不是找工程师写代码？**

A: 这是一个现实选择。B 端中台 PM 往往没有专属工程师资源，排期优先级不如核心业务。Vibecoding 让你绕过了"等工程师排期"的瓶颈——你自己就能把流程跑通。这是 PM 做 AI 赋能的核心技能：**用自然语言驱动开发，快速验证想法，用数据说服团队投入工程资源**。

---

## 四、知识树干节点

```text
System / Agent Runtime 🌿
├── Function Calling 🌿 — 设计 Schema、嵌入 Badcase 循环
├── Agent Loop 🌱 — Agent 的核心循环模式
└── Tool Calling 🌿 — 模型调用外部工具

Decision / Planning 🌱
└── Plan-Execute 🌱 — 先规划再执行的 Agent 模式

Data / Transformation 🌿
└── Schema Mapping 🌿 — 两个平台间字段映射 ← 与字节 Label Correction 同类问题

Data / Validation 🌿
└── Badcase 分类 🌿 — 数据驱动的迭代优化

System / Workflow Engine 🌿
└── Vibecoding 🌿 — 自然语言驱动的工程实现

Evaluation 🌱
└── 可量化的效率提升 — 迁移成功率的持续追踪（虽然不够系统化，但比行至进了一步）
```

---

## 五、延伸拓展：面试话术

### PM 视角（你现在会说的）

> "我在百度负责广告物料跨平台迁移的产品设计，搭建了一个 Function Calling Agent，定义了输入输出 Schema，通过 Badcase 分类处理持续提升了迁移成功率，大幅提高了物料迁移效率。"

### 算法/工程视角（补齐后可以说）

> "我设计了一个基于 Plan-Execute 模式的物料迁移 Agent。核心设计包括：输入 Schema 的字段定义（确保模型参数填充准确）、Badcase 分类体系（Schema 层/数据层/规则层/系统层四类）、以及基于 Badcase 数据的迭代优化循环。我遇到的一个关键 case 是 Schema Mapping 引起的迁移失败——两个平台的字段语义相同但类型不同，通过增加类型转换的预处理逻辑解决。最终迁移成功率从初始的约 60% 提升到约 85%。"

### 面试官追问及准备

**追问：如果让你重新设计，你会怎么做？**

> "我会加三个东西。第一，评测体系——不只是看成功率，还要看每种 Badcase 类型的占比变化趋势，以及修复一类 Badcase 是否会引入新问题。第二，A/B 测试——修改 Schema 或规则后，对比新旧版本的差异。第三，自动重试——对于系统层面（API 超时）的失败，自动重试应该能救回不少 case。"

**追问：Plan-Execute 和 ReAct 怎么选？**

> "取决于任务的不确定性。物料迁移的步骤相对固定，Plan-Execute 更合适——先读源数据、再做映射、再写入、再校验，计划在第一步就确定了。但如果场景是'帮我优化这个广告投放方案'——目标不确定、中间可能需要多次调整——ReAct 更合适，因为每一步的结果都可能改变下一步的决策。"

---

## 六、开放问题（你可以思考后与我交流）

**O1:** 你在百度定义 Schema 字段时，最难处理的是哪种类型的字段？你是怎么解决的？

**O2:** Badcase 分类里，有没有遇到过"修好了一类，但引入了另一类新问题"的情况？这在工程上叫什么？

**O3:** 如果你要评估这个物料迁移 Agent 的 ROI（投资回报率），你会怎么算？

**O4:** 你现在在字节做的 Pipeline 修复和质检，和百度做 Badcase 分类处理，有什么本质相同和不同的地方？

---

## 七、岗位澄清（2026-07-11）

### 百度你的实际岗位：中台PM

```text
商业化品牌广告部门
│
├── 策略组 — 做 CTR/CVR 优化、出价策略、定向策略、预算分配
│       （你不是这个）
│
└── 中台组 — 做投放效率工具、平台能力建设、流程自动化
        （你是这个 ← 物料迁移Agent属于中台提效）
```

**中台PM 和 策略PM 的区别：**

| | 中台PM（你做的） | 策略PM |
|---|---|---|
| 核心目标 | 流程效率提升 | 业务指标提升 |
| 典型产出 | 自动化工具、平台能力 | 出价策略、定向策略、排序优化 |
| 工作方式 | 搭建系统/Agent/Workflow | 跑数据 → 定策略 → 上实验 → 看指标 |
| 你的百度项目 | ✅ 物料迁移Agent | — |

### 为什么你要补齐策略PM技能

不是为了把百度经历包装成"策略PM"，而是：

1. **技能通用性**：SQL + 数据分析 + A/B Test 在任何数据相关岗位都有用
2. **你的 AI Data 主线也需要**：验证 Pipeline 改动的效果、量化质检规则的有效性、设计数据策略实验
3. **就业面**：两类岗位（商业化策略PM、AI数据策略）你都能面，底层技能共享

### 百度项目和策略思维的真正连接

百度项目本身是**中台工作**，但你做 Badcase 分类 → 定位根因 → 修改策略 → 验证成功率提升的这个循环，恰好是**策略思维的体现**。不是因为你做了策略PM的工作，而是因为你用数据驱动的方式做了中台PM的工作。

---

## 八、两类"数据策略"的区别

技能重叠，但领域不同。面试时不要混淆：

```text
商业化数据策略                     AI 数据策略（你的主线）
──────────────                     ──────────────────
领域：搜索/广告/推荐                领域：LLM模型训练
对象：用户行为数据                  对象：训练数据
指标：CTR/CVR/GMV/ROI              指标：Learnability/合格率/数据配比有效性
方法：A/B Test on 线上流量          方法：Ablation Study on 训练数据
产出：出价/定向/排序策略            产出：采样/配比/质检策略

重叠技能：
├── SQL 取数跑数
├── 数据分析和规律发现
├── 实验设计 + 假设检验
├── 指标定义 + 归因分析
└── 数据驱动的决策框架
```

> 面试策略PM岗位时：强调你的通用技能（SQL + 分析 + 实验思维），用百度的 Badcase 循环和字节的 Pipeline 优化作为案例。不需要假装做过商业化策略，但可以证明你有策略思维。
>
> 面试 AI 数据岗位时：强调你的 Pipeline 实践经验 + Learnability 理解，策略思维是加分项。
