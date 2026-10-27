# Cleanup targets

Where space goes on a macOS developer machine, which class each is (SKILL.md §2), and how to clean it.
`scan.sh` sizes every path in the first column of these tables, so keep one literal path per row (no globs).
Sources: this skill's own runs, plus the module lists of [Mole](https://github.com/tw93/Mole),
[mac-cleanup-py](https://github.com/mac-cleanup/mac-cleanup-py) and [kondo](https://github.com/tbillington/kondo).

Prefer the tool's command. Use `rm -rf` only where the table says the folder is a plain cache.

## Agent sessions (usually the largest)

| Path | What | Class | Clean with |
|---|---|---|---|
| `~/.codex/worktrees` | Codex worktrees, one per task, never removed | A after audit | `worktree-audit.sh` → `worktree-remove.sh` |
| `~/.claude/worktrees` | Claude Code worktrees outside a repo | A after audit | same |
| `~/Documents/Codex` | Codex desktop task folders, some holding worktrees | A after audit | same; non-worktree files are D |
| `~/.cursor/worktrees` | Cursor background-agent worktrees | A after audit | same |
| `~/conductor/workspaces` | Conductor workspaces | A after audit | same |
| `~/.codex/sessions` | Codex transcripts | D | leave unless asked |
| `~/.claude/projects` | Claude Code transcripts and memory | D | leave |
| `~/Library/Application Support/Claude/vm_bundles` | Claude desktop sandbox VM images | B | the app re-downloads; delete only with Claude quit |

In-repo `<repo>/.claude/worktrees/*` are found by `scan.sh` and audited the same way.

## Build output (inside repos and worktrees)

Found by `artifacts.sh`, which lists a folder only beside its manifest.

| Folder | Manifest | Notes |
|---|---|---|
| `target/` | `Cargo.toml` | Often 5–20 GB per checkout. Global alternative: `cargo sweep -r -t 14 ROOT` |
| `node_modules/` | `package.json` | `npx npkill` for an interactive picker |
| `.build/` | `Package.swift` | SwiftPM |
| `.next/`, `.svelte-kit/`, `.turbo/`, `.parcel-cache/` | `package.json` | |
| `.gradle/` | `build.gradle*` | project-level; the global one is below |
| `.dart_tool/` | `pubspec.yaml` | |
| `zig-cache/` | `build.zig` | |

`.venv/` is regenerable too but often holds hand-installed packages; list it, don't delete it by default.

## Docker

| Path | What | Class | Clean with |
|---|---|---|---|
| `~/Library/Containers/com.docker.docker` | `Docker.raw` sparse disk image; `ls -l` shows virtual size | B | `docker system df -v` first, then the commands below |
| `~/.colima` | Colima VM disk | B | `colima prune`, or the docker commands inside it |
| `~/.orbstack` | OrbStack data | B | `orb` / docker commands |

- Stopped containers: `docker container prune -f` (their named volumes survive).
- Images not used by a container: `docker image prune -a -f`; dangling only: `docker image prune -f`.
- Build cache: `docker builder prune -a -f`.
- Volumes: `docker volume rm NAME…` by name, only 0-link build caches (`*-target`, `*-cache`, `*node_modules*`,
  `*-store`). Never `docker volume prune -a` and never a `*pgdata*`/`*mysql*`/`*redis*`/`*data` volume (class D).
- `docker system prune -a --volumes` is too broad to run unasked.

## Apple developer tools

| Path | What | Class | Clean with |
|---|---|---|---|
| `~/Library/Developer/Xcode/DerivedData` | Xcode build output | A | `rm -rf` the folder (Xcode closed) |
| `~/Library/Developer/Xcode/Archives` | App archives with dSYMs | D | Organizer → Archives; keep shipped builds |
| `~/Library/Developer/Xcode/iOS DeviceSupport` | Symbols per connected iOS version | A | delete versions no device runs |
| `~/Library/Developer/Xcode/watchOS DeviceSupport` | same for watchOS | A | same |
| `~/Library/Developer/CoreSimulator/Devices` | Simulator devices | B | `xcrun simctl delete unavailable`; agent-made devices (non-stock names) by UDID with `xcrun simctl delete`; `xcrun simctl erase all` resets the rest |
| `~/Library/Developer/CoreSimulator/Caches` | Simulator dyld caches | A | `rm -rf` (regenerates on boot) |
| `~/Library/Caches/com.apple.dt.Xcode` | Xcode cache | A | `rm -rf` |
| `~/Library/Developer/XCPGDevices` | Playground simulators | A | `rm -rf` |

Simulator runtimes are separate APFS volumes (`diskutil apfs list`, ~17 GB each):
`xcrun simctl runtime list`, then `xcrun simctl runtime delete <id>` for versions nothing targets.
Old Xcodes in `/Applications/Xcode-*.app` are 10–40 GB each.

## Package managers and toolchains

| Path | What | Class | Clean with |
|---|---|---|---|
| `~/Library/Caches/Homebrew` | Bottle downloads | B | `brew cleanup --prune=all` (also `brew autoremove`) |
| `~/.npm` | npm cache | B | `npm cache clean --force` |
| `~/Library/pnpm/store` | pnpm store | B | `pnpm store prune` |
| `~/Library/Caches/Yarn` | Yarn classic cache | B | `yarn cache clean` |
| `~/.yarn/berry/cache` | Yarn berry cache | B | `yarn cache clean --all` |
| `~/.bun/install/cache` | Bun cache | B | `bun pm cache rm` |
| `~/.cache/uv` | uv cache | B | `uv cache prune` (keeps what's in use); `uv cache clean` for all. Fails on a lock if uv is running: report, don't `--force` |
| `~/Library/Caches/pip` | pip cache | B | `pip cache purge` |
| `~/Library/Caches/pypoetry` | Poetry cache | B | `poetry cache clear --all .` |
| `~/.pyenv/versions` | Python builds | D | `pyenv uninstall` versions nothing uses |
| `~/.cargo/registry` | Crate sources and downloads | B | `cargo cache -a` (cargo-cache), or `rm -rf ~/.cargo/registry/{cache,src}` |
| `~/.cargo/git` | Git dependencies | B | same |
| `~/.rustup/toolchains` | Rust toolchains | B | `rustup toolchain list`, `rustup toolchain uninstall` old nightlies |
| `~/go/pkg/mod` | Go module cache | B | `go clean -modcache` |
| `~/Library/Caches/go-build` | Go build cache | B | `go clean -cache` |
| `~/.gradle/caches` | Gradle cache | A | `rm -rf` with no Gradle daemon running (`gradle --stop`) |
| `~/.gradle/wrapper/dists` | Gradle distributions | A | delete old versions |
| `~/.m2/repository` | Maven repository | A | `rm -rf` (re-downloads) |
| `~/Library/Caches/CocoaPods` | CocoaPods cache | B | `pod cache clean --all` |
| `~/.android/avd` | Android emulators | D | Android Studio → Device Manager |
| `~/Library/Android/sdk/system-images` | Emulator images | B | `sdkmanager --uninstall` old images |
| `~/.nuget/packages` | NuGet cache | B | `dotnet nuget locals all --clear` |
| `~/.composer/cache` | Composer cache | B | `composer clear-cache` |
| `~/.gem` | Ruby gems | B | `gem cleanup` |
| `~/.deno` | Deno cache | B | `deno clean` |

Nix: the store is its own APFS volume. `nix-collect-garbage -d` (and `nix store optimise`) after
checking `nix-store --gc --print-roots` for roots that matter.

## Models and ML

| Path | What | Class | Clean with |
|---|---|---|---|
| `~/.cache/huggingface` | Hugging Face models and datasets | B | `hf cache scan` / `hf cache delete` (older: `huggingface-cli delete-cache`); ask per model, they are slow to re-download |
| `~/.ollama/models` | Ollama models | B | `ollama list`, `ollama rm NAME` |
| `~/.lmstudio/models` | LM Studio models | B | in the app |
| `~/.cache/torch` | PyTorch hub weights | A | `rm -rf` |
| `~/.cache/whisper` | Whisper weights | A | `rm -rf` |

## Browser and app caches (plain caches)

| Path | What | Class | Clean with |
|---|---|---|---|
| `~/Library/Caches/ms-playwright` | Playwright browsers | A | `npx playwright uninstall --all` |
| `~/.cache/puppeteer` | Puppeteer browsers | A | `rm -rf` |
| `~/Library/Caches/Google` | Chrome cache | A | `rm -rf` with Chrome quit (profiles live elsewhere) |
| `~/Library/Caches/com.spotify.client` | Spotify stream cache | A | Spotify → Settings → Storage |
| `~/Library/Application Support/Slack/Cache` | Slack cache | A | `rm -rf` with Slack quit |
| `~/Library/Application Support/Code/Cache` | VS Code cache | A | `rm -rf` with VS Code quit |
| `~/Library/Application Support/Code/CachedData` | VS Code compiled cache | A | same |
| `~/Library/Logs` | App logs | A | delete files older than 30 days |

`~/Library/Caches/*` in general is regenerable, but a few apps keep state there; clean named
subfolders, not the whole directory.

## Personal data (class D: report, never delete)

| Path | What | Where the person cleans it |
|---|---|---|
| `~/Library/Group Containers/group.net.whatsapp.WhatsApp.shared` | WhatsApp media | WhatsApp → Settings → Storage and Data → Manage Storage |
| `~/Library/Messages` | iMessage attachments | Messages → Settings → General → Keep messages; or System Settings → General → Storage → Messages |
| `~/Library/Containers/com.apple.MobileSMS` | Messages data | same |
| `~/Library/Application Support/MobileSync/Backup` | iPhone/iPad backups | Finder → device → Manage Backups |
| `~/Library/Containers/com.apple.mail` | Mail downloads | Mail → Settings; or delete large attachments in Mail |
| `~/Pictures` | Photos library | Photos; check iCloud "Optimize Mac Storage" |
| `~/Library/Mobile Documents` | iCloud Drive local copies | Finder → Remove Download (keeps the iCloud copy) |
| `~/Library/Application Support/Steam` | Games | Steam → Storage |
| `~/Library/Application Support/UnityHub` | Unity editors | Unity Hub → Installs |
| `~/Downloads` | Downloads | Installers and extracted archives are class C after their checks; everything else is D |
| `~/.Trash` | Trash | the person empties it |

## System (report only)

- Time Machine local snapshots: `tmutil listlocalsnapshots /`; they purge themselves under pressure.
  `tmutil thinlocalsnapshots / 999999999999 4` asks the system to thin them.
- "Purgeable" space in Finder is reclaimed by macOS on demand; `df` already counts it as used.
- `/Library`, `/private/var`, `/System`: out of scope (needs sudo, SIP-protected).
