"""Python half of comments.ts: comment counts, and AST equality with docstrings removed."""

import ast
import io
import subprocess
import sys
import tokenize


def _strip_docstrings(tree: ast.AST) -> ast.AST:
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if not isinstance(body, list):
            continue
        node.body = [
            stmt
            for stmt in body
            if not (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and isinstance(stmt.value.value, str)
            )
        ] or [ast.Pass()]
    return tree


def _shape(source: str) -> str:
    return ast.dump(_strip_docstrings(ast.parse(source)))


def _comment_lines(source: str) -> int:
    count = 0
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type == tokenize.COMMENT and not tok.string.startswith("#!"):
                count += 1
    except (tokenize.TokenError, SyntaxError):
        return 0
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return count
    for node in ast.walk(tree):
        for stmt in (
            getattr(node, "body", [])
            if isinstance(getattr(node, "body", None), list)
            else []
        ):
            if (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and isinstance(stmt.value.value, str)
            ):
                count += (stmt.end_lineno or stmt.lineno) - stmt.lineno + 1
    return count


def main(argv: list[str]) -> int:
    mode, *rest = argv
    if mode == "inventory":
        for path in rest:
            text = open(path, encoding="utf-8").read()
            print(f"{path}\t{_comment_lines(text)}\t{len(text.splitlines())}")
        return 0
    rev, *paths = rest
    bad = 0
    for path in paths:
        try:
            before = subprocess.run(
                ["git", "show", f"{rev}:{path}"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout
        except subprocess.CalledProcessError:
            print(f"NEW FILE (not a comment edit): {path}")
            bad += 1
            continue
        after = open(path, encoding="utf-8").read()
        try:
            same = _shape(before) == _shape(after)
        except SyntaxError as err:
            print(f"SYNTAX ERROR: {path}: {err}")
            same = False
        if not same:
            print(f"CODE CHANGED: {path}")
            bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
