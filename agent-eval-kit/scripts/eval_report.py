#!/usr/bin/env python3
"""eval_report.py — Agent 评测统计工具（Python 标准库，无第三方依赖）

把逐 case 的评测结果转换成可归因的统计报告，实现笔记/论文中沉淀的评测统计方法：
- pass@1 / pass@k / pass^k：区分"偶尔做对"和"稳定做对"
- AA 校验：同一套评测跑两遍，区分真实退化与随机波动
- Cohen's Kappa：两个裁判（或 LLM Judge vs 人工）的一致性

输入 JSON 结构（见 examples/results.json）：
{
  "suite": "评测套件名",
  "trials": {"c1": [1,0,1,1], "c2": [1,1,1], ...},   // 每个 case 的多轮 0/1 结果
  "run_a": {"c1": 1, "c2": 1, ...},                  // 第一遍逐 case 通过/失败（AA 用）
  "run_b": {"c1": 1, "c2": 0, ...},                  // 第二遍逐 case 通过/失败（AA 用）
  "judge": [{"case": "c1", "a": 4, "b": 4}, ...]     // 双裁判打分（Kappa 用）
}

用法：
  python3 eval_report.py results.json [--k N] [--output report.md]
"""

import argparse
import json
import math
from collections import Counter


def load_results(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def pass_metrics(trials, k=None):
    """从多轮 0/1 结果计算 pass@1 / pass@k / pass^k。"""
    per_case = {}
    for cid, ts in trials.items():
        n = len(ts)
        kk = k if k and k <= n else n
        if kk <= 0:
            continue
        pass1 = sum(1 for t in ts if t == 1) / n
        pass_k = 1 if any(t == 1 for t in ts) else 0          # 至少一次成功
        pass_all = 1 if all(t == 1 for t in ts) else 0        # 全部成功（稳定性）
        per_case[cid] = {"n": n, "pass@1": pass1, "pass@k": pass_k, "pass^k": pass_all}

    n_cases = len(per_case)
    if n_cases == 0:
        return {"cases": {}, "summary": {}}
    summary = {
        "cases": n_cases,
        "avg_pass@1": round(sum(c["pass@1"] for c in per_case.values()) / n_cases, 4),
        "pass@k_cases": round(sum(c["pass@k"] for c in per_case.values()) / n_cases, 4),
        "stable_cases": round(sum(c["pass^k"] for c in per_case.values()) / n_cases, 4),
    }
    return {"cases": per_case, "summary": summary}


def aa_consistency(run_a, run_b):
    """AA 校验：两遍运行逐 case 一致性。"""
    all_cases = sorted(set(run_a) | set(run_b))
    agree = 0
    disagreements = []
    for c in all_cases:
        a, b = run_a.get(c), run_b.get(c)
        if a is None or b is None:
            continue
        if a == b:
            agree += 1
        else:
            disagreements.append((c, a, b))
    total = len(all_cases)
    rate = round(agree / total, 4) if total else None
    return {"total": total, "agree": agree, "rate": rate, "disagreements": disagreements}


def cohen_kappa(pairs):
    """双裁判打分的一致性（Cohen's Kappa）。"""
    if not pairs:
        return None
    a_ratings = [p["a"] for p in pairs]
    b_ratings = [p["b"] for p in pairs]
    n = len(pairs)
    observed = sum(1 for a, b in zip(a_ratings, b_ratings) if a == b) / n
    pa = Counter(a_ratings)
    pb = Counter(b_ratings)
    expected = sum((pa[v] / n) * (pb[v] / n) for v in set(pa) | set(pb))
    if expected == 1.0:
        return None
    return round((observed - expected) / (1 - expected), 4)


def render_markdown(suite, metrics, aa, kappa, k):
    lines = [f"# 评测统计报告：{suite}", ""]
    m = metrics["summary"]
    lines.append("## 通过率与稳定性（pass@1 / pass@k / pass^k）")
    lines.append("")
    lines.append(f"- 用例数：{m['cases']}")
    lines.append(f"- 平均 pass@1（单次通过率）：{m['avg_pass@1']:.2%}")
    lines.append(f"- pass@k（多试几次至少成功一次，k={k}）：{m['pass@k_cases']:.2%}")
    lines.append(f"- pass^k（连续全部成功，稳定性）：{m['stable_cases']:.2%}")
    lines.append("")
    lines.append("> 判断：pass@k 高但 pass^k 低 = 偶尔做对（方差问题，先修 prompt/环境）；两者都低 = 能力缺失（需加工具/数据）。")
    lines.append("")
    if aa:
        lines.append("## AA 校验（评测稳定性）")
        lines.append("")
        lines.append(f"- 两遍运行逐 case 一致率：{aa['rate']:.2%}（{aa['agree']}/{aa['total']}）")
        if aa["disagreements"]:
            lines.append(f"- 不一致 case：{aa['disagreements'][:10]}")
            lines.append("- 建议：一致率过低时先修评测稳定性（环境重置/判分口径），再读实验差异。")
        lines.append("")
    if kappa is not None:
        lines.append("## 双裁判一致性（Cohen's Kappa）")
        lines.append("")
        lines.append(f"- κ = {kappa}")
        lines.append("- 参考：κ < 0.6 说明判分标准不一致，需要先对齐 rubric 或人工仲裁。")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="评测结果 JSON")
    ap.add_argument("--k", type=int, default=None, help="pass@k 的 k（默认取每个 case 的试验次数）")
    ap.add_argument("--output", default=None, help="输出 Markdown 报告路径（默认打印到 stdout）")
    args = ap.parse_args()

    data = load_results(args.input)
    suite = data.get("suite", "unknown")
    metrics = pass_metrics(data.get("trials", {}), k=args.k)
    aa = aa_consistency(data.get("run_a", {}), data.get("run_b", {})) if data.get("run_a") else None
    kappa = cohen_kappa(data.get("judge", [])) if data.get("judge") else None

    if args.k is None:
        args.k = max((len(v) for v in data.get("trials", {}).values()), default=1)
    report = render_markdown(suite, metrics, aa, kappa, args.k)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print("written:", args.output)
    else:
        print(report)


if __name__ == "__main__":
    main()
