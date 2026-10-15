# Rust

## Standards adopted

| Source | What to take from it |
|---|---|
| [rustfmt](https://github.com/rust-lang/rustfmt) | Formatting, unconfigured. |
| [Clippy](https://doc.rust-lang.org/clippy/) `pedantic` | Enable crate-wide in `Cargo.toml` `[lints]`; CI denies warnings. Thresholds stay at Clippy's defaults (`too_many_lines` 100, `too_many_arguments` 7, `struct_excessive_bools` 3). |
| [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/) | Naming (C-CASE, C-CONV `as_`/`to_`/`into_`, C-GETTER without `get_`), common traits (C-COMMON-TRAITS), `From` conversions, typed errors (C-GOOD-ERR). |
| [Microsoft Pragmatic Rust Guidelines](https://microsoft.github.io/rust-guidelines/) | Balanced modules (essentials at the root, the rest grouped semantically), no weasel words (`Service`, `Manager`), short names that do not repeat their module, panics only for bugs, `allow_attributes_without_reason`. |
| [matklad, "Delete Cargo Integration Tests"](https://matklad.github.io/2021/02/27/delete-cargo-integration-tests.html) | One integration-test crate with modules (`tests/it/main.rs`) rather than one binary per file: faster links, shared fixtures, and folders that mirror `src/`. |

For a service or binary crate, `missing_errors_doc`, `missing_panics_doc` and
`must_use_candidate` may be allowed with a reason: they target published library
APIs. Pick one module layout (`foo/mod.rs` or `foo.rs` + `foo/`) and enforce it
with `self_named_module_files` or `mod_module_files`.

## Module layout

- A domain is a directory: `src/finance/` with `mod.rs` holding the domain's
  public face (types and the router) and submodules for each concept.
- `mod.rs` declares and re-exports; once it passes ~100 lines of logic, move
  the logic into a named submodule.
- Group HTTP handlers per resource: `finance/receipts/routes.rs` next to
  `finance/receipts/store.rs` (SQL) and pure logic (`finance/receipts/match.rs`).
  Handlers parse, call, and map errors; they do not contain business rules.
- SQL lives with the domain that owns the table, in a `store.rs` (or
  `sql.rs`) module; callers use its functions, never raw queries.
- Unit tests for a large module go in a sibling `tests.rs`
  (`#[cfg(test)] mod tests;`) so the source file stays readable.
- Visibility: default private, `pub(crate)` for cross-domain use, `pub` only for
  what `main.rs`/tests need.

## Seams for a long file or function

- **Pure core versus I/O.** Extract computation (parsing, matching, scheduling,
  money arithmetic) into functions taking owned/borrowed data, returning
  values. Leave `sqlx`/`reqwest` calls in thin async wrappers.
- **One `match` arm per variant is a table.** Long matches mapping variants to
  data become a method on the enum or a `const` table.
- **Builder or params struct** when a function needs more than ~5 related
  arguments; name the struct for the concept (`ReceiptQuery`), not `Args`.
- **Pipeline stages.** A 150-line async function that fetches, transforms,
  writes, and notifies becomes four functions called in sequence.
- **Enums over bool flags** (`struct_excessive_bools`, `fn_params_excessive_bools`).

## Errors and panics

- Return the crate's error type (`Result<_, AppError>`) across module boundaries; implement `From` for
  upstream errors instead of repeating `map_err`.
- `unwrap`/`expect` only on invariants the code itself established, with an
  `expect` message stating the invariant. Never on input, env, or I/O.
- Casts: prefer `try_from` with a handled error; an `as` cast that truncates
  needs `#[expect(clippy::cast_possible_truncation, reason = "...")]`.

## Verify

```sh
cargo fmt --check
cargo clippy --all-targets -- -D warnings
cargo test
```

Integration tests that need a database run against a throwaway instance, never a shared one.
