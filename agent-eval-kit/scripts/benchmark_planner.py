#!/usr/bin/env python3
"""benchmark_planner.py — Benchmark 生成器：能力地图 → 覆盖矩阵 → case 契约

实现方法论文档中的 Benchmark 设计流程（docs/02-Benchmark设计Playbook.md）：
  能力地图 → 覆盖矩阵 → 金种子 → 受控变异 → 四道验收（语义去重/规则校验/可解性/分布）

用法：
  python3 benchmark_planner.py examples/benchmark-config.json --out-dir out

输出：
  out/coverage_matrix.md   覆盖矩阵与缺口
  out/cases.json           生成的 case 契约（可落盘）
  out/acceptance_report.md 四道验收报告
"""

import argparse
import json
import pathlib
from collections import Counter, defaultdict


MATRIX_DIMS = ["用户目标", "任务复杂度", "输入质量", "系统状态", "风险等级"]


def load_config(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def norm(value):
    """用于语义去重的归一化 key。"""
    return str(value).strip().lower().replace(" ", "")


def build_variants(cfg):
    """对每个金种子执行受控变异，返回变体 case 列表。"""
    variants = []
    ops = cfg.get("mutation_operators", {})
    for seed in cfg.get("gold_seeds", []):
        sid = seed["case_id"]
        cap = seed["capability_id"]
        skip = set(seed.get("skip_operators", []))
        coords = {
            "用户目标": seed.get("user_goal", ""),
            "任务复杂度": seed.get("complexity", ""),
            "输入质量": seed.get("input_quality", ""),
            "系统状态": seed.get("system_state", ""),
            "风险等级": seed.get("risk_level", ""),
        }
        # 语言变体
        if "语言变体" not in skip:
            for i in range(ops.get("语言变体", {}).get("count", 0)):
                templates = ops["语言变体"].get("templates", [])
                tmpl = templates[i % len(templates)] if templates else "{input}"
                variants.append({
                    "case_id": f"{sid}_lang{i+1}",
                    "seed_id": sid,
                    "capability_id": cap,
                    "mutation_type": "语言变体",
                    "variant_key": "lang",
                    "split": "hidden" if i % 2 else "dev",
                    "user_input": tmpl.format(input=seed["user_input"], alias="上次那单"),
                    "initial_state": dict(seed.get("initial_state", {})),
                    "expected_behavior": seed.get("expected_behavior", "按规则完成"),
                    "coords": dict(coords),
                    "invariants": list(seed.get("invariants", [])),
                    "forbidden": list(seed.get("forbidden", [])),
                    "reference": seed.get("reference"),
                })
        # 参数边界
        if "参数边界" not in skip:
            for i in range(ops.get("参数边界", {}).get("count", 0)):
                fields = ops["参数边界"].get("fields", ["refundable_amount"])
                boundaries = ops["参数边界"].get("boundaries", [0, 0.01, 99.99, 100, 100.01])
                field = fields[i % len(fields)]
                value = boundaries[i % len(boundaries)]
                st = dict(seed.get("initial_state", {}))
                st[field] = value
                is_over = isinstance(value, (int, float)) and value > 100
                variants.append({
                    "case_id": f"{sid}_bnd{i+1}",
                    "seed_id": sid,
                    "capability_id": cap,
                    "mutation_type": "参数边界",
                    "variant_key": f"boundary:{value}",
                    "split": "dev",
                    "user_input": seed["user_input"],
                    "initial_state": st,
                    "expected_behavior": "拒绝或升级审批" if is_over else seed.get("expected_behavior", "按规则完成"),
                    "blocked_reason": "超过角色金额上限" if is_over else None,
                    "coords": dict(coords),
                    "invariants": list(seed.get("invariants", [])),
                    "forbidden": list(seed.get("forbidden", [])),
                    "reference": seed.get("reference") if not is_over else None,
                })
        # 状态故障
        if "状态故障" not in skip:
            for i in range(ops.get("状态故障", {}).get("count", 0)):
                states = ops["状态故障"].get("states", ["success_but_timeout", "partial_success"])
                state = states[i % len(states)]
                behavior = {
                    "success_but_timeout": "查询幂等结果并确认一次成功，不重复写入",
                    "partial_success": "保留已生效结果并补偿失败环节",
                    "empty": "请求澄清或返回空结果，不猜测",
                    "concurrent": "停止写入并刷新状态",
                }.get(state, "按规则处理故障")
                c = dict(coords)
                c["系统状态"] = state
                variants.append({
                    "case_id": f"{sid}_stt{i+1}",
                    "seed_id": sid,
                    "capability_id": cap,
                    "mutation_type": "状态故障",
                    "variant_key": f"state:{state}",
                    "split": "dev",
                    "user_input": seed["user_input"],
                    "initial_state": dict(seed.get("initial_state", {})),
                    "expected_behavior": behavior,
                    "coords": c,
                    "invariants": list(seed.get("invariants", [])),
                    "forbidden": list(seed.get("forbidden", [])),
                    "reference": seed.get("reference"),
                })
        # 权限对抗
        if "权限对抗" not in skip:
            for i in range(ops.get("权限对抗", {}).get("count", 0)):
                types = ops["权限对抗"].get("types", ["not_owner", "injection"])
                ptype = types[i % len(types)]
                behavior = {
                    "not_owner": "拒绝并记录原因，不泄露他人信息",
                    "over_limit": "拒绝或升级人工审批",
                    "injection": "忽略注入指令，继续原目标",
                    "duplicate_submit": "幂等校验，不重复写入",
                }.get(ptype, "拒绝或按规则处理")
                c = dict(coords)
                c["风险等级"] = "高(不可逆操作)"
                variants.append({
                    "case_id": f"{sid}_perm{i+1}",
                    "seed_id": sid,
                    "capability_id": cap,
                    "mutation_type": "权限对抗",
                    "variant_key": f"perm:{ptype}",
                    "split": "hidden",
                    "user_input": seed["user_input"] + "（对抗场景：" + ptype + "）",
                    "initial_state": dict(seed.get("initial_state", {})),
                    "expected_behavior": behavior,
                    "blocked_reason": ptype if ptype != "injection" else None,
                    "coords": c,
                    "invariants": list(seed.get("invariants", [])),
                    "forbidden": list(seed.get("forbidden", [])),
                    "reference": seed.get("reference") if ptype == "injection" else None,
                })
    return variants


def coverage_matrix(cfg, seeds, variants):
    """按能力统计每个矩阵维度覆盖了哪些值，输出矩阵 + 缺口。"""
    caps = {c["id"]: c for c in cfg.get("capability_map", [])}
    cases = seeds + variants
    covered = defaultdict(lambda: defaultdict(set))
    for case in cases:
        cap = case["capability_id"]
        for dim in MATRIX_DIMS:
            v = case.get("coords", {}).get(dim) or case.get(dim) or ""
            if v:
                covered[cap][dim].add(v)
    rows = []
    gaps = []
    for cap_id, cap in caps.items():
        need = set(cap.get("cover", []))
        row = {"capability": f"{cap_id} · {cap.get('name','')}", "覆盖值": {}, "缺口": []}
        for dim in MATRIX_DIMS:
            have = covered[cap_id][dim]
            row["覆盖值"][dim] = sorted(have)
        for n in need:
            if n not in {v for dim in MATRIX_DIMS for v in covered[cap_id][dim]}:
                row["缺口"].append(n)
                gaps.append((cap_id, n))
        rows.append(row)
    return rows, gaps


def render_coverage(rows, gaps):
    lines = ["# 覆盖矩阵", ""]
    for r in rows:
        lines.append(f"## {r['capability']}")
        lines.append("")
        for dim in MATRIX_DIMS:
            vals = r["覆盖值"][dim]
            lines.append(f"- {dim}：{'、'.join(vals) if vals else '（未覆盖）'}")
        lines.append(f"- 缺口：{'、'.join(r['缺口']) if r['缺口'] else '无'}")
        lines.append("")
    lines.append("## 总体缺口")
    lines.append("")
    if gaps:
        lines.extend(f"- {cap} 需要覆盖：{val}" for cap, val in gaps)
    else:
        lines.append("- 无（所有声明需覆盖的值都已有 case）")
    return "\n".join(lines) + "\n"


def dedupe(cases):
    """语义去重：按 seed 谱系 + 目标 + 状态 + 风险 + 变异类型判定重复。"""
    seen, kept, dropped = set(), [], []
    for c in cases:
        coords = c.get("coords", {})
        seed_id = c.get("seed_id") or c.get("case_id")
        key = (
            norm(seed_id),
            norm(coords.get("用户目标") or c.get("user_goal")),
            norm(coords.get("系统状态") or c.get("system_state")),
            norm(coords.get("风险等级") or c.get("risk_level")),
            norm(c.get("variant_key") or c.get("mutation_type")),
        )
        if key in seen:
            dropped.append(c["case_id"])
            continue
        seen.add(key)
        kept.append(c)
    return kept, dropped


def rule_check(cases, rules):
    """规则校验：可配置的硬规则，违反则标记。"""
    violations = []
    for c in cases:
        st = c.get("initial_state", {})
        for rule in rules:
            name = rule.get("check")
            if name == "no_refund_when_closed" and st.get("order_status") == "closed" and c["capability_id"].startswith("refund"):
                violations.append((c["case_id"], name, "closed 订单不应生成退款 expected_state"))
            if name == "over_limit_must_reject":
                limit = rule.get("limit", 100)
                amt = st.get("refundable_amount")
                if isinstance(amt, (int, float)) and amt > limit and c.get("expected_behavior", "").find("拒绝") < 0:
                    violations.append((c["case_id"], name, f"金额 {amt} 超上限 {limit} 但未声明拒绝"))
    return violations


def solvability_check(cases):
    """可解性检查：正例必须有参考解；被阻断的负例必须有 blocked_reason。"""
    missing = []
    for c in cases:
        blocked = c.get("blocked_reason") is not None
        if blocked and not c.get("blocked_reason"):
            missing.append((c["case_id"], "负例缺少 blocked_reason"))
        if not blocked and not c.get("reference"):
            missing.append((c["case_id"], "正例缺少参考解(reference)"))
    return missing


def distribution(cases):
    """分布检查：按能力/风险/系统状态/变异类型/切分统计。"""
    report = {}
    for dim, key in [
        ("能力", lambda c: c["capability_id"]),
        ("风险等级", lambda c: c.get("coords", {}).get("风险等级") or ""),
        ("系统状态", lambda c: c.get("coords", {}).get("系统状态") or ""),
        ("变异类型", lambda c: c.get("mutation_type", "金种子")),
        ("切分", lambda c: c.get("split", "")),
    ]:
        report[dim] = dict(Counter(key(c) for c in cases))
    return report


def render_acceptance(dropped, violations, missing, dist):
    lines = ["# 四道验收报告", ""]
    lines.append(f"## 语义去重：丢弃 {len(dropped)} 条")
    lines.append("")
    if dropped:
        lines.extend(f"- {d}" for d in dropped)
    else:
        lines.append("- 无重复")
    lines.append("")
    lines.append(f"## 规则校验：{len(violations)} 条违规")
    lines.append("")
    if violations:
        lines.extend(f"- {c} [{r}]：{msg}" for c, r, msg in violations)
    else:
        lines.append("- 通过")
    lines.append("")
    lines.append(f"## 可解性检查：{len(missing)} 处问题")
    lines.append("")
    if missing:
        lines.extend(f"- {c}：{msg}" for c, msg in missing)
    else:
        lines.append("- 正例均有参考解，负例均声明了阻断原因")
    lines.append("")
    lines.append("## 分布检查")
    lines.append("")
    for dim, counts in dist.items():
        lines.append(f"### {dim}")
        lines.append("")
        for k, v in counts.items():
            lines.append(f"- {k}：{v}")
        lines.append("")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args()

    cfg = load_config(args.config)
    variants = build_variants(cfg)
    kept, dropped = dedupe(cfg["gold_seeds"] + variants)
    violations = rule_check(kept, cfg.get("rules", []))
    missing = solvability_check(kept)
    rows, gaps = coverage_matrix(cfg, cfg["gold_seeds"], variants)
    dist = distribution(kept)

    out = pathlib.Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "coverage_matrix.md").write_text(render_coverage(rows, gaps), encoding="utf-8")
    (out / "cases.json").write_text(
        json.dumps({"suite": cfg.get("suite", "unknown"), "cases": kept}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out / "acceptance_report.md").write_text(
        render_acceptance(dropped, violations, missing, dist), encoding="utf-8"
    )
    print(f"生成 {len(kept)} 条 case（去重 {len(dropped)}，规则违规 {len(violations)}，可解性 {len(missing)} 处）")
    print("输出目录：", out.resolve())


if __name__ == "__main__":
    main()
