# Driver contract

Every persona sees the same five kinds of action whatever the platform. The persona agent files in `agents/` carry the
behavioural half of this contract as their system prompt, because persona agents cannot read files.

| Kind | Web (Playwright MCP) | iOS (mobile-mcp) |
|---|---|---|
| observe | `browser_snapshot`, `browser_take_screenshot` | `mobile_list_elements_on_screen`, `mobile_take_screenshot` |
| act | `browser_click`, `browser_type`, `browser_fill_form`, `browser_press_key`, `browser_select_option`, `browser_hover`, `browser_drag`, `browser_navigate_back` | `mobile_click_on_screen_at_coordinates`, `mobile_type_keys`, `mobile_swipe_on_screen`, `mobile_long_press_on_screen_at_coordinates`, `mobile_press_button` |
| lifecycle | `browser_navigate` (start URL only) | `mobile_launch_app`, `mobile_terminate_app`, `mobile_open_url` (start link only); install and reset happen outside the persona in `scripts/device-pool.sh prep` |
| system | `browser_emulate_media` (dark mode) | `simctl ui` settings applied by `prep` before the session |
| record | the structured step log | the structured step log; the harness screenshots the end state |

## Blinding

Each persona agent type has a `tools` allowlist of its driver's tools only (plus ToolSearch to load them), its own
`mcpServers` entry so it gets a private browser or device connection, and `omitClaudeMd: true`. It has no Read, Grep,
Glob, Bash or Edit, so it cannot reach the repository. Deliberately excluded: `browser_evaluate`,
`browser_run_code_unsafe`, `browser_console_messages`, `browser_network_requests` (they expose the code or its errors),
`browser_file_upload`, `mobile_install_app`, `mobile_uninstall_app`, device logs and crash reports.

Web agents run `--isolated --headless`, so each session starts with an empty in-memory profile. Isolation of backend
state comes from one throwaway account per persona.

## What is prompt-only

- Staying on the assigned simulator: mobile-mcp takes a device id on every call, so a persona could address another.
  The workflow checks `devices_used` against the assignment and marks findings from stray sessions uncertain.
- Reading and scrolling limits. Wrong-turn and backtrack limits are enforced from the log afterwards.

## Agent types

| Driver | Agent type | Notes |
|---|---|---|
| `web-desktop` | `persona-web-desktop` | 1280×800 |
| `web-mobile` | `persona-web-mobile` | `--device "iPhone 15"`: viewport, touch, mobile user agent |
| `web-tree` | `persona-web-tree` | no screenshot tool |
| `ios` | `persona-ios` | |
| `ios-tree` | `persona-ios-tree` | no screenshot tool |

Install with `scripts/install-agents.sh`, then start a new session. Plugins cannot ship these: plugin agents ignore
`mcpServers`.
