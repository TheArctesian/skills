# Python

## Standards adopted

| Source | What to take from it |
|---|---|
| [PEP 8](https://peps.python.org/pep-0008/) via `ruff format` | Formatting. |
| [Ruff rules](https://docs.astral.sh/ruff/rules/) | Pyflakes/pycodestyle errors (`E4`,`E7`,`E9`,`F`), import order (`I`), bugbear (`B`), pyupgrade (`UP`), simplify (`SIM`), McCabe complexity (`C90`), Pylint size and design checks (`PL`). Config lives in `ruff.toml` or `pyproject.toml`. |
| [PEP 257](https://peps.python.org/pep-0257/) | A one-line docstring stating what a module or public function does. |

## Idioms

- Typed boundaries: annotate public functions; parse untrusted input into
  dataclasses or pydantic models at the edge, not dicts passed inward.
- Exceptions are typed per domain (`class ReceiptError(Exception)`); never bare
  `except:` or `except Exception: pass`.

- One statement per line; no `if x: return` on one line (`E701`/`E702`).
- f-strings, not `%` formatting (`UP031`).
- `subprocess.run(..., check=True)` unless the exit status is handled
  explicitly (`PLW1510`).
- Imports at module top; a deferred import needs a reason (`PLC0415`).
- A script is a thin `main()` over importable functions, so tests import the
  functions rather than shelling out.
- Data shapes as `@dataclass(frozen=True)`; paths as `pathlib.Path`.

## Verify

```sh
ruff check . && ruff format --check .     # or the pinned `uvx ruff@<version>` the repo uses
<the repo's type checker, e.g. mypy or pyright>
<the repo's test runner, e.g. pytest or python -m unittest>
```
