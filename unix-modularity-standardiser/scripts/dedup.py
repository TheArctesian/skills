#!/usr/bin/env python3
"""Token-based near-duplicate detection across source files (winnowing).

Oversized files are frequently a symptom of cross-file duplication: the real
fix is to extract a shared module, not to split each copy in place. This finds
those clones so the plan phase can extract-first.

Method: tokenize each file with Pygments (language-aware), normalize away
identifier names and literal values so renamed copies still match, build k-gram
hashes, then select a fingerprint subset via winnowing (Schleimer, Wilkerson &
Aiken 2003). Files sharing many fingerprints are reported as clone pairs with an
approximate overlap ratio.

Usage:
    python dedup.py <root_dir> [--min-overlap 0.30] [--only file1 file2 ...]
                    [--json]
"""
import argparse
import json
import os
import sys

try:
    from pygments import lex
    from pygments.lexers import get_lexer_for_filename
    from pygments.token import Token
    from pygments.util import ClassNotFound
except ImportError:
    print("error: pygments is required (pip install pygments)", file=sys.stderr)
    sys.exit(2)

# Reuse the scanner's ignore/source rules.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan import IGNORE_DIRS, is_source_file  # noqa: E402

K = 12          # k-gram length in tokens
WINDOW = 8      # winnowing window size


def normalize_tokens(path, text):
    """Yield a normalized token string: names -> N, literals -> L, keep structure."""
    try:
        lexer = get_lexer_for_filename(path, text)
    except ClassNotFound:
        return []
    out = []
    for ttype, value in lex(text, lexer):
        if ttype in Token.Comment or ttype in Token.Text or ttype in Token.Whitespace:
            continue
        if ttype in Token.Name:
            out.append("N")
        elif ttype in Token.Literal or ttype in Token.String or ttype in Token.Number:
            out.append("L")
        else:
            v = value.strip()
            if v:
                out.append(v)
    return out


def kgram_hashes(tokens):
    if len(tokens) < K:
        return []
    hashes = []
    for i in range(len(tokens) - K + 1):
        gram = " ".join(tokens[i:i + K])
        hashes.append(hash(gram) & 0xFFFFFFFF)
    return hashes


def winnow(hashes):
    """Return the set of fingerprint hashes selected by winnowing."""
    if not hashes:
        return set()
    if len(hashes) < WINDOW:
        return set(hashes)
    fps = set()
    min_idx = -1
    for i in range(len(hashes) - WINDOW + 1):
        window = hashes[i:i + WINDOW]
        m = min(range(len(window)), key=lambda j: window[j])
        gi = i + m
        if gi != min_idx:
            fps.add(window[m])
            min_idx = gi
    return fps


def fingerprint_file(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return set()
    return winnow(kgram_hashes(normalize_tokens(path, text)))


def collect_files(root, only):
    if only:
        return [os.path.abspath(p) for p in only if os.path.isfile(p)]
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS
                       and not d.startswith(".")]
        for name in filenames:
            if is_source_file(name):
                found.append(os.path.join(dirpath, name))
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--min-overlap", type=float, default=0.30)
    ap.add_argument("--only", nargs="*", default=None,
                    help="restrict comparison to these specific files")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    files = collect_files(args.root, args.only)
    fps = {}
    for p in files:
        fp = fingerprint_file(p)
        if fp:
            fps[p] = fp

    pairs = []
    paths = list(fps)
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            a, b = paths[i], paths[j]
            inter = len(fps[a] & fps[b])
            if not inter:
                continue
            smaller = min(len(fps[a]), len(fps[b]))
            overlap = inter / smaller if smaller else 0.0
            if overlap >= args.min_overlap:
                pairs.append({
                    "file_a": os.path.relpath(a, args.root),
                    "file_b": os.path.relpath(b, args.root),
                    "shared_fingerprints": inter,
                    "overlap": round(overlap, 3),
                })
    pairs.sort(key=lambda p: p["overlap"], reverse=True)

    if args.json:
        print(json.dumps({"root": os.path.abspath(args.root),
                          "min_overlap": args.min_overlap,
                          "clone_pairs": pairs}, indent=2))
        return

    if not pairs:
        print("No significant cross-file duplication found "
              f"(min overlap {args.min_overlap:.0%}).")
        return
    print(f"Potential clone pairs (>= {args.min_overlap:.0%} overlap), "
          "strongest first:\n")
    for p in pairs:
        print(f"  {p['overlap']:>5.0%}  {p['file_a']}  <->  {p['file_b']}")
    print("\n  Extract the shared logic into one module BEFORE splitting "
          "these files individually.")


if __name__ == "__main__":
    main()
