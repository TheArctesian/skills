#!/usr/bin/env python3
"""Score a skill workflow's returned JSON (and, for apply runs, the edited tree) against an eval's expected.json."""

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
THRESHOLDS = {"recall": 0.8, "keep": 0.9, "false_positives": 0}


def norm(s):
    return " ".join(str(s or "").lower().split())


def same_file(a, b):
    a, b = norm(a).lstrip("./"), norm(b).lstrip("./")
    return bool(a) and (a.endswith(b) or b.endswith(a))


def blob(obj):
    return norm(json.dumps(obj))


def prune(exp, res, tree):
    if tree:
        text = {f: (tree / f).read_text() for f in {e["file"] for e in exp["must_keep"] + exp["must_delete"] + exp.get("must_survive_code", [])}}
        deleted = [e for e in exp["must_delete"] if e["text"] not in text[e["file"]]]
        kept = [e for e in exp["must_keep"] if e["text"] in text[e["file"]]]
        code = [e for e in exp.get("must_survive_code", []) if e["text"] in text[e["file"]]]
        missing_code = len(exp.get("must_survive_code", [])) - len(code)
    else:
        props = res.get("proposals") or []

        def verdict(e):
            hits = [p for p in props if same_file(p.get("file"), e["file"]) and (norm(e["text"]) in norm(p.get("text")) or norm(p.get("text")) in norm(e["text"]) and len(norm(p.get("text"))) > 8)]
            if any(p.get("action") == "delete" or (p.get("action") == "rewrite" and norm(e["text"]) not in norm(p.get("rewrite"))) for p in hits):
                return "gone"
            return "kept"

        deleted = [e for e in exp["must_delete"] if verdict(e) == "gone"]
        kept = [e for e in exp["must_keep"] if verdict(e) == "kept"]
        missing_code = 0
    rnt = res.get("rule_needs_test") or []
    found_rules = [e for e in exp.get("rule_needs_test", []) if any(same_file(r.get("file"), e["file"]) and norm(e["text"]) in blob(r) for r in rnt)]
    return {
        "recall": len(deleted) / len(exp["must_delete"]),
        "keep": len(kept) / len(exp["must_keep"]),
        "false_positives": missing_code,
        "rule_findings": f"{len(found_rules)}/{len(exp.get('rule_needs_test', []))}",
        "rules_ok": len(found_rules) == len(exp.get("rule_needs_test", [])),
        "missed": [e["text"] for e in exp["must_delete"] if e not in deleted],
        "wrongly_removed": [e["text"] for e in exp["must_keep"] if e not in kept],
    }


def cupid(exp, res, _tree):
    findings = res.get("findings") or []
    hit, wrong_prop = [], []
    for p in exp["planted"]:
        on_file = [f for f in findings if same_file(f.get("file"), p["file"]) and any(norm(k) in blob(f) for k in p["keywords"])]
        if any(p["property"] in (f.get("properties") or [f.get("property")]) for f in on_file):
            hit.append(p["id"])
        elif on_file:
            wrong_prop.append(p["id"])
    fps = [f for f in findings if any(same_file(f.get("file"), c) for c in exp["clean_files"])]
    return {
        "recall": len(hit) / len(exp["planted"]),
        "keep": 1.0,
        "false_positives": len(fps),
        "missed": [p["id"] for p in exp["planted"] if p["id"] not in hit],
        "wrong_property": wrong_prop,
        "false_positive_findings": [f"{f.get('property')} {f.get('file')}: {f.get('smell')}" for f in fps],
        "needs_human": len(res.get("needs_human") or []),
    }


def tests(exp, res, _tree):
    marks = [m for p in res.get("plans") or [] for m in p.get("marks") or []]

    def mark_of(e):
        ms = [m for m in marks if same_file(m.get("file"), e["file"]) and norm(e["test"]) in norm(m.get("test"))]
        return ms[0].get("mark") if ms else "R"

    flagged = [e for e in exp["must_flag"] if mark_of(e) in e["marks"]]
    # F keeps the contract and repairs the assertion, so it counts as kept; only C and D remove a test.
    kept = [e for e in exp["must_keep"] if mark_of(e) in ("R", "F")]
    return {
        "recall": len(flagged) / len(exp["must_flag"]),
        "keep": len(kept) / len(exp["must_keep"]),
        "false_positives": len(exp["must_keep"]) - len(kept),
        "missed": [e["test"] for e in exp["must_flag"] if e not in flagged],
        "wrongly_flagged": [e["test"] for e in exp["must_keep"] if e not in kept],
    }


def perf(exp, res, _tree):
    gaps = [g for lane in res.get("lanes") or [] for g in lane.get("gaps") or []]
    confirmed = [g for g in gaps if g.get("confirmed")]

    # A gap is "about" what its title names; evidence and fix text mention neighbouring code too freely to match on.
    def matches(g, p):
        return any(same_file(ev.split(":")[0], p["file"]) or norm(p["file"]) in norm(ev) for ev in g.get("evidence") or []) and any(norm(k) in norm(g.get("title")) for k in p["keywords"])

    hit = [p["id"] for p in exp["planted"] if any(matches(g, p) for g in confirmed)]
    fps = [d["id"] for d in exp["decoys"] if any(matches(g, d) for g in confirmed)]
    return {
        "recall": len(hit) / len(exp["planted"]),
        "keep": 1.0,
        "false_positives": len(fps),
        "missed": [p["id"] for p in exp["planted"] if p["id"] not in hit],
        "decoys_confirmed": fps,
        "uncertain": len(res.get("uncertain") or []),
    }


SCORERS = {"prune-comments": prune, "code-quality": cupid, "test-audit": tests, "app-optimisation": perf}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("skill", choices=SCORERS)
    ap.add_argument("result", type=pathlib.Path, help="the JSON object the workflow returned")
    ap.add_argument("--tree", type=pathlib.Path, help="apply runs: the edited fixture copy to inspect")
    ap.add_argument("--second-run", type=pathlib.Path, help="result of re-running on the already-processed tree")
    a = ap.parse_args()
    exp = json.loads((HERE / a.skill / "expected.json").read_text())
    res = json.loads(a.result.read_text())
    if res.get("stage") == "estimate":
        sys.exit("this is an estimate; score the confirmed run's result")
    score = SCORERS[a.skill](exp, res, a.tree)
    if a.second_run:
        again = json.loads(a.second_run.read_text())
        t = again.get("totals") or {}
        score["second_run_changes"] = (t.get("deleted", 0) + t.get("rewritten", 0)) if a.skill == "prune-comments" else len(again.get("findings") or again.get("refuted") or [])
    score["version"] = res.get("version")
    score["pass"] = score["recall"] >= THRESHOLDS["recall"] and score["keep"] >= THRESHOLDS["keep"] and score["false_positives"] <= THRESHOLDS["false_positives"] and score.get("rules_ok", True)
    print(json.dumps(score, indent=2, ensure_ascii=False))
    sys.exit(0 if score["pass"] else 1)


if __name__ == "__main__":
    main()
