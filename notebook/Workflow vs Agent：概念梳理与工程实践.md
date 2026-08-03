本文整理自一次完整的讨论，涵盖概念辨析、工具对比、业务场景判断与三大工程实践。

---
一、Workflow 和 Agent 的核心区别
来源
这个框架主要来自 Anthropic 官方文档（"Building Effective Agents"）和 Anthropic 工程师 Barry Zhang 在 AI Engineer Summit 上的演讲，而非卡帕西。
Anthropic 的三层分类
暂时无法在飞书文档外展示此内容
一句话判断标准
"下一步做什么"，是人决定的还是模型决定的？
- 能写成 if-else 的 → Workflow
- 需要"看情况"判断的 → Agent
Workflow 的核心优势
- Token 消耗可预测，成本可控
- 行为确定性强，容易审计
- 适合流程已知、步骤固定的任务
Agent 的适用场景
- 任务模糊，无法预先穷举决策树
- 需要跨系统、跨工具的动态组合
- 任务价值足以覆盖更高的 token 成本和不确定性风险

---
二、主流工具的定位对比
工具光谱
控制流归人 ◄──────────────────────────► 控制流归模型
   n8n      Dify(workflow)   Dify(agent)   Coze(agent)   OpenClaw
  [纯流程]    [混合]           [混合]        [混合]        [纯 agent]
OpenClaw
- 定位：纯 agentic personal agent，模型控制整个 loop
- 架构：七阶段 agentic loop（消息接收 → 上下文组装 → 模型调用 → 工具执行 → 循环）
- 特点：你给目标，模型决定怎么执行；多平台消息路由（WhatsApp/Telegram/Slack 等）
- 安全风险：权限宽泛，存在 prompt injection 和数据泄露风险
Hermes（Nous Research）
- 不是 agent 平台，是一个专为结构化评估训练的模型
- 在多 agent 系统中被用作"Quality Gate"——在内容进入 Live Wiki 前做事实一致性评分和验证
- 本质是 pipeline 中的一个监督节点
Dify / n8n / Coze
暂时无法在飞书文档外展示此内容

---
三、业务场景中如何判断
案例一：AI 客服场景
场景描述：用户提问后，系统按需路由到售后 agent 或物流 agent。
用户提问
    ↓
[路由判断] ← Workflow（控制流归人，规则预定义）
    ↓           ↓
[售后 Agent] [物流 Agent] ← Agent（内部控制流归模型）
结论：这是典型的 Workflow + Agent 嵌套结构，业内称为 "Multi-Agent Workflow" 或 "Orchestrated Agents"。
- 外层路由 = Workflow（路由规则人工定义，行为确定）
- 内层执行 = Agent（每个职能 agent 自主决定调哪些工具、追问还是直接回复）
工程建议：
- 如果某个"内层 agent"每次都按相同步骤执行，应直接改成确定性的 workflow 节点
- 只在真正需要模型自主判断的地方用 agent，其余用 workflow 包裹住
案例二：内容营销自动化
纯 Workflow 版本（流程固定）：
新品信息录入 → 写小红书文案 → 写微信推文 → 写产品描述 → 同时发布
引入 Agent 版本（需要策略判断）：
新品信息录入
    ↓
[内容策略 Agent]
模型自主决定：目标用户是谁？要做哪些渠道？
每个渠道用什么风格？要不要生成 KOL briefing？
    ↓
[小红书 Workflow] [抖音 Workflow] [微博 Workflow]
（各渠道内部执行步骤确定，用 workflow）
    ↓
[效果监控 Agent]（发布后自主判断是否调整策略）
规律：
- 策略层（"做什么、怎么做"）→ Agent
- 执行层（"写文案、排版、发布"）→ Workflow

---
四、三大工程实践
1. Prompt Engineering
定义：控制模型在单次调用中的输出质量和格式。
Workflow 中的应用
- 每个节点职责单一，prompt 可以写得非常精准
- 输出格式完全可控（强制 JSON、强制特定字段）
- 示例：意图识别节点只返回类别名称，不允许解释
# 好的路由 prompt
你是客服路由系统。判断用户消息属于以下哪个类别，
只返回类别名称，不要解释：
- 售后退换货 / 物流查询 / 产品咨询 / 投诉建议 / 其他
用户消息：{input}
Agent 中的应用
- System prompt 承担更重的责任：定义边界、决策风格、异常处理逻辑
- 需要明确：agent 能做什么、不能做什么、模糊情况怎么处理
- Prompt 写得不好，行为会漂移，且难以追踪根因

---
2. Context Engineering
定义：控制每次 LLM 调用时，context window 里放什么信息、放多少、怎么组织。
Workflow 中的应用
- 核心问题：信息如何在节点间传递
- 原则：每个节点只给它需要的信息，不多也不少
- 示例：意图识别节点传给物流查询节点时，要不要带原始用户消息？
Agent 中的应用（挑战更大）
Context 随 loop 膨胀问题：
第1轮：2,000 tokens
第3轮：5,000 tokens（加入了工具调用结果）
第8轮：18,000 tokens（充满中间步骤噪音）
四个关键工程点：
暂时无法在飞书文档外展示此内容

---
3. Harness Engineering
定义：为 agent/workflow 搭建外部的约束、评测、反馈基础设施。让模型行为可测量、可控制、可审计。
没有 harness 的 agent = 黑盒。每次改 prompt 都不知道是变好还是变坏。
Workflow 中的应用
节点级自动 QA：
节点：生成退款回复
↓
Harness 检查：
  - 是否包含订单号？
  - 是否包含退款金额？
  - 是否包含处理时间承诺？
  - 情感倾向是否正向安抚？
↓
不通过 → 重新生成 或 触发人工审核
Agent 中的应用（最关键）
三个核心组件：
① 行为边界约束
售后 agent 调用"发起退款"工具前
Harness 检查：退款金额是否超限？订单状态是否允许？是否需要二次确认？
② 轨迹可观测性
记录 agent 每一步的决策链：调用了什么工具、用了什么参数、返回了什么、然后决定做什么。
- 没有轨迹记录 → 出问题无法排查根因
③ 自动化 Eval（最核心）
以客服 agent 为例：
跑 1000 条历史真实对话，自动检查：
  - 问题解决率
  - 工具调用准确率
  - 升级人工率
  - 平均 token 消耗
这是卡帕西 autoresearch 能跑 700 个实验的核心原因——有明确的自动评测指标，不需要人来判断每次实验好坏。

---
五、综合对比
三大工程 × 两种架构
暂时无法在飞书文档外展示此内容
建设顺序建议
1. Prompt Engineering  →  先让每个节点/agent 能用
2. Context Engineering →  优化信息质量，降低 token 消耗
3. Harness Engineering →  建立评测体系，让迭代有据可依

---
六、一句话总结每个核心概念
- Workflow vs Agent：控制流归人 vs 控制流归模型
- 判断标准：能写成 if-else 的用 workflow，需要"看情况"的用 agent
- 最佳实践：workflow 包裹 agent，把不确定性限制在最小范围
- Prompt Engineering：控制单次输出质量
- Context Engineering：控制模型"看到什么"
- Harness Engineering：控制系统"是否在做对的事"