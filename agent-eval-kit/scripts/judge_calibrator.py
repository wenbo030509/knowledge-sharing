#!/usr/bin/env python3
"""judge_calibrator.py — LLM Judge 校准器：一致性 + 三大偏差检测

实现 LLM Judge 可靠性笔记中的方法：
- Cohen's Kappa：Judge vs 人工（或双 Judge）的判分一致性
- 位置偏差：同一对答案交换顺序后，偏好是否翻转
- 自我偏好：模型是否系统性地偏好自己生成的答案
- 冗长偏差：分数与回答长度是否相关（应无关）

用法：
  python3 judge_calibrator.py examples/judge-data.json [--output report.md]

输入 JSON（examples/judge-data.json）：
{
  "suite": "...",
  "judge_vs_human": [{"case":"c1","judge":"a","human":"b"}, ...],   // Kappa
  "position": [{"case":"c2","order_ab":"a","order_ba":"b"}, ...],   // 位置偏差
  "self_pref": [{"case":"c3","model":"M1","prefer_self":true}, ...],// 自我偏好
  "scores": [{"case":"c4","score":4,"words":320}, ...]              // 冗长偏差
}
"""

import argparse
import json
from collections import Counter


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def kappa(pairs):
    """Cohen's Kappa：两方判分一致性。"""
    if not pairs:
        return None
    n = len(pairs)
    observed = sum(1 for p in pairs if p["judge"] == p["human"]) / n
    pj = Counter(p["judge"] for p in pairs)
    ph = Counter(p["human"] for p in pairs)
    expected = sum((pj[v] / n) * (ph[v] / n) for v in set(pj) | set(ph))
    if expected == 1.0:
        return None
    return round((observed - expected) / (1 - expected), 4)


def position_bias(items):
    """位置偏差：同一对答案 AB / BA 顺序的偏好是否翻转。"""
    if not items:
        return None
    flips = [i["case"] for i in items if i["order_ab"] != i["order_ba"]]
    return {"total": len(items), "flips": len(flips), "flip_rate": round(len(flips) / len(items), 4), "flip_cases": flips}


def self_preference(items):
    """自我偏好：模型偏好自己答案的比例。"""
    if not items:
        return None
    self_wins = sum(1 for i in items if i["prefer_self"])
    return {"total": len(items), "self_wins": self_wins, "self_rate": round(self_wins / len(items), 4)}


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx == 0 or vy == 0:
        return None
    return round(cov / (vx ** 0.5 * vy ** 0.5), 4)


def verbosity_bias(items):
    """冗长偏差：分数与字数相关性 + 高/低分平均字数。"""
    if not items:
        return None
    scores = [i["score"] for i in items]
    words = [i["words"] for i in items]
    high = [i["words"] for i in items if i["score"] >= 4]
    low = [i["words"] for i in items if i["score"] < 4]
    return {
        "total": len(items),
        "corr_score_words": pearson(scores, words),
        "mean_words_high": round(sum(high) / len(high), 1) if high else None,
        "mean_words_low": round(sum(low) / len(low), 1) if low else None,
    }


def render(data, k, pos, selfp, verb):
    lines = [f"# LLM Judge 校准报告：{data.get('suite','unknown')}", ""]
    lines.append("## 一致性（Cohen's Kappa）")
    lines.append("")
    if k is None:
        lines.append("- 无 judge_vs_human 数据")
    else:
        lines.append(f"- κ = {k}")
        lines.append("- κ ≥ 0.6：可接受；κ < 0.6：先对齐 rubric / 增加人工仲裁后再上线")
    lines.append("")
    lines.append("## 位置偏差")
    lines.append("")
    if pos is None:
        lines.append("- 无 position 数据")
    else:
        lines.append(f"- 偏好翻转率：{pos['flip_rate']:.2%}（{pos['flips']}/{pos['total']}）")
        if pos["flip_cases"]:
            lines.append(f"- 翻转 case：{pos['flip_cases'][:10]}")
        lines.append("- 建议：评分时随机打乱选项顺序，并对关键 case 多次评测取稳定结论")
    lines.append("")
    lines.append("## 自我偏好")
    lines.append("")
    if selfp is None:
        lines.append("- 无 self_pref 数据")
    else:
        lines.append(f"- 偏好自己答案的比例：{selfp['self_rate']:.2%}（{selfp['self_wins']}/{selfp['total']}）")
        lines.append("- 显著高于 50% 时：对裁判匿名化 / 混入对照样本，避免自我偏好污染")
    lines.append("")
    lines.append("## 冗长偏差")
    lines.append("")
    if verb is None:
        lines.append("- 无 scores 数据")
    else:
        lines.append(f"- 分数与字数相关系数：{verb['corr_score_words']}")
        lines.append(f"- 高分平均字数：{verb['mean_words_high']}；低分平均字数：{verb['mean_words_low']}")
        lines.append("- |r| > 0.3 时存在明显冗长偏差：用盲评或长度归一化缓解")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--output", default=None)
    args = ap.parse_args()
    data = load(args.input)
    k = kappa(data.get("judge_vs_human", []))
    pos = position_bias(data.get("position", []))
    selfp = self_preference(data.get("self_pref", []))
    verb = verbosity_bias(data.get("scores", []))
    report = render(data, k, pos, selfp, verb)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print("written:", args.output)
    else:
        print(report)


if __name__ == "__main__":
    main()
