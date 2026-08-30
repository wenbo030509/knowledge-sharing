# Benchmark 设计 Playbook

> 把"如何构建一套评测集"沉淀为可执行步骤。综合自：Anthropic evals、冷启动评测集、SWE-bench/CRMArena-Pro/ToolSandbox/AgentDojo、Optima 等。

## 八步流程

```text
1. 能力地图      明确 Agent 承诺做什么、不做什么；每个叶节点可映射到可观察结果
2. 覆盖矩阵      用户目标 × 任务复杂度 × 输入质量 × 系统状态 × 风险等级
3. 金种子        20-50 条人工案例：两人可独立判同、参考解通过全部 grader、
                 断言可追溯、失败可区分（Agent/工具/环境/grader）
4. 受控变异      LLM 只在规定维度扩写（语言/参数边界/状态故障/权限对抗），
                 不改变业务规则与安全边界
5. 四道验收      语义去重 → 规则校验 → 可解性 → 分布检查
6. 六数据桶      Gold / Coverage / Challenge / Regression / Canary / Hidden
7. 三层 Oracle   Outcome（办成没）→ Behavior（合不合规）→ Response（说清没）
8. 发布门禁      Guardrail 指标独立于成功率，高风险阈值预登记为零
```

## 防污染红线

- Hidden Test 按 seed family 切分，不随机打散 mutation。
- 金种子、覆盖集、挑战集、回归集、Canary、隐藏集职责分离。
- 参考执行用于验证题目+grader 可用，不规定唯一轨迹。

## 判分优先级

```text
程序验证 > 规则验证 > LLM Judge > 人工抽检
```

Judge 只处理开放表达，必须看到证据、允许返回 unknown，并接受业务人员校准。
