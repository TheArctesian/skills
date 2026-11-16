#!/usr/bin/env python3
"""Scan a directory for source files that are too large or doing too much.

Judges violations on CODE lines (blanks and comments excluded) while still
reporting the total, because comment density and scoped CSS should never be
what trips the threshold. For component files (.svelte/.vue) only the <script>
region is measured against the threshold — template and scoped style are mass
that can't idiomatically move out, so counting them produces false violations.

Ranks violators by how far over they are (real split candidates float to the
top; 301-340 "leave it alone" cases sink) and tags a coarse "kind" guess so the
caller isn't forced to open every file to triage.

Usage:
    python scan.py <root_dir> [--threshold 300] [--json] [--check [--baseline FILE]]
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

IGNORE_DIRS = {
    "node_modules", "bower_components", "jspm_packages",
    ".venv", "venv", "env", "virtualenv", "__pypackages__",
    "site-packages", ".tox", ".eggs", "vendor", "Pods", "Carthage",
    "target", "build", "dist", "out", "bin", "obj", ".next", ".nuxt",
    ".output", "coverage", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".gradle", ".idea", ".vscode", ".git", ".hg", ".svn",
    "migrations", ".terraform", "vendored", "third_party", "deps",
    "Godeps", ".cargo", ".dart_tool", ".pub-cache", "elm-stuff",
}

SOURCE_EXTS = {
    ".py", ".pyi", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx",
    ".go", ".rs", ".java", ".kt", ".kts", ".scala", ".rb", ".php",
    ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".hh", ".cs", ".swift",
    ".m", ".mm", ".dart", ".ex", ".exs", ".erl", ".clj", ".cljs",
    ".hs", ".ml", ".lua", ".r", ".jl", ".sh", ".bash", ".zsh",
    ".vue", ".svelte",
}

GENERATED_MARKERS = (".min.", ".bundle.", ".generated.", "_pb2.", ".pb.")

# Component files bundle script + template + style by design.
COMPONENT_EXTS = {".svelte", ".vue"}

# Per-extension line-comment markers for a cheap code/comment/blank split.
# Block comments and string-embedded markers are approximated, not parsed —
# good enough to stop comment density from driving the threshold.
LINE_COMMENT = {
    ".py": "#", ".pyi": "#", ".rb": "#", ".sh": "#", ".bash": "#",
    ".zsh": "#", ".r": "#", ".jl": "#", ".ex": "#", ".exs": "#",
    ".pl": "#",
}
# Default C-family marker for everything else.
DEFAULT_COMMENT = "//"
HASH_FALLBACK_EXTS = set(LINE_COMMENT)


def is_source_file(name: str) -> bool:
    lower = name.lower()
    if any(m in lower for m in GENERATED_MARKERS):
        return False
    if lower.endswith(".d.ts"):
        return False
    _, ext = os.path.splitext(lower)
    return ext in SOURCE_EXTS


def reraise_walk_error(error: OSError):
    raise error


def extract_script(text: str) -> str:
    """Return concatenated <script> blocks from a component file, or '' if none."""
    blocks = re.findall(r"<script[^>]*>(.*?)</script>", text,
                        re.DOTALL | re.IGNORECASE)
    return "\n".join(blocks)


def line_breakdown(text: str, ext: str):
    """Approximate (code, comment, blank) line counts.

    Handles line comments per language and the two common block-comment
    styles (/* */ and triple-quoted Python). Not a parser — a pragmatic
    classifier whose only job is to stop comments inflating the gate.
    """
    marker = "#" if ext in HASH_FALLBACK_EXTS else DEFAULT_COMMENT
    code = comment = blank = 0
    in_block = False          # /* ... */
    in_pydoc = False          # ''' or """ (python-ish only)
    pydoc_q = ""
    pyish = ext in (".py", ".pyi")

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            blank += 1
            continue

        if in_block:
            comment += 1
            if "*/" in line:
                in_block = False
            continue
        if in_pydoc:
            comment += 1
            if pydoc_q in line:
                in_pydoc = False
            continue

        if line.startswith("/*"):
            comment += 1
            if "*/" not in line:
                in_block = True
            continue
        if pyish and (line.startswith('"""') or line.startswith("'''")):
            pydoc_q = line[:3]
            comment += 1
            # closing on same line (and not just the opener)?
            if not (line.count(pydoc_q) >= 2):
                in_pydoc = True
            continue
        if line.startswith(marker):
            comment += 1
            continue
        code += 1
    return code, comment, blank


def guess_kind(text: str, ext: str) -> str:
    if ext in COMPONENT_EXTS:
        return "component"
    lowered = text.lower()
    # A single dominant class/struct with little else.
    class_hits = len(re.findall(r"\b(class|struct|interface)\s+\w", text))
    if class_hits == 1 and "\nclass " not in text[text.find("class "):][6:]:
        return "single-class"
    # Big literal table: many lines that look like data, few statements.
    data_like = len(re.findall(r"^\s*[\['\"{].*[,\]}]\s*$", text, re.MULTILINE))
    if data_like > 0.5 * max(1, text.count("\n")):
        return "data-table"
    return "module"


def scan(root: str, threshold: int):
    files = []
    for dirpath, dirnames, filenames in os.walk(root, onerror=reraise_walk_error):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS
                       and not d.startswith(".")]
        for name in filenames:
            if not is_source_file(name):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root)
            _, ext = os.path.splitext(name.lower())
            text = Path(full).read_text(encoding="utf-8", errors="replace")
            total = text.count("\n") + (1 if text and not text.endswith("\n") else 0)

            # For components, gate on the <script> region only.
            measured_text = text
            measured_note = None
            if ext in COMPONENT_EXTS:
                script = extract_script(text)
                measured_text = script
                measured_note = "script-only"

            code, comment, blank = line_breakdown(measured_text, ext)
            gate = code  # violations judged on code lines
            files.append({
                "path": rel,
                "dir": os.path.dirname(rel) or ".",
                "total_lines": total,
                "code_lines": code,
                "comment_lines": comment,
                "blank_lines": blank,
                "measured": measured_note or "whole-file",
                "kind": guess_kind(text, ext),
                "overage": gate - threshold,
                "violation": gate > threshold,
            })
    files.sort(key=lambda f: (-f["overage"], f["path"]))
    return files


PREFIX_RE = re.compile(r"^([a-z]+)[-_.]")


def topic_clusters(filenames):
    """Group filenames by leading prefix token; >1 cluster suggests mixed topics."""
    clusters = {}
    for n in filenames:
        base = os.path.basename(n).lower()
        m = PREFIX_RE.match(base)
        key = m.group(1) if m else base.split(".")[0]
        clusters.setdefault(key, []).append(n)
    return clusters


def load_baseline(path: Path, threshold: int) -> dict:
    report = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(report, dict) or report.get("gate") != "code_lines"
            or report.get("threshold") != threshold
            or not isinstance(report.get("violations"), list)):
        raise ValueError("expected a scan JSON report with the same threshold")
    counts = {}
    for row in report["violations"]:
        if (not isinstance(row, dict) or not isinstance(row.get("path"), str)
                or not row["path"] or row["path"] in counts
                or type(row.get("code_lines")) is not int or row["code_lines"] <= threshold):
            raise ValueError("invalid or duplicate violation in the baseline")
        counts[row["path"]] = row["code_lines"]
    return counts


def print_check_result(blocking, baseline, threshold):
    for row in blocking:
        previous = baseline.get(row["path"])
        budget = f"limit {threshold}"
        if previous is not None:
            budget += f", baseline {previous}"
        print(
            f'{row["path"]}: {row["code_lines"]} code lines ({budget}). '
            'Move a cohesive responsibility behind a small interface or reuse existing shared code.',
            file=sys.stderr,
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--threshold", type=int, default=300)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 on oversized files (or new/growing violations with --baseline)")
    ap.add_argument("--baseline", type=Path,
                    help="previous --json report at the same threshold, for use with --check")
    args = ap.parse_args()
    if args.threshold < 1:
        ap.error("--threshold must be positive")
    if args.baseline and not args.check:
        ap.error("--baseline requires --check")
    if not os.path.isdir(args.root):
        ap.error(f"not a directory: {args.root}")

    try:
        baseline = load_baseline(args.baseline, args.threshold) if args.baseline else {}
        files = scan(args.root, args.threshold)
    except (OSError, ValueError) as error:
        ap.error(str(error))
    violations = [f for f in files if f["violation"]]
    blocking = [f for f in violations if f["code_lines"] > baseline.get(f["path"], args.threshold)]
    check_status = int(args.check and bool(blocking))
    if check_status:
        print_check_result(blocking, baseline, args.threshold)

    by_dir = {}
    for f in files:
        by_dir.setdefault(f["dir"], []).append(f["path"])

    # Advisory only: flag a directory ONLY when filenames show >1 topic cluster.
    mixed_dirs = {}
    for d, fs in by_dir.items():
        if len(fs) < 6:
            continue
        clusters = topic_clusters(fs)
        substantive = {k: v for k, v in clusters.items() if len(v) >= 2}
        if len(substantive) >= 2:
            mixed_dirs[d] = {k: len(v) for k, v in sorted(
                substantive.items(), key=lambda kv: -len(kv[1]))}

    if args.json:
        report = {
            "root": os.path.abspath(args.root),
            "threshold": args.threshold,
            "gate": "code_lines",
            "total_files": len(files),
            "violations": violations,
            "mixed_topic_dirs": mixed_dirs,
        }
        if args.check:
            report["blocking_violations"] = blocking
        print(json.dumps(report, indent=2))
        return check_status

    print(f"Scanned {len(files)} source files under {args.root}")
    print(f"Threshold: {args.threshold} code lines "
          f"(blanks/comments excluded from the gate)\n")
    if not violations:
        print("No files exceed the threshold. Nothing to standardise.")
    else:
        print(f"{len(violations)} file(s) over {args.threshold} code lines, "
              f"ranked by overage:\n")
        print(f"  {'code':>5} {'+over':>6} {'total':>6}  kind          path")
        for f in violations:
            tag = "" if f["measured"] == "whole-file" else f" [{f['measured']}]"
            print(f"  {f['code_lines']:>5} {f['overage']:>+6} "
                  f"{f['total_lines']:>6}  {f['kind']:<13} {f['path']}{tag}")
        if not args.check:
            print("\n  Review small overages and cohesive files before planning a split.")

    if mixed_dirs:
        print("\nDirectories showing multiple topic clusters "
              "(advisory \u2014 review, don't assume):\n")
        for d, clusters in mixed_dirs.items():
            desc = ", ".join(f"{k}-* ({n})" for k, n in clusters.items())
            print(f"  {d}/  ->  {desc}")
        print("\n  NOTE: a high file count in a cohesive single-topic directory "
              "is CORRECT, not a violation.")

    return check_status


if __name__ == "__main__":
    sys.exit(main())
