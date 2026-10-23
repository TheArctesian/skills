#!/usr/bin/env python3
"""Score a skill workflow's returned JSON (and, for apply runs, the edited tree) against an eval's expected.json."""

import argparse
import json
import pathlib
import re
import subprocess
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
        # A comment sweep must leave nothing behind: untracked files are gate or tool debris.
        debris = subprocess.run(["git", "-C", str(tree), "status", "--porcelain", "--untracked-files=all"], capture_output=True, text=True, check=True).stdout
        missing_code += sum(1 for line in debris.splitlines() if line.startswith("??"))
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


def suite_passes(tree, cmd):
    return subprocess.run(cmd, cwd=tree, capture_output=True, env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin:/opt/homebrew/bin"}).returncode == 0


def mutation_score(exp, tree):
    """Each mutation must turn the suite red; the source is restored byte for byte after each."""
    caught = []
    for m in exp["mutations"]:
        f = tree / m["file"]
        original = f.read_bytes()
        assert m["from"].encode() in original, f"mutation {m['id']} no longer applies"
        try:
            f.write_bytes(original.replace(m["from"].encode(), m["to"].encode(), 1))
            if not suite_passes(tree, exp["test_cmd"]):
                caught.append(m["id"])
        finally:
            f.write_bytes(original)
    return caught


def tests(exp, res, tree):
    if tree:
        caught = mutation_score(exp, tree)
        text = "\n".join(p.read_text() for p in (tree / "tests").rglob("*.py"))
        junk_left = [t for t in exp.get("junk_tests", []) if f"def {t}(" in text]
        green = suite_passes(tree, exp["test_cmd"])
        return {
            "recall": len(caught) / len(exp["mutations"]),
            "keep": 1.0 if green else 0.0,
            "false_positives": len(junk_left),
            "mutations_caught": caught,
            "mutations_missed": [m["id"] for m in exp["mutations"] if m["id"] not in caught],
            "junk_left": junk_left,
            "suite_green": green,
        }

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


def personas(exp, res, _tree):
    findings = res.get("findings") or []
    confirmed = [f for f in findings if f.get("confirmed")]

    def matches(f, p):
        where = norm(f.get("screen")) + " " + norm(f.get("element"))
        text = " ".join(norm(f.get(k)) for k in ("title", "what", "element")) + " " + norm(" ".join(f.get("also") or []))
        return any(s in where for s in p["screens"]) and any(norm(k) in text for k in p["keywords"])

    hit = [p["id"] for p in exp["planted"] if any(matches(f, p) for f in confirmed)]
    fps = [d["id"] for d in exp["decoys"] if any(matches(f, d) for f in confirmed)]
    ai_only = [d for d in exp["decoys"] if d["kind"] == "ai-only"]
    rejected = [d["id"] for d in ai_only if not any(matches(f, d) for f in confirmed)]
    banned = [w for w in ("% of users", "users will", "satisf") if w in norm(res.get("report"))]
    return {
        "recall": len(hit) / len(exp["planted"]),
        "keep": 0.0 if banned else 1.0,
        "false_positives": len(fps),
        "missed": [p["id"] for p in exp["planted"] if p["id"] not in hit],
        "decoys_confirmed": fps,
        "ai_only_rejected": f"{len(rejected)}/{len(ai_only)}",
        "report_banned_phrases": banned,
        "uncertain": len([f for f in findings if f.get("uncertain")]),
        "collapsed": len(res.get("collapsed") or []),
    }


def ux_laws(exp, res, _tree):
    # polish (could-priority) findings are reported unverified rather than dropped, so they count for decoys and
    # clean-file hits as much as verified ones; crediting them for plants too is deliberate, since a correctly
    # identified problem rated "polish" is still found.
    findings = (res.get("findings") or []) + (res.get("polish") or [])

    def laws_of(f):
        return [l for l in (f.get("laws") or [f.get("law")]) if l]

    def prose(f):
        # Keywords match the reviewer's own words only. Matching the whole JSON let one finding that listed every
        # file and every law score every plant.
        return " ".join(norm(f.get(k)) for k in ("what", "fix", "arithmetic", "measurement_needed", "tradeoff")) \
            + " " + norm(" ".join(f.get("also") or []))

    def hits_file(f, p, strict):
        paths = [e.split(":")[0].strip() for e in (f.get("evidence") or [])] + [f.get("shared_component") or ""]
        if any(same_file(e, c) for e in paths if e for c in p["files"]):
            return True
        if any(norm(c) in norm(ev) for ev in (f.get("evidence") or []) for c in p["files"]):
            return True
        if strict:
            return False
        # A journey finding names the flow, not a file, so it gets a name fallback — bounded by word boundaries, or
        # "help text" in a proximity finding would read as a hit on Help.tsx.
        where = " ".join(norm(f.get(k)) for k in ("screen", "element", "shared_component"))
        return any(re.search(rf"\b{re.escape(pathlib.PurePath(c).stem.lower())}\b", where) for c in p["files"])

    def matches(f, p, strict=False):
        if not any(l in p["law"] for l in laws_of(f)):
            return False
        if not hits_file(f, p, strict or not p.get("flow")):
            return False
        if not any(norm(k) in prose(f) for k in p["keywords"]):
            return False
        # A computed plant is only scored when the finding shows the numbers it claims to have derived.
        return all(n in prose(f) for n in p.get("proof", []))

    # One finding may satisfy at most one plant: without this, a single blob naming every law and every file
    # scored full recall.
    hit, used = [], set()
    for p in exp["planted"]:
        for i, f in enumerate(findings):
            if i not in used and matches(f, p):
                hit.append(p["id"])
                used.add(i)
                break
    fps = [d["id"] for d in exp["decoys"] if any(matches(f, d) for f in findings)]
    refuted_decoys = [d["id"] for d in exp["decoys"] if any(matches(f, d) for f in (res.get("refuted") or []))]
    unreachable = norm(json.dumps(res.get("unreachable") or []))
    traced = [d["id"] for d in exp["decoys"] if d["kind"] in ("unreachable", "excluded")
              and any(pathlib.PurePath(c).stem.lower() in unreachable for c in d["files"])]
    # "On" a clean file means the problem is there, not that the file was cited for comparison: every real run quoted
    # the help page beside a finding about another screen, and counting those failed correct audits.
    def only_evidence_is(f, cands):
        paths = [e.split(":")[0].strip() for e in (f.get("evidence") or [])]
        code = [x for x in paths if re.search(r"\.(tsx?|jsx?|vue|svelte|html|css|swift|kt|dart)$", x)]
        return bool(code) and all(any(same_file(x, c) for c in cands) for x in code)

    on_clean = [f"{','.join(laws_of(f))} {f.get('screen')}" for f in findings
                if only_evidence_is(f, exp["clean_files"])]
    # A grade is a claim about evidence; a claim without its proof is the failure mode this skill exists to avoid.
    # A grade the verifiers corrected is exempt: the correction happens after the author supplied the proof.
    unproven = [f"{','.join(laws_of(f))} {f.get('screen')}: {f.get('grade')}"
                for f in findings + (res.get("needs_measurement") or [])
                if not f.get("grade_corrected_from")
                and ((f.get("grade") == "computed" and not norm(f.get("arithmetic")))
                     or (f.get("grade") == "needs_measurement" and not norm(f.get("measurement_needed"))))]
    # Word boundaries: "does not satisfy SC 2.5.8" and "unit conversion" are correct prose, not population claims.
    BANNED = (r"\b\d+\s?% of (users|people)", r"\busers will\b", r"\buser satisfaction\b",
              r"\bsatisfaction (score|rating)", r"\bconversion (rate|lift|uplift)", r"\bengagement will\b")
    banned = [b for b in BANNED if re.search(b, norm(res.get("report")))]
    padded = len(findings) > exp.get("max_findings", 30)
    return {
        "recall": len(hit) / len(exp["planted"]),
        "keep": 0.0 if (banned or padded) else 1.0,
        "false_positives": len(fps),
        "missed": [p["id"] for p in exp["planted"] if p["id"] not in hit],
        "decoys_confirmed": fps,
        "decoys_refuted": f"{len(refuted_decoys)}/{len(exp['decoys'])}",
        "unreachable_traced": traced,
        "findings_on_clean_files": on_clean,
        "grades_without_proof": unproven,
        "report_banned_phrases": banned,
        "findings_total": len(findings),
        "padded": padded,
        "rules_ok": not on_clean and not unproven,
        "needs_measurement": len(res.get("needs_measurement") or []),
        "needs_human": len(res.get("needs_human") or []),
    }


SCORERS = {"prune-comments": prune, "code-quality": cupid, "test-audit": tests, "app-optimisation": perf, "persona-test": personas, "ux-laws": ux_laws}


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
