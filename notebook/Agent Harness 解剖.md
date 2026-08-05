# Agent Harness — 八层 Technical Anatomy

> 主题：Harness（Agent 运行外壳）
> 日期：2026-08-05
> 状态：🌿 正在深挖中（八层解剖完成，待面试检验 + 工业界持续跟踪）
> 面试价值：Agent PM 的杠杆认知——能力在模型层，行为在 harness 层，产品设计空间在 harness 层

---

## ① 它是什么？

**一句话定义：Harness 是把「会聊天的模型」变成「能行动的 Agent」的工程外壳——模型本身之外的一切运行环境。**

- 词源：harness = 马具。马（模型能力）再强，不套上缰绳挽具，就无法拉车干活。
- 类比 1（操作系统）：模型 = CPU，harness = OS——CPU 只算指令，OS 负责进程、文件、权限、输入输出，让程序可用的正是 OS。
- 类比 2（舞台）：模型 = 演员，harness = 舞台 + 灯光 + 剧本 + 场务。观众看的是戏，但戏能不能成立取决于舞台系统。

**组成（模型之外的一切）：**

```text
Harness
├── Agent Loop          — observe → reason → act → feedback → iterate 的工程实现
├── Tool System         — 工具注册、参数校验、调用执行、错误返回
├── Context Management  — 窗口管理、压缩、记忆、检索
├── Permission & Safety — 文件系统/网络/命令的授权模型、hook、沙箱
├── System Prompt & Scaffolding — 控制模型行为的指令层（系统提示、skills、项目指令）
└── Environment Interface — 终端、文件、浏览器、GUI（Claude Code vs OpenClaw 的差异就在这层）
```

**已知实例：** Claude Code（SWE harness）、OpenClaw（computer-use harness）、OpenAI Codex、Cursor Agent。

---

## ② 为什么出现？

**核心问题：LLM 输出的是文本，但「行动」需要的是对环境的操作。中间缺一整层工程。**

时间线（工程视角）：

```text
2023 前      ChatBot 时代：Input → Generate → Output，模型不接触环境
2023.6       function calling API：模型能输出结构化工具调用意图
            └── 但执行仍由开发者自己写循环，每个应用重复造轮子
2023-2024    Agent 框架爆发（AutoGPT/LangChain）：prompt 驱动「伪 agent」
            └── 无权限边界、无恢复机制、上下文爆炸 → 可靠性崩塌
2024-2025    专业 harness 产品化：Claude Code / Codex / Devin
            └── 工具调用 + 上下文管理 + 权限 + 恢复 打包成可用产品
2024.11      MCP 开源：工具接入标准化，harness 生态开始统一
```

**没有 harness 之前怎么做的（PM 视角）：**

- 每个 Agent 应用从零实现「模型输出 → 解析 → 执行 → 回传」循环，质量参差
- 对话式 AI 只能回答问题，无法真正完成任务（查库存、改代码、操作浏览器）
- 权限和安全靠各家自己拍脑袋，事故频发

**为什么必须集中化（策略视角）：** 工具调用、上下文管理、权限、恢复是**每个** Agent 应用的公共基础设施。把它们从「每个应用自己写」变成「一个可复用的运行层」，是软件工程的分层思想在 Agent 领域的必然结果。

---

## ③ 数学原理是什么？

Harness 本身不是学习算法，没有自己的公式；但它服务的 Agent 循环有清晰的数学框架，harness 是这些框架的工程实现（算法视角）：

**MDP 视角：Agent 运行 = 马尔可夫决策过程的在线执行**

```text
State   = 上下文（对话历史 + 环境状态快照）
Action  = 文本输出 / 工具调用
Transition = harness 执行动作，环境产生新状态
Reward  = 任务成功信号 / 环境反馈（测试通过、错误信息）
```

Harness 就是 MDP 中「环境接口」的工程实现——它决定了模型的 Action 怎么落地、Feedback 怎么回传。

**RL 训练视角（与你的数据工作直接连接）：**

RLHF / RLVR 训练 Agent 时，harness 就是 **rollout 环境**：

```text
训练分布 = f(harness 设计)
├── 工具集决定模型能采取什么动作
├── 反馈形式决定模型学什么（错误信息质量 = 学习信号质量）
└── 权限边界决定探索空间
```

→ 结论：**harness 设计直接影响训练数据分布。** 这是「Agent 数据」和「harness」的连接点——你在字节做的数据质量工作，在 Agent 训练里有一半发生在 harness 层。

**信息论视角：harness 的上下文管理设计「模型能看到什么」**

- 上下文窗口有限（如 200k tokens）→ 压缩/检索/裁剪 = 在有限 token 预算下最大化相关信息量
- Harness 是**信息瓶颈的设计者**（连接你的 Information Bottleneck 节点）：它决定哪些信息进入模型的感知范围

**工程数学（工程视角）：**

- Token 预算分配 = 约束优化问题
- 工具参数校验 = 模式匹配/类型检查问题
- 对不稳定模型输出做确定性兜底 = 概率与可靠性问题（重试策略、上限设计）

---

## ④ 工程怎么实现？

以 Claude Code 为解剖对象（最熟悉的实例，工程视角 + PM 视角）：

**Agent Loop（主循环）**

```text
while 任务未完成 and 迭代次数 < 上限:
    感知  → 读文件 / 跑命令 / 看测试结果
    推理  → 模型生成思考 + 计划
    行动  → 输出文本 或 调用工具
    观察  → 读取工具执行结果
    失败  → 模型看到错误信息，自我修复（重试循环）
```

**Tool System（工具系统）**

```text
每个工具 = 一个 JSON Schema（名称 / 参数定义 / 描述）
    ↓
模型输出 tool_call（结构化指令）
    ↓
harness 校验参数合法性（工程视角：失败返回给模型重试，而非崩溃）
    ↓
执行工具
    ↓
结果注入上下文 → 模型继续推理
```

MCP（Model Context Protocol）= 工具接入的标准协议：工具/资源/Prompt 三类能力，stdio/HTTP 两种传输。harness 通过 MCP 连接外部工具生态，无需为每个工具写定制代码。

**Context Management（上下文管理）**

```text
窗口有限 → 三种策略组合：
├── 压缩：把历史对话总结成摘要，释放空间
├── 裁剪：丢弃最早/最不相关的轮次
└── 检索：repo index / 按需加载（不把整个仓库塞进上下文）
```

**Permission & Safety（权限与安全边界）**

```text
├── 授权模型：每个工具调用按权限模式（默认询问 / 允许 / 拒绝）
├── Hook 系统：在工具调用前/后插入自定义逻辑（拦截、记录、审批）
├── 沙箱：worktree 隔离（改动不污染主分支）、容器隔离
└── 网络/命令：敏感操作默认拒绝
```

**Scaffolding（行为指令层）**

```text
├── 系统提示：harness 内置的行为规范（怎么用工具、什么时候停）
├── Skills：按需加载的指令包（项目自定义工作流）
└── CLAUDE.md：项目级指令注入（这个仓库的 CLAUDE.md 就是实例）
```

**Environment Interface（环境接口）**

```text
Claude Code：Terminal + FileSystem + Git + Shell + 浏览器
OpenClaw：   GUI（鼠标/键盘/窗口）via Playwright / PyAutoGUI / VNC
             + 视觉系统（screenshot / OCR / DOM tree）
```

**失败恢复（可靠性核心，工程视角）：**

```text
├── 错误不是终结而是输入：工具报错 → 模型看到 → 修复重试
├── 重试上限：防止死循环（连接 Price-Agent 的「追问上限 3 次」设计）
└── 明确放弃：达上限后向用户如实报告，不假装成功
```

---

## ⑤ 为什么有效？

**核心机制：有界灵活性（Bounded Flexibility）**

```text
灵活性在模型层：模型可以任意组合工具、任意规划——这是通用性的来源
边界在 harness 层：权限、格式、恢复、上下文——这是可靠性的来源
```

模型输出天然不稳定（随机、会错、会幻觉），但 harness 把「不稳定输出」翻译成「可控行为」：格式错 → 校验拦截重试；权限越界 → 授权模型拒绝；步骤失败 → 恢复循环。**确定性由 harness 提供，灵活性由模型提供——这是 Agent 产品成立的根本原因。**

**为什么这个机制有效（算法视角）：**

1. **能力复用**：同一模型 + 不同 harness = 不同产品（SWE agent / computer-use agent / 数据分析 agent）。模型公司的模型是公用品，差异化发生在 harness 层——这解释了为什么模型公司全部亲自下场做 harness（Claude Code、Codex、Gemini CLI）：**harness 是模型公司的第二护城河**。
2. **反馈回路质量**：harness 决定模型的每一步反馈（错误信息、测试结果、文件状态）。**反馈质量决定推理质量**——模糊的错误信息让模型只能瞎猜，结构化反馈让模型快速收敛。
3. **可观测性**：harness 记录完整 transcript（输入/工具调用/输出/错误）。这是评测、归因、迭代的基础——**没有 transcript 就没有 badcase 分析**（连接你的 Evals 方法论）。
4. **迭代杠杆**：改模型能力要重训（慢、贵），改 harness 行为是产品迭代（快、便宜）。PM 的大部分改进动作发生在 harness 层。

---

## ⑥ 为什么不用别的方法？

面试高频问题：为什么 Agent 必须有 harness？替代方案逐一对比（工程视角 + 策略视角）：

| 替代方案 | 做法 | 为什么不行 |
|---------|------|-----------|
| **纯 prompt 驱动** | prompt 里写「你是 agent，输出命令」，正则解析执行 | 模型输出格式不稳定，无结构化协议；无权限控制；早期 AutoGPT 的失败模式 |
| **专用单一集成** | 每个任务写死调用链（无通用循环） | 不可复用，每次新场景重写 = 就是 Workflow 而非 Agent |
| **全模型自主** | 无 harness，模型直接操作一切 | 不可控、成本爆炸、无安全边界、上下文无限增长，真实世界不可用 |
| **轻量编排库**（LangGraph 等） | 只给循环骨架 | 权限/恢复/上下文/可观测性要开发者自己解决；灵活但生产力低 |

**Harness 胜出的原因：** 结构化工具协议（function calling 原生支持）+ 权限边界 + 恢复机制 + 可观测性——它是「有界灵活性」的正解。完整 harness（Claude Code） vs 轻量库（LangGraph）的取舍 = **控制权 vs 生产力**：产品化场景选 harness，研究/定制场景选轻量库。

**Workflow vs Agent 的连接**（连接已有笔记）：Workflow 是「固定路径 + 确定性编排」，Agent 是「自由路径 + harness 兜底」。两者不是替代关系：**Workflow 是 harness 里的特殊模式**——当任务确定性高时，用 Workflow 牺牲灵活性换稳定性；确定性低时，让模型自由发挥 + harness 兜底。

---

## ⑦ 工业界怎么做？

**Anthropic（第一梯队）：**

```text
Claude Code  = SWE harness 产品（本仓库日常使用对象）
Claude Agent SDK = 可编程 harness（Tool Runner）：把 agent loop 嵌入任意应用
               ├── 开发者自定义工具、模型、循环行为
               └── = 「harness 作为 API」——harness 本身在平台化
```

**OpenAI：** Codex（CLI harness）+ Computer Use（浏览器/GUI harness）。两家都遵循「模型公司亲自做 harness」的护城河逻辑。

**OpenClaw（开源）：** computer-use harness——GUI 操作器（鼠标/键盘/窗口）+ 视觉系统（screenshot/OCR/DOM）+ 系统工具 + API 工具。harness 的开源生态验证了「工具接入标准化」的趋势。

**MCP 生态（2024.11 至今）：** 工具接入协议事实标准——harness 通过 MCP 接任意工具，工具商通过 MCP 接入任意 harness。**harness 的竞争从「工具数量」转向「循环质量 + 权限体系 + 评测能力」。**

**你的经历连接（PM 视角）：**

- 百度物料迁移 Agent = 内部 harness + 工具集 + 业务规则（Function Calling + Schema Mapping）
- 字节的 LLM Repair = 把 LLM 当工具嵌入 Pipeline（LLM-as-Tool）——Pipeline 的 Stage 接口就是轻量 harness
- **工业界趋势判断（面试可用）：** harness 平台化（Agent OS）+ API-first（GUI 只是备份）+ harness 行为评测标准化

---

## ⑧ 和整个 AI 系统怎么连接？

**全链路位置（PM 视角）：**

```text
模型能力（大脑）→ Harness（身体+神经系统）→ 环境（世界）
     ↑                      ↑
  训练数据             Agent 行为数据（trajectory）
  （Pretrain/SFT/RL）     → 回流为 RL 训练数据
```

**知识树连接（已挂载 2026-08-05）：**

- `Harness` ← → `Agent Runtime`：harness 是 Agent Runtime 的完整工程外壳
- `Harness` ← → `LLM Brain`：产品差异的 80% 在 harness 层
- `Harness` ← → `Tool Calling / Function Calling`：工具系统是 harness 核心组件
- `Harness` ← → `Claude Code 产品功能`：权限/hooks/MCP/skills/worktree = harness 层产品决策
- `Harness` ← → `Agent 评测`：评测要区分「模型能力」vs「harness 行为」
- `Harness` ← → `RL Data`：harness 决定 rollout 轨迹 → 训练分布（新增连接方向）

**对秋招的三条应用（面试视角）：**

1. **产品面**：「如果你来定义 Agent 产品的下一版迭代，改什么？」→ 答案是 harness 层的决策：工具暴露、权限、反馈设计、上下文策略——不是 prompt 玄学
2. **数据面**：「Agent 训练数据从哪来？」→ harness 产生的轨迹数据 + 轨迹质量评测（你的 Evals 方法论直接适用）
3. **评测面**：「Agent 评测和模型评测有什么区别？」→ 模型评测测能力上限（benchmark），Agent 评测测行为（工具选择、错误恢复、权限边界）——分水岭就在 harness 层

---

**待深挖方向（面试前补齐）：**

- [ ] Claude Agent SDK 的 Tool Runner 具体 API（可编程 harness 的工程细节）
- [ ] MCP 协议细节（工具/资源/Prompt 三类能力的规范）
- [ ] harness 评测的具体案例（Anthropic evals 方法论中 harness 行为维度）
- [ ] 工业界 harness 横向对比（Claude Code vs Codex vs Cursor，功能矩阵）
