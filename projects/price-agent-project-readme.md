# Price Agent — 电商领域 AI 搜索助手

基于 **ReAct + Plan-Execute 混合策略**的 LLM Agent，支持文本查询和图片识物两种入口，在京东、淘宝、拼多多、苏宁 4 个电商平台并行搜索，完成商品搜索与购买推荐指导，具备**语义推荐**、**引导式购物**、**RAG 知识增强**能力。

> 当前为 mock 数据验证版本。架构上预留了 DataSource 抽象层，验证通过后可替换为真实电商数据源。

## 核心架构

```
用户输入（文本 / 图片）
        │
        ▼
┌─────────────────────────────────────────────────┐
│              ReActAgent 引擎                      │
│                                                  │
│  _detect_intent() → 意图分类                       │
│       │              │              │             │
│       ▼              ▼              ▼             │
│  recommendation  comparison    shopping           │
│  (语义推荐)     (Plan-Execute) (引导式购物)          │
│       │              │              │             │
│       ▼              ▼              ▼             │
│  _react_loop   _plan_and_     _guided_shopping    │
│  +intent_hint  execute()      + ShoppingContext   │
│       │         Phase 1: Plan       │             │
│       │         Phase 2: mini-ReAct │             │
│       │         Phase 3: Synthesize │             │
│       │              │              │             │
│       └──────┬───────┴──────┬───────┘             │
│              ▼              ▼                     │
│     Self-Reflection  Sliding Window               │
│     多模型路由                                      │
└──────────────┬───────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│                6 个工具                           │
│  - multi_platform_comparison                      │
│  - query_single_platform                          │
│  - get_all_platform_products                      │
│  - search_product_by_image                        │
│  - semantic_product_search  （向量+规则混合召回）    │
│  - search_product_knowledge  （RAG 知识检索）      │
└──────────────┬───────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│          PlatformParallelAgent                   │
│  ThreadPoolExecutor (4 workers)                  │
│  京东 │ 淘宝 │ 拼多多 │ 苏宁                        │
└──────────────────────────────────────────────────┘
```

## 四种执行模式

| | ReAct | Plan-Execute | 语义推荐  | 引导式购物 |
|---|---|---|---|---|
| **场景** | 单商品比价 | 多商品对比、混合意图 | 场景/预算/处理器推荐 | 模糊需求、无明确型号 |
| **触发** | 默认兜底 | 多商品 / 对比词 | 场景词/预算词/处理器词 | "想买个手机""帮我挑" |
| **策略** | ReAct 循环 | Plan → Execute → Synthesize | ReAct + 向量召回 | ShoppingContext 状态机 |
| **特点** | 灵活 | 并行 + 依赖编排 | 语义相似度容错 | 槽位填充 + 主动引导 |

## 模块完成状态

| 模块 | 说明 | 状态 |
|------|------|:--:|
| M1: 行业配置框架 | Config Schema + 手机品类配置 + 注入通道 | ✅ |
| M2: 语义召回升级 | 向量召回 + 规则过滤混合检索，2048 维 embedding | ✅ |
| M3: RAG 知识库 | BM25 + 语义混合检索，手机领域知识增强 | ✅ |
| M4: 生成式推荐 | LLM 意图分解 + Rerank + 推荐解释（计划中） | 📋 |
| M5: 引导式购物 Agent | ShoppingContext 状态机 + 槽位填充 + 多轮购物 | ✅ |
| M6: Trace 数据处理工坊 | trace → SFT 训练数据集构建 + 质量评分 + LLM-Judge + 人工审核 | ✅ |
| **推理可视化** | TraceEvent 结构化事件 + SSE 流式 + 模式可视化 + 调试仪表盘 | ✅ |

## 功能特性

### 核心能力
- **ReAct 推理闭环**：Thought → Action → Observation → Final Answer
- **Plan-Execute 策略**：Phase 1 生成 JSON 计划 → Phase 2 每 Step 独立 mini-ReAct → Phase 3 综合回答
- **意图分类路由**：自动识别 4 种意图（推荐/查价/对比/购物），路由到最优执行模式
- **Skills 按需加载**：5 个 SKILL.md 技能模块，LLM 通过 `load_skill` 元工具自主选择，用户 `/skill-name` 显式调用
- **自反思纠错**：工具返回空结果时自动注入反思提示，引导重试或追问
- **多模型路由**：文本模型 DeepSeek V4 Flash，视觉模型豆包，Embedding 豆包
- **滑动窗口上下文**：保留最近 6 轮对话，理解"那小米14呢"等上下文指代

### 语义召回（M2）
- **向量+规则混合检索**：doubao-embedding-vision-251215（2048 维），语义相似度容错
- **商品 Embedding 预热**：启动时计算并持久化到 `embeddings_cache.pkl`，后续启动仅增量更新新增/变更商品（↓74% API 调用）
- **MD5 指纹检测**：按 `build_product_text` 输出计算指纹，自动识别商品内容变更
- **功能开关**：`enable_vector_recall` 控制，关闭回退纯规则

### RAG 知识增强（M3）
- **BM25 + 语义混合检索**：alpha=0.7 语义为主，BM25 为辅，两路归一化融合
- **## 标题分块**：Markdown 文档按二级标题切分，携带 source/section 元数据
- **知识类型过滤**：chipset_compare / phone_review / spec_lookup / auto
- **真实场景规划**：文档中包含四层内容运营平台演进方案（摄入/加工/索引/监控）

### 引导式购物（M5）
- **ShoppingContext 状态机**：GREETING → SLOT_FILLING → SEARCHING → RECOMMENDING → FOLLOW_UP
- **槽位填充**：5 个槽位（场景/预算/品牌/处理器/屏幕），必填优先，最多追问 3 次
- **对比模式**：多款商品按维度（性能/拍照/续航/价格/屏幕）逐项对比

### 推理可视化（L1-L4）
- **结构化 Trace 事件**：17 种事件类型（intent/mode_select/react_round/tool_call/tool_result/reflection/plan_start/plan_generated/step_start/step_end/synthesize_start/synthesize_end/shopping_phase/slot_filled/skill_load/error/done），替代 print() 驱动
- **SSE 实时流式传输**：`/api/chat/stream` 端点，前端 ReadableStream 消费，推理步骤逐个实时出现
- **模式特定可视化**：
  - M5 购物状态机：6 阶段横向进度条 + 槽位填充 chip
  - Plan-Execute DAG：并行/串行分组 + 步骤状态 pending→running→done/error（pulse 动画）
  - 时间瀑布：步骤耗时水平条形图
  - 模型路由徽章：节点标题行内显示模型名称
- **调试仪表盘**：Trace 自动保存 → 列表（按会话过滤）→ 逐步骤回放（速度 0.5x-5x）→ 性能摘要

### Trace 数据处理工坊（M6）
- **独立页面**：`/training-data`，4 步向导式处理链路
- **Trace 列表**：分页表格（50条/页）+ 按意图/模式/工具数筛选 + 点击展开详情
- **格式提取**：Trace → OpenAI SFT fine-tuning JSONL，左右对比视图 + 在线编辑
- **质量评分**：4 维度启发式评分（能力展现/执行质量/回答可信度/数据完整度，每项 0–10 分），与 LLM-as-Judge 评分尺度一致，便于交叉校验
- **LLM-as-Judge**：调用 DeepSeek 从 4 维度（能力展现/执行质量/回答可信度/数据完整度）+ 幻觉检测评估样本质量
- **完整数据采集**：Agent 运行后自动保存完整 messages（含 tool call 参数和 tool response 全文），替代早期事件摘要截断，训练数据质量显著提升
- **人工审核**：卡片式审核列表 + ✓通过/✗拒绝 + 按状态筛选 + 批量操作
- **JSONL 导出**：符合 OpenAI Chat Completions fine-tuning 格式，可对接 HuggingFace TRL / Unsloth
- **处理规模**：188 条 Trace → ~52 条高价值训练样本（≥70分）

### Skills 架构（Prompt 按需组合）
- **SKILL.md 驱动**：5 个技能模块（比价/图片搜索/语义推荐/RAG 知识/购物引导），YAML frontmatter + markdown 定义
- **LLM 自主选择**：`load_skill` 元工具让 LLM 根据用户意图自行决定加载哪个技能
- **用户显式调用**：支持 `/price_comparison` 等 Skill 前缀直接调用
- **上下文持久化**：加载后的 Skill 内容跨 ReAct 轮次持久保留
- **Token 优化**：Catalog 仅 253 chars（vs 原 5,825 chars SYSTEM_PROMPT），单场景节省 74-80%
- **零代码扩展**：新增 Skill 只需添加一个 .md 文件

### IT3C 手机品类
- **17 个商品字段**：brand、processor、processor_brand、performance_tier、screen_size、battery、use_case_tags、description
- **处理器归一化**：骁龙→sd、天玑→mt、A 系列→apple、麒麟→kirin
- **场景标签**：gaming / photography / battery / business / student / budget / flagship

## 技术栈

- **LLM**：DeepSeek V4 Flash（文本）+ 火山引擎 ARK（视觉 + Embedding）
- **Embedding**：doubao-embedding-vision-251215（2048 维）
- **向量检索**：numpy 内存 + BM25 混合（mock 期）→ ChromaDB（生产期）
- **RAG**：自研 KnowledgeIndexer + KnowledgeRetriever + rank-bm25
- **框架**：Flask + SQLite
- **测试**：P0-P6 + IT3C + M1-M5 专项，150+ 测试用例

## 快速开始

```bash
pip install -r requirements.txt
cp .env.example .env   # 填入 API Key
python app.py
```

### 环境变量

```bash
# DeepSeek（文本模型）
DEEPSEEK_API_KEY=your_key
DEEPSEEK_MODEL=deepseek-v4-flash

# 火山引擎 ARK（视觉 + Embedding）
ARK_API_KEY=your_key
ARK_VISION_MODEL=doubao-seed-2-0-pro-260215
ARK_EMBEDDING_MODEL=doubao-embedding-vision-251215
```

## 项目结构

```
price-agent/
  app.py                   ← Flask Web 入口（API + SSE 流式）
  main.py                  ← 命令行 REPL 入口
  db_manager.py            ← 数据库管理工具（终端菜单）
  agent/
    react_engine.py        ← ReActAgent + ShoppingContext（M5）+ Skills 架构
    trace.py               ← TraceEvent 结构化事件系统（L1-L2）
    prompts.py             ← 公共 Prompt 片段（COMMON_RULES/FORMAT/ERROR）
    skills/
      loader.py            ← SkillLoader：SKILL.md 解析 + Catalog 生成
      price_comparison.md  ← 比价 Skill（4 个 few-shot）
      vision_search.md     ← 图片搜索 Skill
      semantic_recommend.md ← 语义推荐 Skill（3 个 few-shot）
      rag_knowledge.md     ← RAG 知识检索 Skill
      shopping_guide.md    ← 购物引导 Skill
  config/
    settings.py            ← 配置管理 + 多模型路由 + Embedding
    embedding.py           ← EmbeddingClient（doubao-embedding）
    industry_loader.py     ← 行业 Config 动态加载器（M1）
    industries/mobile.py   ← 手机品类配置（M1）
  tools/
    semantic_search_tool.py ← 语义推荐 + 向量召回（M2）
    rag_tool.py            ← RAG 知识检索工具（M3）
    knowledge_indexer.py   ← 知识索引 + BM25 混合检索（M3）
    multi_platform_tools.py ← 多平台比价工具
    image_search_tools.py  ← 图片搜索工具
    registry.py            ← 工具注册器
  platforms/
    parallel_agent.py      ← 并行查询 + Embedding 预热（M2）
    platform_database.py   ← 平台数据库（17 字段 Schema）
  knowledge/mobile/        ← 手机领域知识库（M3）
    processors/            ← 芯片对比文档
    reviews/               ← 机型评测文档
  scripts/
    training_data.py       ← M6 Trace 数据处理 + 质量评分 + LLM-Judge（~680行）
  tests/
    test_trace.py          ← L1/L2 结构化事件 + SSE 流式测试（72 用例）
    conftest.py            ← pytest fixtures（client/indexer/retriever/agent）
    test_m1_config.py      ← M1 配置测试
    test_m2_recall.py      ← M2 召回测试
    test_m3_rag.py         ← M3 RAG 测试
    test_m5_shopping.py    ← M5 购物测试
    test_react_engine.py   ← ReActEngine 核心测试
  eval/                    ← 评估框架（P0-P6 + IT3C 回归套件）
    results/traces/        ← L4 自动保存的 trace 文件（~188条）
  templates/
    training.html          ← M6 Trace 数据处理工坊页面
  static/js/
    training.js            ← M6 工坊前端交互逻辑（~630行）
  abtest-demo/
    app.py                 ← 独立 A/B 测试实验分析仪表盘
    tools/                 ← 8 个 A/B 测试专用工具
    skills/                ← abtest_analysis.md
  docs/modules/            ← 模块详细设计文档
  docs/trace-data-processing-plan.md  ← M6 完整方案文档
```

## 文档

- [总规划](roadmap.md) — 能力现状、架构总览、可扩展方向、待办事项
- [模块设计](docs/modules/) — M0-M6 各模块详细设计文档
  - [00-基础设施评估](docs/modules/00-基础设施评估.md) | [01-行业配置框架](docs/modules/01-行业配置框架.md)
  - [02-语义召回升级](docs/modules/02-语义召回升级.md) | [03-RAG知识库](docs/modules/03-RAG知识库.md)
  - [04-生成式推荐](docs/modules/04-生成式推荐.md) | [05-引导式购物Agent](docs/modules/05-引导式购物Agent.md)
  - [06-LLM-as-Judge质量评估](docs/modules/06-LLM-as-Judge质量评估.md)
- [Skills 架构方案](docs/skills-architecture-plan.md)
- [Plan-Execute 方案](docs/plan-execute-方案.md)
- [推理可视化方案](docs/reasoning-visualization-plan.md)
- [Trace 数据处理方案](docs/trace-data-processing-plan.md)
- [评估体系规划](docs/评估体系规划.md) | [测试用例手册](docs/测试用例手册.md)
- [多平台架构说明](docs/MULTI_PLATFORM_README.md)
- [项目复盘](docs/项目复盘文档.md) | [IT3C 复盘](docs/IT3C问题复盘-产品视角.md)

---

## Technical Anatomy（八层解剖）

> 按 CLAUDE.md 项目文档规范补充。主题从真实实现中抽取，每个主题覆盖八层 + 面试视角追问。
> 标准：面到这个话题，能讲 5 分钟。

### 主题 1：意图路由 —— 四种执行模式的前提

```text
① 它是什么
   用户输入 → _detect_intent() 关键词规则引擎 → 判定四类意图之一（推荐/查价/对比/购物）
   → 路由到四种执行模式之一（语义推荐 / ReAct / Plan-Execute / 引导式购物）

② 为什么出现
   用户买手机的决策状态天然分四种：目标明确（查价）、犹豫对比（多品）、
   有方向没目标（推荐）、完全没方向（购物）。四种状态的执行路径差异显著：
   查价=一次并行检索；对比=多步骤依赖编排；推荐=语义召回；购物=多轮引导。
   单一模式要么慢要么不准，所以按状态路由到最优路径。

③ 数学原理
   无模型，是确定性决策：关键词 + 正则匹配，约 60 行代码，构成三层决策树：
   有购物词 + 无型号 + 无场景 → shopping
   有场景词/预算词/推荐词 → recommendation
   多商品 + 对比词 → comparison
   其余 → query 兜底
   本质是"用代码的确定性换取 LLM 的不确定性"——显式路由的 trade-off。

④ 工程实现
   路由保护：购物状态机激活后，run() 入口跳过意图分类直接进 _guided_shopping
   （否则"打游戏"会被误判为 recommendation，购物上下文丢失——线上 bug 修复而来）
   话题切换 > 结束检测：购物途中"算了帮我查 iPhone 15" 按话题切换处理
   候选内型号不算切换：推荐列表里的机型追问属于对比，不是退出

⑤ 为什么有效
   意图分类错误的代价极高：模式选错 = 走完全错误的交互路径，用户困惑 + 信任丧失。
   规则引擎 100% 确定、0 token、0 毫秒延迟、改一行代码立即可验证。

⑥ 为什么不用别的方法
   方案 A：LLM 意图分类 → 拒绝。每次多一次 API 调用（+200ms 延迟 + 成本），
   且 95% 确定性不可接受——"想买个手机"必须每次都进购物模式。
   方案 B：全交给 LLM 自主判断（通用模式）→ 拒绝。不可靠的决策者完成不容出错的任务，
   模式选错 → 工具选错 → 回答偏离，不确定性层层放大。

⑦ 工业界怎么做
   生产 Agent 普遍采用两级路由：规则粗筛（覆盖高频确定场景）+ LLM 语义分类兜底
   （覆盖长尾表达、多意图混合），LLM 兜底 case 定期 Review 沉淀回规则层——数据飞轮。
   LangChain 的 Router、多 Agent 架构的意图分流与此同构。

⑧ 与 AI 系统连接
   Agent Runtime 的决策层（选模式）→ Tool Calling 的前置（选工具集）
   → Skills 预加载（按意图注入对应 SKILL.md）→ 与 CoT 质检的 Cascading Classification 同构

面试视角追问：
├── 【算法】意图分类准确率是系统瓶颈指标，当前未量化留存（待补）
├── 【工程】关键词库维护成本随品类扩展线性增长，长尾表达覆盖不全
└── 【策略】引入 LLM 兜底的拐点：每周维护关键词 > 2 小时 / 长尾占比 > 10%
```

### 主题 2：Plan-Execute 编排 —— DAG 并行调度

```text
① 它是什么
   多商品对比的执行模式：Phase 1 生成 JSON 执行计划 → Phase 2 按 DAG 执行 → Phase 3 综合回答

② 为什么出现
   对比场景若走 ReAct：三步串行（查A→查B→对比），用户等待时间累加；
   且 LLM "边走边想"可能查完 A 就输出结论（线上真实问题：LLM 误判 complexity=simple
   回退 ReAct → 只查一个商品就下结论）。Plan-Execute 逼迫 LLM 动手前先想清楚全局。

③ 数学原理
   计划的本质是有向无环图（DAG）：每个 Step 声明 depends_on 字段引用前置步骤。
   无依赖步骤 → 并行组（等待时间 = max，而非累加）；有依赖 → 串行组（拓扑序）。
   并行度收益：3 步任务从 T1+T2+T3 变为 max(T1,T2)+T3。

④ 工程实现
   Phase 1：LLM 输出 JSON 计划，depends_on 声明依赖，complexity 字段兜底（simple 回退 ReAct）
   Phase 2：每个 Step 内部是 mini-ReAct 循环（自反思纠错），ThreadPoolExecutor 并行执行无依赖步骤
   Phase 3：专用 model_synthesize 综合回答
   前端 DAG 可视化：并行节点 CSS Grid 自动分列，串行节点 Flex 纵向堆叠

⑤ 为什么有效
   计划编排与工具执行解耦：代码不做任何领域假设，并行/串行决策权交给 LLM 语义理解，
   换领域自然理解该领域依赖关系。用户等待从"累加"变"取最长"。

⑥ 为什么不用别的方法
   方案 A：纯 ReAct 硬跑对比 → 拒绝。串行慢 + 可能提前输出结论。
   方案 B：代码硬编码步骤顺序 → 拒绝。领域假设写死，换品类不可复用。
   Plan-Execute 是"逼迫先规划"的中间态，且保留 complexity 兜底避免过度设计。

⑦ 工业界怎么做
   OpenAI AgentKit、LangGraph 的 plan-and-execute 模式；MetaGPT 的多 Agent 规划。
   与 Kubernetes 的 DAG 调度、数据 Pipeline 的依赖编排思想同构。

⑧ 与 AI 系统连接
   Agentic Loop（Plan-Execute 是 ReAct 之上的编排层）→ Evaluation（P2 端到端验证）
   → 推理可视化（TraceEvent 记录 plan_start/step_start/step_end）

面试视角追问：
├── 【算法】并行度的收益怎么量化？Step 失败如何影响整体结论？
├── 【工程】LLM 生成的计划格式错误（非法 JSON）怎么兜底？
└── 【策略】"让 LLM 决定并行/串行"和"代码硬编码"的分界线在哪？
```

### 主题 3：语义召回（M2）—— 向量 + 规则混合检索

```text
① 它是什么
   semantic_product_search 工具：向量召回 + 规则过滤的混合检索，服务推荐型 query

② 为什么出现
   模糊需求（"5000 以内拍照好的游戏手机"）无型号可匹配，数据库里可能不存在包含
   "拍照好的游戏手机"字面的商品。关键词精确匹配召回为 0，必须语义相似度容错。

③ 数学原理
   商品文本 → doubao-embedding-vision-251215（2048 维）→ 余弦相似度匹配。
   混合检索：向量召回（语义相关）+ 规则过滤（预算/品牌/处理器硬约束——
   语义相近不能推荐超预算商品）。α=0.7 是 RAG 中 BM25 与语义两路归一化融合的权重。

④ 工程实现
   Embedding 预热：启动时全量计算并持久化 embeddings_cache.pkl，
   后续启动按 MD5 指纹（build_product_text 输出）检测变更，仅增量更新 → API 调用 ↓74%
   功能开关 enable_vector_recall：关闭回退纯规则，策略可无缝降级
   存储：numpy 内存（mock 期）→ ChromaDB（生产期）

⑤ 为什么有效
   "语义理解 + 硬约束过滤"是 Agent 从"查到"到"查对"的关键：
   召回靠向量（宽），保真靠规则（严），两者互补。

⑥ 为什么不用别的方法
   方案 A：纯关键词 → 召回为 0，方案 B：纯向量 → 可能推荐超预算/跨品牌商品。
   混合检索是行业标准答案（与 RAG 的 BM25+Dense 融合同理）。

⑦ 工业界怎么做
   电商搜索的召回-精排结构（向量召回 + 规则/模型精排）；
   Embedding 预热的工程手法与向量数据库的增量索引思想一致。

⑧ 与 AI 系统连接
   Data / 向量化 Pipeline（预处理 → embedding → 存储 → 增量更新）
   → Decision（推荐排序）→ 与 CoT 质检 Pipeline 的幂等/增量设计同构

面试视角追问：
├── 【工程】embedding 模型换版本，缓存怎么处理？MD5 指纹的粒度？
├── 【策略】α=0.7 有做扫描曲线吗？单点结论的敏感性未知（待补）
└── 【算法】召回质量的评测指标？（Recall@K / 排序相关性）
```

### 主题 4：引导式购物状态机（M5）—— 200 行代码 vs LangGraph

```text
① 它是什么
   shopping 模式的执行引擎：6 状态状态机（GREETING → SLOT_FILLING → SEARCHING
   → RECOMMENDING → COMPARING → FOLLOW_UP），槽位填充 + 主动引导

② 为什么出现
   "想买个手机"没有任何结构化信息。朴素 ReAct 会乱搜。
   需要一轮一轮收集需求（5 个槽位：场景/预算/品牌/处理器/屏幕），收敛后搜索。

③ 数学原理
   状态机 + 槽位填充（slot-filling）：每个状态只做一件事，出口条件明确。
   追问上限 3 次（需求收敛 vs 体验损耗的平衡），只统计有效槽位提取
   （用户闲聊"今天天气不错"不计入追问次数——惩罚用户的无意行为不合理）。

④ 工程实现
   ShoppingContext dataclass：ctx.phase 存状态，ctx.slots 存槽位，不依赖历史消息
   约 200 行代码。路由保护：激活后 run() 跳过意图分类。
   边界处理三坑（每个坑沉淀一个 test case）：
   ├── 话题切换 > 结束检测（"算了帮我查 iPhone 15"）
   ├── 无关输入不消耗追问次数
   └── 路由不被意图分类覆盖（"打游戏"在购物上下文中是槽位，不是推荐意图）

⑤ 为什么有效
   对话状态由代码管理而非 LLM 从历史中理解：可测试、可调试、可修改。
   "规则负责控制流，LLM 负责语义判断"——两者解耦。

⑥ 为什么不用别的方法
   方案 A：LangGraph → 拒绝。场景状态分支明确，200 行代码比 10 万行框架更可控；
   Trace 事件需要精确控制状态颗粒度；避免框架 API 变动维护成本。
   方案 B：纯 prompt 约束 LLM 引导 → 拒绝。状态不可测试、不可回放。
   "场景越垂直、需求越定制，框架的收益越低"。

⑦ 工业界怎么做
   客服机器人/保险理赔引导的经典状态机 + 槽位设计；
   Dialogflow / Rasa 的 forms 机制与此同构（Rasa 也是自研小型状态机思路）。

⑧ 与 AI 系统连接
   Agentic Loop（状态机是 ReAct 之外的另一类控制流）→ M6 Trace 记录 shopping_phase
   → Evaluation（P3 边界 + M5 专项测试）

面试视角追问：
├── 【PM】为什么是 5 个槽位？必填/可选怎么定义？
├── 【算法】追问上限 3 次有数据支撑吗？还是经验值？
└── 【策略】"多轮对话不等于把历史拼接进 prompt"——状态机 vs 上下文注入的分工
```

### 主题 5：分层评测体系 —— tests/ 与 eval/ 两层防线

```text
① 它是什么
   两层评测架构：tests/（模块级、秒级反馈、不依赖 LLM）+ eval/（Agent 级、分钟级、需 LLM）

② 为什么出现
   传统软件测试"输入 A 断言输出 B"在 Agent 上失效：LLM 非确定性（同输入不同措辞/
   不同工具顺序）、状态空间爆炸（6 状态 × 每状态 5+ 输入类型）、"对"的定义难
   （价格对错需要 Ground Truth，人工标注成本高且电商价格实时变）。

③ 数学原理
   Ground Truth 不靠人工标注：直接从 SQLite 计算——compute_cheapest() 查 MIN(price)，
   Agent 回答中提取价格数字比对，容差内算对；幻觉检测 detect_hallucination()
   提取 ≥2000 的价格数字与 Ground Truth 交叉比对（5% 容差），是自动化硬指标。

④ 工程实现
   eval/ 由 run.py 编排 9 个阶段，按依赖层级组织：
   ├── P0 单元（无 LLM，1 秒出结果：DB CRUD/评分逻辑/自反思消息，43+ case）
   ├── P1 属性提取（单次 LLM：商品名/颜色/内存解析，17 case）
   ├── P2 端到端（多轮 LLM：ReAct/Plan-Execute 完整循环 + 幻觉检测，17 case）
   ├── P3 能力边界（不存在商品/歧义/空输入/矛盾需求，15 case）
   ├── P4 汇总基准（同 session 聚合，7 维度指标报告）
   ├── P5 优化验证（自反思/System Prompt 质量，13 case）
   ├── P6 图片识物（10+ case）
   └── IT3C 行业回归（51+ case）
   Session 机制：每次运行生成 session ID，P4 聚合同 session 报告，不同 run 横向对比
   （"这次 PR 改了意图路由，P2 通过率从 100% 降到 94% → 排查"）
   全量：P0-P6 + IT3C + M1-M5 专项，150+ 测试用例

⑤ 为什么有效
   分层隔离故障域（P0 挂 → 问题在解析层，P2 挂 → 需端到端排查）；
   分层控制成本（改什么验证什么，发版才跑全套）；
   让开发者愿意频繁跑测试 → 问题不累积。

⑥ 为什么不用别的方法
   方案 A：全放一个框架 → 拒绝。每次改代码要等 5 分钟 + API 费用。
   方案 B：单一通过率指标 → 拒绝。掩盖问题（P2 100% 但 P1 88%，
   问题在 LLM 参数解析能力）。7 维度拆分才能精准定位。

⑦ 工业界怎么做
   与"单元测试 → 集成测试 → E2E"同构；LLM 应用的 evals（OpenAI Evals、
   LangSmith）分层思想；AI Agent 评测是当前行业前沿（与字节 Eval Set 建设直接相关）。

⑧ 与 AI 系统连接
   Evaluation 主干节点 ← 与 CoT 质检 5 层 Gate 同构（多层级联分类）
   → M6 评分体系（4 维度启发式评分与 LLM-as-Judge 尺度一致）→ 数据驱动迭代闭环

面试视角追问：
├── 【算法】166 个可评分 eval case 综合通过率 94.6%——失败 case 的分布与归因？
├── 【工程】评测的统计显著性？样本量与置信区间？
└── 【策略】评测结论驱动了哪些具体迭代？（M5 三个坑 → 3 个 case）
```

### 主题 6：Trace → SFT 数据工坊（M6）—— Agent 训练数据的闭环

```text
① 它是什么
   /training-data 页面：Agent 运行的 Trace 轨迹 → 质量评分 → 人工审核 → 导出
   OpenAI SFT fine-tuning JSONL（可对接 HuggingFace TRL / Unsloth）

② 为什么出现
   Agent 系统的运行轨迹本身就是最真实、最稀缺的训练数据（比人工编写/蒸馏都真实）。
   "生产日志回流"是 SFT 数据构建质量最高的来源。188 条 Trace 里只有高价值部分值得训练。

③ 数学原理
   质量评分：4 维度启发式评分（能力展现/执行质量/回答可信度/数据完整度，每项 0-10 分），
   与 LLM-as-Judge 评分尺度一致 → 可交叉校验。
   数据筛选漏斗：188 条 Trace → ~52 条高价值样本（≥70 分），约 28% 留存率。

④ 工程实现
   完整数据采集：Agent 运行后自动保存完整 messages（含 tool call 参数和 tool response
   全文），替代早期事件摘要截断 → 训练数据质量显著提升
   评分链路：启发式评分 + LLM-as-Judge（4 维度 + 幻觉检测）→ 人工审核（✓/✗ + 筛选）
   → JSONL 导出（OpenAI Chat Completions fine-tuning 格式）

⑤ 为什么有效
   Trace 结构化（17 种事件类型）→ 既服务推理可视化（可观测性），又天然可转训练数据
   （同一份数据两种用途）。质量筛选保证"好数据"而非"多数据"。

⑥ 为什么不用别的方法
   方案 A：人工编写 SFT 数据 → 贵、慢、不够真实。
   方案 B：模型蒸馏（GPT-4 跑 case）→ 性价比高但域内真实性不如生产轨迹。
   生产轨迹回流是唯一"零额外成本 + 最真实"的来源，代价是需清洗筛选（PII、低质量）。

⑦ 工业界怎么做
   与预训练/SFT 数据生产的"高质量轨迹沉淀"思路一致；Agent 产品（Claude Code 等）
   的"clawback/优质会话样本回流"同构；这是 Agent 数据 PM 岗位的核心工作。

⑧ 与 AI 系统连接
   Data / SFT 数据生产 → Evaluation（评分即评测）→ 可观测性（Trace）→ 训练数据回流
   直接对应字节岗位 JD 的"数据生产管线 + 评测体系"双能力

面试视角追问：
├── 【算法】启发式评分 4 维度权重怎么定？LLM-as-Judge 的可靠性怎么验证？
├── 【工程】PII/敏感数据处理？trace 去重？幂等？
└── 【策略】188→52 的筛选漏斗损失了什么？被丢弃的 trace 有分析价值吗（错误模式）？
```

---

## 四视角展开

### PM 视角

```text
├── 四种用户状态 → 四种执行模式：从用户真实决策路径反推产品架构
│   （目标明确 → ReAct / 犹豫对比 → Plan-Execute / 有方向没目标 → 语义推荐 /
│    完全没方向 → 引导式购物）
├── 引导式购物：不知道买什么的用户靠 5 槽位逐轮收敛，"让系统承担复杂度，不让用户承担"
├── 边界场景兜底：品牌别名改写、商品不存在、置信度低、追问上限
├── Skills 按需加载的产品逻辑：系统预判（90%+ 无感）→ Agent 自主补课 → 用户显式指定，
│   对应"好产品不需要用户学习"+"聪明助手会自己查资料"+"给高级用户快捷键"
└── 演示驱动设计：Trace 可视化让 Agent 的思考过程可演示、可讲解、可复盘
```

### 算法视角

```text
├── 意图分类准确率是系统瓶颈指标（当前未量化留存，待补）
├── 混合检索 α=0.7（RAG 中 BM25 与语义融合权重，语义为主）
├── 幻觉检测硬指标：价格数字提取 + Ground Truth 交叉比对（5% 容差）
├── 4 维度启发式评分（能力展现/执行质量/回答可信度/数据完整度）
├── LLM-as-Judge：4 维度 + 幻觉检测的样本质量评估
└── 分层评测通过率（P0 97.7% / P2 88.2%，失败集中在 LLM 不稳定环节：属性提取、端到端判断）
```

### 工程视角

```text
├── 多平台并行：ThreadPoolExecutor（4 workers），一次工具调用并行打 4 平台
├── Embedding 预热 + MD5 指纹增量更新：API 调用 ↓74%
├── 功能开关（enable_vector_recall）：策略无缝降级，不阻断主流程
├── 滑动窗口上下文：最近 6 轮 + 字符数双重截断
├── Trace 事件流（17 种类型）→ SSE 流式推送 → DAG 可视化 + 调试仪表盘回放
├── 幂等与容错：工具失败不抛 traceback，结构化错误返回；自反思重试
├── 多模型路由：DeepSeek V4 Flash（文本循环）+ 豆包（视觉）+ 豆包（Embedding）——
│   不要让最强模型做 SQL，也不要让最便宜模型做策略判断
└── 测试分层：tests/ 秒级 + eval/ 分钟级，改什么验证什么
```

### 策略视角

```text
├── 评估驱动迭代闭环：M5 三个线上坑 → 3 个 test case，"坑踩一个 case 加一个"
├── Ground Truth 自动计算（SQL 直查）→ 零人工标注的评测可行性
├── Session + 基准报告：不同 run 横向对比，改动回归可量化
├── Trace → SFT 数据漏斗（188 → 52 条）：训练数据的质量筛选策略
├── 追问上限 3 次：需求收敛 vs 体验损耗的平衡决策
└── 两级路由规划：规则覆盖高频，LLM 兜底长尾，case 回流形成数据飞轮
```

---

## 面试故事（30 秒 / 2 分钟 / 5 分钟）

### 版本 A（30 秒）

> 我独立设计并实现了 Price Agent——电商领域 AI 搜索助手。核心是意图路由 + 四种执行模式（ReAct / Plan-Execute / 语义推荐 / 引导式购物状态机），覆盖用户从"明确查价"到"完全不知道买什么"的完整链路；配套落地了行业配置框架、向量语义召回、RAG 知识增强、Trace→SFT 数据工坊等模块，并搭建 150+ 测试用例的分层评测体系，评测结论直接驱动了购物状态机等关键迭代。

### 版本 B（2 分钟）

> 背景是 AI 对传统搜索的重构——从结果列表到直接完成决策。我选择电商比价做载体，因为它天然覆盖四种用户状态，能把 Agent 的核心能力串成一条可演示、可复用的完整链路。
>
> 架构上，我用意图路由把用户输入分到四种执行模式：查价走 ReAct、多品对比走 Plan-Execute（Phase 1 生成 JSON 计划 → Phase 2 DAG 并行执行 → Phase 3 综合回答）、模糊需求走向量语义召回、完全没方向走 6 状态购物状态机（5 槽位逐轮收敛，最多追问 3 次）。
>
> 工程上，多平台比价一次调用并行打 4 个电商平台；语义召回用 2048 维 embedding + 规则过滤混合检索，通过预热 + MD5 指纹增量更新把 API 调用降了 74%；RAG 用 BM25 + 语义融合（α=0.7）做手机领域知识增强。
>
> 评测上，我搭了两层评测体系：tests/ 模块级秒级反馈 + eval/ 端到端分层评测（P0-P6 + IT3C），共 150+ 测试用例。Ground Truth 直接从数据库计算，幻觉检测是自动化的硬指标。这套体系直接发现了购物状态机的三个线上 bug，每个坑沉淀一个 test case。
>
> 最后，我把运行 Trace 做成了 SFT 数据工坊：188 条轨迹 → 4 维度质量评分 + LLM-as-Judge + 人工审核 → 52 条高价值训练样本，可直接对接 SFT 微调。这也是 Agent 训练数据闭环的最真实来源。

### 版本 C（5 分钟）— 版本 B + 四视角展开 + 反思

```text
PM 视角：四种模式诞生于用户真实决策状态，不是炫技；让系统承担复杂度
算法视角：意图分类是瓶颈指标；α=0.7 融合权重；幻觉检测容差；评分维度设计
工程视角：并行调度、embedding 预热、功能开关降级、Trace 可观测性、多模型路由
策略视角：评估驱动迭代（3 坑 → 3 case）、Ground Truth 自动计算、
         Trace→SFT 数据漏斗（188→52 条）、两级路由数据飞轮规划

反思与局限：
├── M4 生成式推荐（"为什么推荐这一款"）已规划未实现——推荐解释是从"能查到"到"能说服"
├── 生产化差距：mock 数据源 → 真实电商 API；单进程内存状态 → Redis 会话持久化；
│   评测时效性 → 价格快照离线回放
├── 意图分类准确率未量化留存，α 敏感性未做扫描曲线
├── 两级路由（LLM 兜底长尾）已设计未落地
└── 若重新做：先固化评测基线与量化指标，再迭代功能（评估先行）
```

---

## 知识树连接

```text
Agent Runtime 🌿
├── Agentic Loop（ReAct / Plan-Execute / 状态机三种控制流）
├── Tool Calling（6 工具统一注册 + Few-Shot 约束）
├── Skills 按需加载（SKILL.md + load_skill 元工具，token ↓74-80%）
└── 自反思纠错（错误恢复机制）

Evaluation 🌿
├── 分层评测体系（tests/ + eval/ P0-P6 + IT3C）← 与 CoT 质检 Gate 同构
├── Ground Truth 自动计算（SQL 直查，零人工标注）
├── LLM-as-Judge + 4 维度启发式评分（可交叉校验）
└── Session 机制（跨 run 横向对比）

Data / Foundational Data ⭐
├── Trace → SFT 数据生产（188 条 → 52 条高价值样本）← Agent 数据 PM 核心能力
├── 归一化 = 实体对齐（处理器多别名 → 标准实体）
├── 17 字段商品模型 = Schema Design
└── Embedding 预处理（预热 + MD5 增量更新）

Decision / Recommendation
├── 语义推荐（向量召回 + 规则过滤）
└── 意图路由（显式路由 vs LLM 判断的 trade-off）

可观测性
├── TraceEvent 17 种事件 + SSE 流式 + DAG 可视化 + 调试仪表盘
└── "先定义观测协议，再写业务逻辑"
```

---

## 待深挖方向

### 算法视角待补

- **意图分类准确率量化**：规则路由的设计逻辑清楚，但没有留存准确率和错误分布，面试不能报数
- **α=0.7 敏感性**：只有单点测试集结论，没做 α 扫描曲线，对结果的敏感范围未知
- **评测统计显著性**：分层评测缺样本量与置信区间，结论是趋势性而非显著性
- **LLM-as-Judge 可靠性验证**：与 4 维度启发式评分的交叉校验做了设计，缺一致性数据（如 Cohen's Kappa）

### 工程视角待补

- **两级路由落地**：规则粗筛 + LLM 兜底 + case 回流飞轮已设计未实现（"评测发现瓶颈 → 换方案"故事差最后一环）
- **M4 生成式推荐**：LLM 意图分解 + Rerank + 推荐解释（README 状态 📋，未实现）
- **生产化差距**：真实电商数据源（DataSource 抽象层已验证）、Redis 会话持久化（并发）、价格快照离线回放（评估时效性）
- **向量库升级**：numpy 内存（mock 期）→ ChromaDB（生产期）切换方案未落地

### 面试视角待补

- **对标公司产品**：与传统比价产品（如什么值得买）的差异点梳理——AI 意图理解 vs 精确输入
- **Claude Code 架构启发**：复盘文档附录八已整理，需消化成自己的 Agent 架构判断
- **Agent 评测行业前沿**：Anthropic Agent Evals 方法论与本项目分层评测的连接（papers/ 已有精读）

---

## 相关文档

- [价格 Agent 复盘文档](price-agent-复盘文档.md) — 面试弹药库：演示逐字稿（Part 0-5）+ 面试官问答 Q1-Q27 + 快手/字节/Agent 基础/LLM-as-Judge/机务 RAG/意图识别/Claude Code 七个专题附录（内容保持原样，仅索引）
- [GitHub 仓库](https://github.com/wenbo030509)（price-agent）— 代码、roadmap、模块设计文档

