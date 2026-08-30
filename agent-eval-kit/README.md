# agent-eval-kit · Agent 评测体系方法论与工具

> 把论文/前沿方法工程化为「可复用方法论 + 可运行工具」，而不是停留在笔记里。
>
> 它是我 12+ 篇评测/数据/训练论文精读、知识树与方法论的**可验证产出**，也是 Price-Agent 分层评测体系的独立化沉淀。

## 定位

一套面向 Agent / LLM / 多模态评测的「设计 → 生产 → 判分 → 统计」方法论与工具：

- **docs/**：评测四层模型、Benchmark 设计 Playbook、LLM Judge 可靠性 Checklist、评测统计学
- **scripts/**：可运行的评测统计与质量工具（pass@k / AA 校验 / Cohen's Kappa）
- **examples/**：可落地的评测数据契约（case contract）与示例结果

## 为什么存在

评测最容易踩的坑是"跑完看个通过率就上线"。本项目的核心立场：

```text
能由状态和规则确定的部分，优先程序验证；
LLM Judge 只处理开放表达，且必须校准；
成功率之外，还要看稳定性（pass^k）与评测本身的稳定性（AA 校验）。
```

## 内容结构

```text
agent-eval-kit/
├── docs/
│   ├── 01-评测四层模型.md
│   └── 02-Benchmark设计Playbook.md
├── scripts/
│   ├── eval_report.py            ← 评测统计工具（pass@k / AA 校验 / Kappa）
│   ├── benchmark_planner.py      ← Benchmark 生成器（能力地图 → 覆盖矩阵 → case 契约）
│   └── judge_calibrator.py       ← LLM Judge 校准器（一致性 + 三大偏差）
├── examples/
│   ├── refund-case-contract.yaml ← 冷启动评测集 case 契约示例
│   ├── results.json              ← 统计工具输入示例
│   ├── benchmark-config.json     ← Benchmark 生成器配置示例
│   └── judge-data.json           ← Judge 校准器输入示例
└── README.md
```

## 快速使用

```bash
python3 scripts/eval_report.py examples/results.json
python3 scripts/eval_report.py examples/results.json --k 5 --output report.md
python3 scripts/benchmark_planner.py examples/benchmark-config.json --out-dir out
python3 scripts/judge_calibrator.py examples/judge-data.json
```

## 路线图

- [x] 评测统计工具（pass@1/pass@k/pass^k、AA 校验、Cohen's Kappa）
- [x] Benchmark 生成器：能力地图 → 覆盖矩阵 → case 契约（受控变异 + 四道验收）
- [x] LLM Judge 校准器：偏差检测（位置/自我偏好/冗长）+ Kappa 报告
- [ ] 文档英文版 + 发布到 GitHub

## 与 Price-Agent 的关系

Price-Agent 是这个方法论的第一代工程载体（9 阶段分层评测、Ground Truth 自动判分、Session 对比）；agent-eval-kit 是把其中可复用的部分独立、泛化、开源化，让方法论可以被其他项目直接使用。
