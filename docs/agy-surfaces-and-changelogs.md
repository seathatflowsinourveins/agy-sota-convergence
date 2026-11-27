# Google Antigravity (AGY) Surfaces, Changelogs, Sunsets & Drift Guardrails

**Verified Baseline:** 2026-11-26  
**Scope:** Canonical cross-surface reference for Google Antigravity's five official product surfaces, seven IDE integrations, 2025–2026 capability waves, time-bound deprecation/sunset calendar, and upstream documentation-drift guardrails.  
**Authoritative Live Sources:** `https://antigravity.google/llms.txt`, `https://antigravity.google/docs/changelog.md` (5 product headings, 270 versioned entries), `https://github.com/google-antigravity/antigravity-cli/releases`, `https://pypi.org/pypi/google-antigravity/json`, `https://antigravity.google/docs/models.md`, and `https://blog.modelcontextprotocol.io/posts/2026-07-28/`.

---

## 1. Strategic Evolution Arc (Nov 2025 – Nov 26, 2026)

Google Antigravity evolved across three architectural eras in its first twelve months:

1. **Era 1 — Monolithic AI IDE (`2025-11-18` – `2026-04-16`; IDE `v1.11.2` – `v1.23.2`):**  
   Launched as a VS Code-derived standalone IDE with an embedded Agent Manager, Chrome browser loop, rich Artifacts, and knowledge management. Key 1.x milestones introduced Secure/Strict Mode (`v1.11.17`), Gemini 3 Flash (`v1.12.4`), Agent Skills (`v1.14.2`, `2026-01-13`), macOS (`v1.15.6`) and Linux (`v1.21.6`) terminal sandboxing, Gemini 3.1 Pro (`v1.18.3`), Nano Banana 2 (`v1.19.6`), `AGENTS.md` rule support (`v1.20.5`), and the unified Agent Permissions engine (`v1.22.2`).
2. **Era 2 — Antigravity 2.0 Multi-Surface Split (`2026-05-19` – `2026-09-30`):**  
   At Google I/O on May 19, 2026, Antigravity unbundled around one shared core agent harness into **five product surfaces**: standalone **Antigravity App** (`v2.0.1+`), Go-based **Antigravity CLI** (`agy`, superseding consumer Gemini CLI on `2026-06-18`), Apache-2.0 **Antigravity Python SDK** (`google-antigravity` `0.1.0+`), refreshed **Antigravity IDE** (`v2.0.1+`), and first-party **IDE Extensions** starting `2026-08-18` (VS Code, Visual Studio, ACP-powered JetBrains/Zed/Xcode, plus Eclipse on `2026-10-27` and Android Studio via ACP Registry). Era 2 delivered Gemini Enterprise & Workforce Identity Federation (Jul 31 – Aug 3), Remote Control (Aug 20), Generative UI (Aug 26), Windows sandboxing/WSL (Sep 19–22), `/plan` + dedicated `20,000`-token rules budget (Sep 22), SDK local models (`LiteRTAgentConfig` / `LocalOpenAIAgentConfig`, Jul 9 – Sep 21), and the Plugin Marketplace (Sep 28).
3. **Era 3 — Frontier Gemini 4, Multi-Agent Orchestration & Platform Expansion (`2026-10-01` – `2026-11-26`):**  
   Shipped the **Gemini 4 element series** (`Argon` Oct 13 → `Carbon` Nov 10 → `Hydrogen` Nov 12 → `Neon` Nov 18) with the dual-model **Orchestrator**, **Auto permission mode** GA (CLI `v1.3.5` / default `v1.5.7`; App GA `v2.30.0`), **UI Extensions & MCP Apps** (`v2.22.0` / `v2.34.0`), **Voice Mode (Gemini Live)** and **Cloud Remote Agents** (`v2.29.0`–`v2.30.0`, CLI `v1.5.0`), **Native Swarms (`/swarm`)** (`v2.31.0`, CLI `v1.5.5`), **Dynamic Workflows (`/run-workflow`)** (SDK `v0.1.22`, App `v2.32.0`, CLI `v1.5.9`), **SSH Host Connections** (`v2.33.0`), **Conversation Management API & unlimited history** (`v2.35.0`, CLI `v1.5.15`), restart auto-resume (`v2.35.1`), mid-turn model switching (`v2.35.2`), and CLI `file:///` permission resolution hardening (`v1.5.18`).

---

## 2. Master 5-Surface & 7-IDE-Extension Release Matrix (`2026-11-26`)

| Product Surface | Earliest Verified Release | Latest in `changelog.md` | Authoritative Upstream Pin | Enterprise Auth | Canonical Role & Reference |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Antigravity App (2.0)** | `v2.0.1` (`2026-05-19`) | `v2.35.2` (`2026-11-25`) | **`2.35.2`** | Yes (WIF/SSO/PAYG) | Desktop command center, visual diffs/artifacts, built-in browser, Voice Mode, Sidecars, MCP Apps, SSH ([changelog](https://antigravity.google/docs/changelog.md)) |
| **Antigravity CLI (`agy`)** | `v1.0.4` GitHub (`2026-06-01`) *(launch `2026-05-19`)* | `v1.5.16` (`2026-11-24`) | **`1.5.18`** (`2026-11-26`, GitHub Releases) | Yes (WIF/SSO/ADC/API Key) | Terminal TUI, headless CI (`-p --output-format stream-json --json-schema`), **`agy acp`** stdio JSON-RPC server ([releases](https://github.com/google-antigravity/antigravity-cli/releases/tag/1.5.18)) |
| **Antigravity Python SDK** | `0.1.0` PyPI (`2026-05-19`) | `v0.1.24` (`2026-11-16`) | **`0.1.24`** (`2026-11-19`, PyPI wheel) | Yes (`vertex=True` / Express / API Key) | Programmatic Python harness embedding compiled `localharness`, hooks, subagents, `beta.workflows`, OTel, LiteRT ([PyPI](https://pypi.org/project/google-antigravity/0.1.24/)) |
| **Antigravity IDE (Standalone)** | `v1.11.2` (`2025-11-18`) / `v2.0.1` (`2026-05-19`) | `v2.8.0` (`2026-11-19`) | **`2.8.0`** | **No** *(consumer only)* | Optional personal all-in-one editor; excluded from Gemini Enterprise deployments ([FAQ](https://antigravity.google/docs/faq.md)) |
| **IDE Ext — VS Code** | `v1.0.0` (`2026-08-18`) | `v1.13.0` (`2026-11-16`) | **`1.13.0`** *(VS Code `1.90+`)* | Yes | Native inline diffs, `@terminal` pills, voice dictation ([docs](https://antigravity.google/docs/ide/extensions/vscode.md)) |
| **IDE Ext — Visual Studio** | `v1.0.260818.0` (`2026-08-18`) | `v1.0.261116.0` (`2026-11-16`) | **`1.0.261116.0`** *(VS 2022 `17.14+` / VS 2026)* | Yes | Native MSBuild/solution diffs, chat & voice dictation ([docs](https://antigravity.google/docs/ide/extensions/visual-studio.md)) |
| **IDE Ext — Eclipse** | `v1.0.0` (`2026-10-27`) | `v1.2.0` (`2026-11-19`) | **`1.2.0`** *(Eclipse `2026-06+`)* | Yes | Native compare editor diffs & workspace trust ([docs](https://antigravity.google/docs/ide/extensions/eclipse.md)) |
| **IDE Exts — JetBrains, Zed, Xcode** | `v1.0.0` (`2026-08-20`) | `v1.5.0` (`2026-11-10`) | **`antigravity-acp 1.5.0`** / `agy 1.5.18` | Yes | Shared Agent Client Protocol (ACP) integration (`JetBrains 2026.2.1+`, `Zed 0.140.0+`, `Xcode 27 beta 6+`; [ACP docs](https://antigravity.google/docs/ide/extensions/acp.md)) |
| **IDE Integration — Android Studio** | Referenced ACP `v1.4.1` (`2026-10-16`) | Shared under ACP notes | **ACP Registry** *(Enterprise Preview)* | Yes (Preview) | Installed via native Android Studio Agent Picker ([docs](https://antigravity.google/docs/ide/extensions/android-studio.md)) |

---

## 3. Major Capability Waves (Verified Across Surfaces)

| Capability Wave | Key Landings & Versions | Architectural Significance |
| :--- | :--- | :--- |
| **Frontier Gemini 4 Lineup & Orchestrator** | `Gemini 4 Carbon` (Nov 10), `Hydrogen` (Nov 12; SDK `0.1.24` default), `Neon` (Nov 18; 512K context, Paid default), `Orchestrator` planner+executor (`high` default in App `v2.35.0` / CLI `v1.5.15`), `Claude Opus/Sonnet 5.5` thinking, SDK `LiteRTAgentConfig` (Gemma 4 26B vision + KV prefix cache) & `LocalOpenAIAgentConfig` | Standardizes post-Nov-30 routing on native AGY models + 4 thinking effort levels (`low`/`medium`/`high`/`xhigh`) without custom proxy glue ([ADR-0003](adrs/ADR-0003-L1-frontier-models-routing-and-sunsets.md)). |
| **4-Tier Native Multi-Agent Orchestration** | `Subagents` (`SubagentConfig`, `@<subagent>`, parallel cards), `/teamwork` agent teams, **Native `/swarm`** shared message board (App `v2.31.0`, CLI `v1.5.5`, Enterprise `v2.33.0`), and **Dynamic Workflows (`/run-workflow`)** with bundled Python runtime (SDK `v0.1.22`, App `v2.32.0`, CLI `v1.5.9`) | Covers focused delegation, peer-to-peer board collaboration, and scripted Python fan-out without polluting parent conversation context ([ADR-0005](adrs/ADR-0005-L3-intra-session-multi-agent-orchestration.md)). |
| **Plugins, Marketplace & MCP Apps** | Plugin Marketplace (App `v2.18.1`, CLI `v1.3.2`), `agy plugin validate` (`v1.4.0`–`v1.4.3`), Partner shelves + inline OAuth (`v2.28.2`+), `migrate-agent-settings` (`v2.30.0`), UI Extensions (`v2.22.0`), and full **MCP Apps** (`io.modelcontextprotocol/ui` + `com.google.antigravity/ui` in App `v2.34.0`) | Bundles skills, rules, hooks, MCP servers, and sandboxed `ui://` HTML widgets into versioned, governable units ([ADR-0007](adrs/ADR-0007-L5-vertical-mcp-apps-and-code-mode.md)). |
| **Customizations, Hooks & Sidecars** | Open Agent Skills (`SKILL.md`, `agentskills.io`), `~/.agents/skills` CLI discovery (`v1.5.16`), dedicated **`20,000`-token rules budget** (App `v2.17.0`, CLI `v1.2.7`), `hooks.json` with `PreToolUse` 6 decisions & Stop-hook `continuationActive` guard, and persistent App **Sidecars** (`sidecar.json` / `agentapi`) | Enforces progressive disclosure and deterministic lifecycle enforcement across App, CLI, Extensions, and SDK ([ADR-0006](adrs/ADR-0006-L4-cross-session-and-federated-messaging.md)). |
| **OS Sandboxing, Auto Mode & Enterprise Governance** | macOS Seatbelt (`v1.15.6`), Linux namespaces (`v1.21.6`), Windows file+network sandbox (`v2.15.1` / CLI non-admin `v1.2.17`), SDK `enable_sandbox=True` (`v0.1.16`), **Auto Mode** GA (App `v2.30.0`, default CLI `v1.5.7`), `file:///` permission hardening (CLI `v1.5.18`), WIF SSO + `admin_settings.json` MDM (`v2.33.0`) | Provides OS-native local isolation plus fail-closed enterprise policy ceilings ([ADR-0002](adrs/ADR-0002-L0-execution-isolation-and-sandboxes.md), [ADR-0010](adrs/ADR-0010-L8-deterministic-security-and-fail-closed-gates.md)). |
| **Conversations API, History & Continuity** | Shared SQLite `.db` store (`v1.0.4`), **unlimited local history** + **`ConversationService` HTTP+JSON API** (App `v2.35.0`, CLI `v1.5.15`), restart auto-resume (`v2.35.1`), mid-turn model switch (`v2.35.2`), `/compact`, and multi-turn read-only `/btw` tabs (`v2.32.2`–`v2.33.0`) | Enables clean programmatic session handoff and unbounded durable local recall without external chat proxies. |
| **Remote Control, Cloud Agents, SSH & ACP** | `agy remote-control` daemon (`v1.2.0`), Cloud Remote Agents (`v2.29.0`–`v2.30.0`, CLI `--remote-agent` `v1.5.0`), OpenSSH remote Linux hosts (`v2.33.0`), and native **`agy acp`** stdio server (`v1.5.0`) | Eliminates custom SSH/PTY glue and editor lock-in across local, remote Linux, and cloud execution topologies ([ADR-0004](adrs/ADR-0004-L2-multi-surface-agy-harness-and-acp.md)). |

---

## 4. Time-Bound Sunset & Breaking-Change Calendar

### 4.1 P0 — Immediate Model Removal Cutoff (`2026-11-30`)

Per live `https://antigravity.google/docs/models.md`, four hosted model families are permanently removed on **November 30, 2026**. Zero active slots in scripts, CI workflows, manifests, or skills may reference them (enforced automatically by `rules/ast-grep/no-retiring-nov30-models.yml`, `scripts/verify_manifest.py`, and `scripts/audit_ecosystem_hygiene.py`):

| Retiring Model Family (`2026-11-30`) | Affected Surfaces / Plans | Mandatory Post-Nov-30 Migration Target |
| :--- | :--- | :--- |
| **Gemini 4 Argon** | Paid Pro, Ultra, Enterprise | **`gemini-4-neon`** (general Paid default, 512K) or **`gemini-4-carbon`** (long-horizon SWE/science) |
| **Gemini 3.8 Flash** | All plans & SDK `0.1.16`–`0.1.23` defaults | **`gemini-4-hydrogen`** (4 thinking levels; Free & SDK `0.1.24` default) |
| **GPT-OSS-120b** | Free, Pro, Ultra | **`gemini-4-hydrogen`** (hosted) or SDK **`LiteRTAgentConfig` / `LocalOpenAIAgentConfig`** (local) |
| **Claude 4.6** (`Sonnet`/`Opus`) | Free & Pro | **`claude-sonnet-5-5`** / **`claude-opus-5-5`** (Paid Pro/Ultra/Enterprise) or **`gemini-4-hydrogen`** (Free) |

*Enterprise legacy note:* `Gemini 3.7 Flash`, `3.6 Flash`, and `3.1 Pro` are Enterprise-only compatibility models and excluded from greenfield active slots.

### 4.2 P1 — Already Effective Platform & SDK Breaking Changes

| Breaking Change / Deprecation | Effective Date / Version | Required Migration & Enforcement |
| :--- | :--- | :--- |
| **Gemini CLI Consumer Tier Sunset** | `2026-06-18` | Free & Google AI Pro/Ultra accounts migrated to `agy`; `gemini-cli` is explicitly not tuned for Gemini 4+. Run `agy plugin import gemini`, move `.gemini/skills/` → `.agents/skills/`, and relocate inline MCP configs to `mcp_config.json` with `serverUrl` ([migration docs](https://antigravity.google/docs/cli/gcli-migration.md)). |
| **Project Config Path Breaking Move** | `2026-09-22` (App `v2.17.0`) | Legacy `.agents/settings.json` is **silently ignored**. Store repo customization settings in `<project>/.gemini/config.json`. |
| **Legacy Single-File Workflows Deprecated** | `2026-05` / `/migrate-workflows` (`v2.12.0+`) | `.agents/workflows/*.md` and `~/.gemini/config/global_workflows/*.md` (`12,000`-char cap) are replaced by directory-bundled **`SKILL.md`** and programmatic **`/run-workflow`**. |
| **CLI `unsandboxed(...)`, `/fast`, `/planning` & Legacy Tools** | `2026-07-08` (`v1.1.0`) – `2026-09-19` (`v1.2.7`) | Use `/plan`, `Shift+Tab` (`auto` default since `v1.5.7`), and unified `Deny > Ask > Allow` `command(...)` rules on personal accounts. `find_by_name`, `grep_search`, and `list_dir` retired from default CLI baseline. |
| **Hardened `--dangerously-skip-permissions` & Domain Grants** | `2026-10-28` (`v1.4.9`) – `2026-11-06` (`v1.5.2`) | Enterprise org policies and protected commands cannot be bypassed by `--dangerously-skip-permissions`; `www.google.com` grants no longer cover `mail.google.com`. |
| **Python SDK `0.1.x` Breaking API Shifts** | `2026-06-04` (`0.1.2`) – `2026-11-16` (`0.1.24`) | `McpSseServer` removed (`0.1.2`, banned by `rules/ast-grep/no-deprecated-mcp-sse-or-autogen.yml`); `gemini_config` → `models` & post-init hook/trigger registration removed (`0.1.4`); `AgentBehavior.AUTONOMOUS` default (`0.1.11`); `TriggerDelivery` removed (`0.1.15`); `CompactionConfig(token_threshold=...)`, `ASK_QUESTION` excluded from defaults, `modified_arguments_json` → `modified_args` (`0.1.17`–`0.1.18`); `START_SUBAGENT` → `INVOKE_SUBAGENT` (`0.1.22`); explicit `model` pin mandatory due to default drift (`3.5 → 3.6 → 3.7 → 3.8 → gemini-4-hydrogen`). |
| **AutoGen & Semantic Kernel Maintenance Mode** | `2026-04-02` | Superseded by **Microsoft Agent Framework (`MAF`) `1.0` GA** (or Google ADK / PydanticAI v2 / LangGraph 1.0); legacy imports banned by `rules/ast-grep/no-deprecated-mcp-sse-or-autogen.yml`. |
| **SWE-bench Verified Retired** | `2026-02-23` | Replace with **SWE-bench Pro Public V2**, **Terminal-Bench 2.0** (Harbor), **Inspect AI**, and **SkillsBench** (`arXiv:2602.12670`; [ADR-0011](adrs/ADR-0011-L9-adversarial-evals-and-trace-optimization.md)). |

### 4.3 P2 — Medium-Horizon Protocol Cutoff (`2027-07-28`, MCP `2026-07-28` Window)

Under the **MCP `2026-07-28`** specification's 12-month minimum deprecation window (`https://blog.modelcontextprotocol.io/posts/2026-07-28/`):

- **Transport:** Ban legacy dual-endpoint HTTP+SSE (`McpSseServer` / `SSEServerTransport`) and stateful `Mcp-Session-Id` stickiness; standardize on **Stateless Streamable HTTP** (`Mcp-Method`/`Mcp-Name` gateway headers) plus optional `io.modelcontextprotocol/tasks` for long-running work.
- **Auth:** Adopt **Client ID Metadata Documents (CIMD)** (AGY advertises `https://antigravity.google/oauth/client-metadata.json`), **RFC 8707** resource indicators, and **RFC 9207** issuer validation instead of Dynamic Client Registration (DCR) alone.
- **Stateless Server Boundary:** Do not adopt deprecated stateful/client-coupled server primitives (client-side LLM sampling, roots, or logging notifications) in new MCP servers; keep reasoning in AGY orchestration / A2A v1.0 and telemetry in **OpenTelemetry GenAI** (`params._meta` `traceparent`).

---

## 5. Upstream Registry & Local-vs-Live Doc-Drift Guardrails

Empirically audited discrepancies that automated tooling and engineers MUST account for:

### 5.1 Four Verified Upstream Registry vs. `changelog.md` Lags

| # | Surface / Artifact | `antigravity.google/docs/changelog.md` | Authoritative Reality (`2026-11-26`) | Guardrail |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **CLI (`agy`) version** | Stops at `v1.5.16` (`2026-11-24`) | GitHub Releases & auto-updated binary at **`v1.5.18`** (`2026-11-26`: `v1.5.17` adds `NotificationTimeoutSeconds` + OAuth 1h auto-refresh; `v1.5.18` fixes `file:///` permission resolution) | Pin CLI tracking against GitHub Releases API, not `changelog.md` alone. |
| **2** | **CLI `v1.0.0`–`v1.0.3` dates** | Stamped `January 1, 2026` below May 19 launch | Placeholder epoch-year docs artifact; public launch was `2026-05-19` and GitHub Releases start at `1.0.4` (`2026-06-01`) | Cite `2026-05-19` launch + `2026-06-01` GitHub `1.0.4` in audit timelines. |
| **3** | **Python SDK release count** | Lists `22` releases (`v0.1.1` → `v0.1.24`) | PyPI has **`25`** releases (`0.1.0` → `0.1.24`, uploaded `2026-11-19`); GitHub repo has `0` GitHub Releases | Treat PyPI JSON API as version truth; always install binary-coupled wheels (`uv add google-antigravity==0.1.24`). |
| **4** | **Android Studio changelog** | No dedicated subsection in `changelog.md` | Tracked under shared `antigravity-acp` notes + `docs/ide/extensions/android-studio.md` (ACP Registry Enterprise Preview) | Monitor `antigravity-acp` releases for Android Studio updates. |

### 5.2 Four Verified Offline Built-In Skill Drifts vs. Live Docs

Never rely blindly on offline built-in skill docs bundled inside `~/.gemini/antigravity/builtin/skills/` without cross-checking live `https://antigravity.google/docs/*.md`:

| # | Offline Built-In Reference | Stale Offline Claim | Live Official Truth (`2026-11-26`) |
| :---: | :--- | :--- | :--- |
| **1** | `antigravity_guide/references/app.md` | Calls feature *"Scheduled Tasks"* and model *"Gemini Next"*; omits `/swarm`, `/run-workflow`, Voice Mode, MCP Apps, SSH | Renamed **Automations** (`v2.21.1`); active models are **Gemini 4 Neon / Carbon / Hydrogen**. |
| **2** | `automation/SKILL.md` (Quick Start) | Cites legacy path `~/.gemini/jetski/sidecars/<slug>/sidecar.json` | Live `sidecars.md` requires **`~/.gemini/config/sidecars/<id>/sidecar.json`** (legacy `jetski` path is ignored). |
| **3** | `agy-customizations/docs/json_configs.md` | Shows `"exclude": ["experimental-.*"]` regex wildcards and `"path": "~/..."` tilde expansion | Live `customization-discovery.md` explicitly states **no `~` expansion** and **no wildcards**; always use resolved absolute paths. |
| **4** | `agy-customizations/docs/hooks.md` | Lists only `4` `PreToolUse` decisions (`allow`, `deny`, `ask`, `force_ask`) | Live `hooks.md` supports **`6`** decisions, adding **`auto_approve`** and **`deny_unless_prior_grant`** (and non-zero exits fail open). |

---

## 6. Related Repository References

- Clean Upstream Version Pins & Provisioning Commands: [Clean Install Registry](clean-install-registry.md)
- Bounded 12-ADR MADR 4.0.0 Catalog: [ADR Catalog](adrs/CATALOG.md)
- `L1` Frontier Models & Sunset ADR: [ADR-0003](adrs/ADR-0003-L1-frontier-models-routing-and-sunsets.md)
- `L2` Multi-Surface Harness & ACP ADR: [ADR-0004](adrs/ADR-0004-L2-multi-surface-agy-harness-and-acp.md)
- Cryptographically Sealed Manifest Guide: [Manifest Guide](manifest-guide.md)
