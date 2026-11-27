---
id: ADR-0004
layer: L2
status: accepted
date: 2026-11-26
decision-makers: SOTA Convergence Swarm (Verified 2026-11-26)
consulted: [sota-ecosystem, cross-session, changelogs, best-practices]
informed: [verifier, coordinator]
---

# ADR-0004: Multi-Surface Google Antigravity Harness, 7 IDE Extensions & ACP Interoperability (`L2`)

## Context and Problem Statement

Layer `L2` defines the developer-facing agent harness surfaces—how engineers and automated pipelines launch sessions, inspect diffs/artifacts, attach context, load customizations (`.agents/`, `~/.gemini/config/`), and integrate with existing IDEs without causing surface drift or editor lock-in.

Since Google I/O on May 19, 2026, Google Antigravity split from a monolithic VS Code fork into **five official product surfaces** sharing one underlying agent harness (`https://antigravity.google/llms.txt`): **Antigravity App (2.0)**, Go-based **Antigravity CLI (`agy`)**, **Antigravity Extensions** (7 IDE integrations), **Antigravity Python SDK (`google-antigravity`)**, and standalone **Antigravity IDE**. Simultaneously, legacy consumer **Gemini CLI** stopped serving individual/Google AI Pro/Ultra accounts on **June 18, 2026** (`https://github.com/google-gemini/gemini-cli/blob/main/README.md`), and the industry converged on **Agent Client Protocol (`ACP`)** (Zed + JetBrains, v2 Preview Nov 20, 2026) as "LSP for AI coding agents."

Without a strict `L2` architecture decision, teams suffer three failure modes: (1) fragmenting skills/rules across incompatible IDE-only or CLI-only paths (`~/.gemini/skills/` shadowing `~/.gemini/config/skills/`), (2) deploying standalone Antigravity IDE in Gemini Enterprise environments where Enterprise sign-in is unsupported (`faq.md`, `enterprise.md`), or (3) building brittle custom PTY wrappers around CLIs instead of using `agy -p --output-format stream-json`, `agy acp`, or the Python SDK.

## Decision Drivers

- **Single Shared Customization Graph Across All Surfaces:** Write rules (`AGENTS.md`, `.agents/rules/*.md`), skills (`.agents/skills/*/SKILL.md`), hooks (`hooks.json`), plugins (`plugin.json`), and MCP configs (`mcp_config.json`) once and share them seamlessly across App, CLI, IDE Extensions, and SDK.
- **Zero Editor Lock-In via Native ACP (`agy acp`):** Support engineers in VS Code, Visual Studio, Eclipse, JetBrains, Android Studio, Zed, and Xcode without forcing IDE migration.
- **Enterprise Auth & Governance Parity:** Ensure every recommended enterprise surface supports Gemini Enterprise / Workforce Identity Federation (WIF), regional inferencing, and `admin_settings.json` policy controls.
- **Right Surface Per Task Modality:** Match visual/browser/MCP-App workflows to App 2.0, fast terminal/SSH/CI pipelines to `agy`, inline code edits to IDE Extensions, and embedded programmatic automation to `google-antigravity`.
- **Zero Custom Harness Wrapper Self-Invention:** Ban ad-hoc PTY screen-scrapers, custom CLI wrappers, and legacy consumer Gemini CLI tooling.

## Considered Options

1. **Option 1 (Chosen): Unified AGY Multi-Surface Harness (`App 2.35.2` + Go `agy 1.5.18` + `7` IDE Extensions / `agy acp` + Python SDK `0.1.24`), Canonical Shared Customizations (`~/.gemini/config/` & `.agents/`), and Enterprise Exclusion of Standalone IDE.**
2. **Option 2 (Rejected): Standalone Antigravity IDE (`v2.8.0`) as the Sole Standardized Surface Across Personal and Enterprise Teams.**
3. **Option 3 (Rejected): Legacy Gemini CLI (`@google/gemini-cli`) + Custom Python/Shell PTY Wrappers Around Interactive Terminals.**
4. **Option 4 (Rejected): Proprietary Single-Vendor IDE Fork Exclusively (e.g., standardizing on Cursor or Devin Desktop alone without ACP interoperability).**

## Decision Outcome

Chosen option: **Option 1 — Unified AGY Multi-Surface Harness with Shared Customization Graph & Native ACP**, because it aligns every surface to one verified upstream runtime, eliminates editor lock-in via `agy acp` and 7 official IDE extensions, cleanly enforces Enterprise auth boundaries, and replaces all legacy Gemini CLI and custom PTY glue.

Canonical surface routing contract at `L2`:

| Surface | Pinned Version (2026-11-26) | Canonical Role | Enterprise Auth | Customization Root Contract |
| :--- | :--- | :--- | :---: | :--- |
| **Antigravity App (2.0)** | `2.35.2` | Multi-agent desktop command center, visual diff/artifact review, built-in browser QA, Voice Mode, Sidecars/Automations, MCP Apps (`SEP-1865`), SSH hosts | Yes (WIF/SSO/PAYG) | Workspace `.agents/` + `<repo>/.gemini/config.json`; Personal `~/.gemini/config/` (symlinked to `~/.agents/skills/`) |
| **Antigravity CLI (`agy`)** | `1.5.18` (GitHub/local) / `1.5.16` (docs) | Terminal-first interactive TUI, SSH sessions, headless CI (`agy -p --output-format stream-json --json-schema`), **`agy acp`** stdio JSON-RPC server | Yes (WIF/SSO/ADC/API Key) | Same canonical roots; **ban** divergent hard copies in CLI-only `~/.gemini/skills/` or `~/.gemini/antigravity-cli/skills/` |
| **IDE Extensions (7 IDEs)** | VS Code `1.13.0`, Visual Studio `1.0.261116.0` (VS 2022 `17.14+` or VS 2026), Eclipse `1.2.0`, JetBrains/Zed/Xcode `antigravity-acp 1.5.0`, Android Studio ACP Registry | Native in-editor inline diffs, `@terminal` context pills, editor comments, and ACP-native agent panels without leaving preferred IDEs | Yes (Android Studio Preview) | Shares workspace `.agents/` & personal `~/.gemini/config/` |
| **Antigravity Python SDK** | `google-antigravity==0.1.24` (PyPI wheel) | Programmatic local/CI agent pipelines, custom Python tools, structured Pydantic outputs, `LiteRTAgentConfig`, native OTel tracing | Yes (`vertex=True` / Express Mode / `GEMINI_API_KEY`) | Declarative `LocalAgentConfig` (`skills_paths` or `inline_skills`, never both) |
| **Antigravity IDE (Standalone)** | `2.8.0` | **Optional personal/consumer fallback only** (lightweight all-in-one editor) | **No** (excluded by `faq.md` & `enterprise.md`) | Workspace `.agents/` + personal `~/.gemini/config/` |

### Consequences

- **Good:** Eliminates "IDE vs. CLI vs. CI drift" by converging all surfaces onto `.agents/` (workspace) and symlink-unified `~/.agents/skills/` → `~/.gemini/config/skills/` (personal, cross-tool AAIF parity).
- **Good:** Native `agy acp` (strictly the subcommand `agy acp`, with no `--acp` flag) future-proofs editor workflows across JetBrains, Zed, Xcode, Android Studio, and ACP v2 Preview clients without vendor lock-in.
- **Good:** Prevents enterprise deployment blockers by explicitly routing Gemini Enterprise / Google Cloud teams to App, CLI, and the 7 IDE Extensions rather than standalone Antigravity IDE.
- **Bad:** Certain rich UI features remain App-only (`MCP Apps` `ui://` iframe rendering, Sidecars, built-in visual browser, full-page Voice Mode), requiring plain-text `content` fallbacks in MCP tools consumed by CLI/IDE surfaces.
- **Bad:** Upstream `changelog.md` can lag GitHub CLI releases by 1–2 patches (`v1.5.16` vs `v1.5.18`), requiring teams to monitor GitHub Releases (`google-antigravity/antigravity-cli`) and PyPI (`google-antigravity`) directly for exact pins.
- **Neutral:** Users migrating from consumer Gemini CLI must run `agy plugin import gemini`, move `.gemini/skills/` → `.agents/skills/`, and move inline MCP configs to `mcp_config.json` with `serverUrl`.

### Confirmation

Run the following executable verification commands from the repository root (every command must exit `0`):

```bash
# 1. Verify pinned Antigravity App (macOS) and CLI versions + ACP subcommand availability
defaults read /Applications/Antigravity.app/Contents/Info.plist CFBundleShortVersionString | grep -qx "2.35.2"
agy --version | grep -qx "1.5.18"
agy acp --help >/dev/null

# 2. Verify headless structured print mode flags
agy --help | grep -q -- "--output-format"
agy --help | grep -q -- "--json-schema"

# 3. Verify zero legacy .agents/settings.json (silently ignored since App v2.17.0) or legacy workflows
test ! -f .agents/settings.json
test ! -d .agents/workflows

# 4. Run zero-secret host ecosystem hygiene auditor & sealed manifest gate
python3 scripts/audit_ecosystem_hygiene.py --json >/dev/null
python3 scripts/verify_manifest.py --verify
```

## Pros and Cons of the Options

### Option 1: Unified AGY Multi-Surface Harness (`App` + `agy` + `7` IDE Extensions / `agy acp` + `Python SDK`)

- **Pro:** Passes all 5 Zero-Self-Invention tests cleanly: 100% official first-party binaries/wheels/extensions, shared `.agents/` & `~/.gemini/config/` customization schema, clean install without forks, and native `agy acp` open-protocol interoperability.
- **Pro:** Covers interactive GUI, headless CI (`stream-json` + `--json-schema`), SSH remote servers, 7 major IDEs, and embedded Python pipelines under one authentication and permission engine.
- **Con:** Requires disciplined symlink/single-root hygiene on workstations so CLI-only `~/.gemini/skills/` copies do not silently shadow `~/.gemini/config/skills/` (monitored continuously by `scripts/audit_ecosystem_hygiene.py`).

### Option 2: Standalone Antigravity IDE (`v2.8.0`) as Sole Surface

- **Pro:** Single desktop binary for individual developers who prefer VS Code.
- **Con (Disqualifying):** Does **not** support Gemini Enterprise sign-in (`faq.md`, `enterprise.md`), lacks App 2.0's Sidecars, MCP Apps `ui://` rendering, Voice Mode, SSH Host command center, and `/swarm` board, and alienates JetBrains, Visual Studio, Eclipse, Xcode, Android Studio, and Zed developers.

### Option 3: Legacy Gemini CLI + Custom PTY/Subprocess Wrappers

- **Pro:** Familiar to pre-May-2026 Gemini CLI users.
- **Con (Disqualifying):** Consumer tiers (Free, Google AI Pro/Ultra) were cut off on `2026-06-18`; `google-gemini/gemini-cli` explicitly states it is **not tuned for Gemini 4+**; custom PTY wrappers fail the Zero-Self-Invention Gate by duplicating `agy -p --input-format stream-json --output-format stream-json` and `google-antigravity`.

### Option 4: Single-Vendor Proprietary IDE Fork Exclusively

- **Pro:** Polished editor experience inside one IDE fork.
- **Con (Disqualifying):** Imposes editor lock-in, breaks multi-IDE enterprise fleets (`.NET`/Visual Studio, Java/Eclipse/JetBrains, Apple/Xcode, Android Studio), and lacks native integration with AGY's unified App/CLI/SDK/MCP-Apps ecosystem.

## Clean Upstream Installation & Adapter Boundary

Aligned 1:1 with [`../clean-install-registry.md`](../clean-install-registry.md) (`L2`), [`../../mise.toml`](../../mise.toml), and [`../../pyproject.toml`](../../pyproject.toml):

- **Antigravity App (`2.35.2`):** Install OS package from `https://antigravity.google/download` (macOS ARM64 DMG: `https://storage.googleapis.com/antigravity-public/antigravity-hub/2.35.2-4585983447007232/darwin-arm/Antigravity.dmg`). Verify with `defaults read /Applications/Antigravity.app/Contents/Info.plist CFBundleShortVersionString`.
- **Antigravity CLI (`agy` `1.5.18`):**
  ```bash
  # Official macOS / Linux installer (or mise pin: mise use -g agy@1.5.18)
  curl -fsSL https://antigravity.google/cli/install.sh | bash
  agy --version && agy acp --help
  ```
- **Antigravity Python SDK (`google-antigravity==0.1.24`):**
  ```bash
  uv add google-antigravity==0.1.24
  uv run python -c "import google.antigravity; print('ok')"
  ```
- **7 Official IDE Extensions:**
  - **VS Code (`1.13.0`, VS Code `1.90+`):** `code --install-extension Google.google-antigravity@1.13.0`
  - **Visual Studio (`1.0.261116.0`, VS 2022 `17.14+` or VS 2026):** Install `Google.GoogleAntigravity` VSIX via Extensions Manager
  - **Eclipse (`1.2.0`, Eclipse `2026-06+`):** Install `Google Antigravity` from Eclipse Marketplace
  - **JetBrains (`2026.2.1+`), Zed (`0.140.0+`), Xcode (`27 beta 6+`), Android Studio (ACP Registry):** Install `antigravity-acp` (`1.5.0`) via each IDE's native Agent/ACP Registry or register `command: "agy", args: ["acp"]`
- **Thin Adapter Boundary:** Repository customizations stay strictly declarative inside `.agents/` (`AGENTS.md`, `rules/*.md`, `skills/<name>/SKILL.md`, `hooks.json`, `mcp_config.json`, `plugins/`) and `<repo>/.gemini/config.json`. Never wrap `agy` inside custom interactive PTY harnesses, never hand-edit atomic `~/.gemini/config/config.json`, and never install `google-antigravity` from raw GitHub source without its PyPI runtime wheel.

## More Information

- Official AGY Sitemap & 5 Products: `https://antigravity.google/llms.txt`
- Official AGY Get Started & Installers: `https://antigravity.google/docs/getting-started.md`
- Official AGY Overview & Surfaces: `https://antigravity.google/docs/overview.md`
- Official IDE Extensions & ACP Docs: `https://antigravity.google/docs/ide/extensions.md`, `https://antigravity.google/docs/ide/extensions/acp.md`, `https://antigravity.google/docs/ide/extensions/visual-studio.md`, `https://antigravity.google/docs/ide/extensions/eclipse.md`, `https://antigravity.google/docs/ide/extensions/android-studio.md`
- Official Enterprise & FAQ Boundaries: `https://antigravity.google/docs/enterprise.md`, `https://antigravity.google/docs/faq.md`
- Gemini CLI Transition & Migration: `https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/`, `https://antigravity.google/docs/cli/gcli-migration.md`, `https://github.com/google-gemini/gemini-cli/blob/main/README.md`
- Upstream CLI Releases & Python SDK PyPI: `https://github.com/google-antigravity/antigravity-cli/releases/tag/1.5.18`, `https://pypi.org/project/google-antigravity/0.1.24/`
- Agent Client Protocol Updates (v2 Preview): `https://agentclientprotocol.com/updates`
- Repository Cross-References: [`../clean-install-registry.md`](../clean-install-registry.md), [`../convergence-stack.md`](../convergence-stack.md), [`../manifest-guide.md`](../manifest-guide.md).
