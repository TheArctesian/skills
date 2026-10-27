---
name: macos-cleanup
description: Find and reclaim wasted disk space on a macOS developer machine — stale git worktrees left by Claude Code and Codex sessions, Rust target/ and node_modules build output, Docker volumes, images and stopped containers, agent-created iOS simulators, package-manager and model caches, installers and already-extracted archives in Downloads. Measures first, classifies every item by how safely it regenerates, proves each deletion safe with scripts (worktree dirty/unpushed audit immune to stale .git pointers, archive-fully-extracted check, in-use checks), asks before deleting, and remeasures. Use when the disk is full or nearly full, "Mac is running out of space", "what is using my storage", "clean up worktrees", "clear caches", "free up disk", or for periodic junk cleaning.
---

# macOS cleanup

Free the most space for the least risk. Every byte removed is either regenerable by a tool or
proven redundant by a check; nothing personal is deleted on a guess.

The order never changes: **measure → classify → verify → approve → delete → remeasure.**

## 1. Measure (read-only)

```sh
bash <skill_dir>/scripts/scan.sh                 # default code roots: ~/Scripts ~/Projects ~/code ~/src ~/dev ~/Developer
bash <skill_dir>/scripts/scan.sh ~/work ~/oss    # or name the roots that hold repositories
```

It prints free space, the biggest home and `~/Library` folders, Docker, simulators, known caches
(sized from [references/targets.md](references/targets.md)), worktree roots, build artifacts and big
Downloads, and writes TSVs to a scratch directory it names. It takes minutes on a large disk:
run it in the background and wait for the notification.

Account for the gap. `df` used minus what the scan found is space somewhere unscanned (another
volume, `/Library`, `/private/var`, Time Machine local snapshots, an APFS volume in
`diskutil apfs list`). Name the gap rather than ignore it.

## 2. Classify

Put every item over ~1 GB in exactly one class. The class decides who deletes it and how.

| Class | Meaning | Who deletes | Examples |
|---|---|---|---|
| **A. Regenerable** | Rebuilt or re-downloaded by a tool on demand | Claude, after approval | `target/`, `node_modules`, DerivedData, Docker build cache and dangling images, package caches, worktrees with no unique work |
| **B. Tool-owned** | Regenerable, but the owning tool must do it | Claude, through that tool's command | Docker volumes and images, simulators, Homebrew, uv, Nix store, Hugging Face cache, Time Machine snapshots |
| **C. Redundant copy** | A second copy proven identical or already applied | Claude, after the proof script passes | Installers for installed apps, archives whose every file is extracted |
| **D. Personal** | The only copy of the person's data | The person, in the owning app | WhatsApp/Messages media, Photos, iOS backups, Mail, Downloads documents, databases |

Never move an item from D to A because it is large or old. Hand class D back with the size and
the exact in-app path to clean it (`references/targets.md` lists them).

## 3. Verify

Each class has a check. Run it; do not reason your way past it.

**Worktrees** — the biggest offender: every agent session makes one and none clean up.

```sh
bash <skill_dir>/scripts/worktree-audit.sh ~/Scripts > audit.tsv    # repos under the roots + ~/.codex/worktrees etc.
```

Columns: `repo path branch dirty unpushed last_commit active state`. A worktree is removable
only when `state` is `ok` or `moved`, `dirty=0`, `unpushed=0` and `active=no`. The script reads each
worktree through its repo's own `.git/worktrees/<name>` record, so a stale `.git` file cannot read
as "0 changes". States:

- `ok`, `locked` — normal; locked is never removed.
- `moved` — the repo or worktree was renamed or moved; audited through the old record, paired only
  on a unique match of record name and folder name.
- `missing` — a record whose folder is gone; `git worktree prune` clears it.
- `error` — git cannot read it; treat as unknown.
- `orphan` — a folder no repo has a record for (renamed and pruned). It cannot be audited: delete only
  its build artifacts and report the rest.

`unpushed` counts commits on no remote branch, so a squash-merged branch still counts; keep it and
list it rather than assume.

**Build artifacts** — only directories a manifest proves are output:

```sh
bash <skill_dir>/scripts/artifacts.sh list ROOT... > artifacts.tsv   # size  kind  path
```

`target` counts only beside a `Cargo.toml`, `node_modules` beside a `package.json`, `.build`
beside a `Package.swift` (the kondo rule). Exclude anything under an active worktree.

**Archives in Downloads** — numbered siblings (`x.zip`, `x-2.zip`, …) are usually *parts* of one
export, not duplicates:

```sh
python3 -I <skill_dir>/scripts/zip-extracted.py ARCHIVE.zip... -- EXTRACTED_DIR...
```

It matches each entry by name, size and the CRC32 the zip stores. Delete an archive only when it
prints `FULLY-EXTRACTED`. An archive with missing files may be the only copy; say so.

**Installers** — delete a `.dmg`/`.pkg`/app `.zip` only when the app is in `/Applications` or
`~/Applications`.

**Docker** — `docker system df -v` shows `LINKS` per volume. A volume with 0 links and a name
ending `-target`, `-cache`, `node_modules` or `-store` is build cache; a volume named `*pgdata`,
`*mysql*`, `*redis*`, `*data` holds a database and is class D however unused it looks.

## 4. Approve

One AskUserQuestion, `multiSelect: true`, one option per group with its size and what regenerates
it ("Docker caches (~310 GB) — 3 unused *-target volumes, stopped containers, images, build
cache; Postgres volumes kept"). Recommend the class A/B groups. List class D in the message, not
as options. Approval covers exactly the groups chosen; a new group found later is a new question.

## 5. Delete

- Prefer the owning tool's command over `rm` (table in `references/targets.md`): `docker volume rm`,
  `xcrun simctl delete`, `uv cache prune`, `brew cleanup --prune=all`, `nix-collect-garbage`.
- Worktrees: `bash <skill_dir>/scripts/worktree-remove.sh < audit.tsv` (the whole audit; it skips what
  is not removable and says why). It re-checks each worktree immediately before removal and uses plain
  `git worktree remove` (never `--force`), so git refuses anything dirty, untracked or locked. It runs
  `git worktree repair` on every `moved` worktree it keeps; only after that is `git worktree prune`
  per repo safe, because prune deletes the record of any worktree whose recorded path is gone.
- Artifacts: `bash <skill_dir>/scripts/artifacts.sh delete artifacts.tsv`. It refuses any path whose
  kind and manifest no longer match.
- Run long deletions in the background; start the next one only after the previous finishes when
  they touch the same tree.
- If a tool holds a lock (`uv`, `brew`, `docker` busy), report it and move on. Never `--force` past a lock.

## 6. Remeasure and report

`df -h /System/Volumes/Data` before and after. Report: free space before → after, what was removed
per group, what was kept and why (class D with sizes and in-app paths, worktrees with work, anything
a check refused), and what will keep regrowing (agent worktrees, Docker build volumes, simulators).

## Pitfalls (each one happened)

- **zsh does not word-split.** `G="git --git-dir=x"; $G status` runs a command named `git --git-dir=x`
  and fails silently, and `for r in $list` passes one argument with newlines. Run loops with
  `bash -c` or the scripts here; pass lists through `xargs`.
- **A failed git command counts as clean.** `git status --porcelain | wc -l` prints `0` when git
  errors. Check `rev-parse HEAD` first and treat an error as unknown.
- **Stale `.git` pointers.** Renaming a repo leaves every worktree's `.git` file pointing at the old
  path. `git worktree list` still lists them, `git -C` on them fails. Go through the admin dir.
- **`git worktree prune` after a rename destroys records.** Every worktree of a moved repo looks
  prunable. Repair the ones you keep first (`worktree-remove.sh` does), or they become unauditable orphans.
- **Your own scan makes things look active.** `git status` rewrites the worktree index, so index mtime
  after a scan means nothing. Judge activity by last commit date and newest working file, outside
  `.git` and build output, as `worktree-audit.sh` does.
- **Numbered archives are parts.** `mydata~…zip`, `-2.zip` … `-5.zip` were five different parts of one
  export, and one part had never been extracted.
- **`du` over a sparse disk image lies in both directions.** `Docker.raw` reports its virtual size in
  `ls -l` (1.8 TB) and its allocated size in `ls -s`/`du`. Read `docker system df`; space returns
  to macOS after a prune as the file is trimmed.
- **Do not use `sudo`.** Permission prompts refuse it, and nothing user-owned needs it. System-owned
  locations are out of scope.
- **`du` on a whole home takes many minutes.** Fan out per top-level folder with `xargs -P`, and run it
  in the background.

## Never

- `rm -rf` a path that came from a glob or a variable that could be empty; build lists, check them
  against a pattern, then delete.
- Delete inside `~/Library/Group Containers`, `~/Library/Messages`, `~/Library/Mobile Documents`,
  `~/Pictures`, `MobileSync/Backup`, or any database volume or folder.
- Touch a main checkout, or a worktree that is active, dirty, unpushed, locked or unaudited.
- Empty the Trash, clear browser profiles or log people out without being asked.
