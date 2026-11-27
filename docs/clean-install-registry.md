# Clean Upstream Installation & Framework Provisioning Registry (`L0`–`L10`)

**Verified Date:** 2026-11-26  
**Verification Method:** 100% live read-only queries against PyPI JSON API (`https://pypi.org/pypi/<pkg>/json`), npm Registry API (`https://registry.npmjs.org/<pkg>`), NuGet Flat Container API (`https://api.nuget.org/v3-flatcontainer/microsoft.agents.ai/index.json`), GitHub Release tags (`https://github.com/<org>/<repo>/releases/tag/<ver>`), Homebrew Formulae JSON API (`https://formulae.brew.sh/api/formula/<name>.json`), and live `antigravity.google/docs/*.md` mirrors. Zero unpinned placeholders; zero global `pip install`.

---

## 1. Clean Provisioning & Isolation Hygiene Standards

To prevent global dependency pollution, binary/wheel skew, and non-reproducible CI builds across `L0`–`L10`, every upstream dependency MUST satisfy five invariants:

1. **Zero Global `pip install`:** Manage Python packages via `uv` (`0.13.10`) using locked project environments (`uv add <pkg>==<ver>` + committed `uv.lock`) or isolated tool environments (`uv tool install <pkg>==<ver>`).
2. **Exact Version Pinning & Lockfiles:** Pin Node/TypeScript dependencies with `--save-exact` and restore in CI with `npm ci`. Pin CLI/security binaries in repo-scoped [`mise.toml`](../mise.toml) (`mise` `2026.11.14`).
3. **Binary-Coupled Wheel Integrity:** Packages shipping compiled native runtimes inside wheels (`google-antigravity==0.1.24`, `codebase-memory-mcp==0.12.1`, `ruff==0.17.6`, `ty==0.0.112`, `ast-grep-cli==0.51.3`, `zizmor==1.33.1`) MUST install from official wheels/releases—never raw source checkouts lacking the compiled runtime binary.
4. **Segregated Dependency Groups:** Keep runtime, cloud, eval/red-teaming (`inspect-ai`, `harbor`, `skillevaluator`, `dspy`, `gepa`), local ML (`litert-lm`), and dev tools isolated in separate [`pyproject.toml`](../pyproject.toml) dependency groups.
5. **Host Secret Isolation:** Keep provider API keys and OAuth tokens exclusively in host OS keyrings or CI secret stores—never in `mise.toml`, `pyproject.toml`, `package.json`, `.agents/mcp_config.json`, or eval configs.

### Provisioner Baseline (Verified 2026-11-26)

| Tool | Registry / Channel | Verified Version (2026-11-26) | Clean Pinned Install Command | Post-Install Verify Command | Official URL |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`uv`** | Homebrew / Astral | `0.13.10` | `curl -LsSf https://astral.sh/uv/0.13.10/install.sh \| sh` | `uv --version` | `https://docs.astral.sh/uv/` |
| **`mise`** | Homebrew / JDX | `2026.11.14` | `curl -fsSL https://mise.jdx.dev/install.sh \| MISE_VERSION=v2026.11.14 sh` | `mise --version` | `https://mise.jdx.dev/` |

---

## 2. Master Clean Upstream Install Registry (`L0`–`L10`)

### `L0` — Execution Isolation & Sandboxes

| Canonical Upstream | Registry / Channel | Exact Verified Version (2026-11-26) | Clean Pinned Install Command | Post-Install Smoke / Verify Command | Zero-Self-Invention Boundary | Official URL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AGY OS-Native Terminal Sandbox** | Bundled in AGY App & CLI | App `2.35.2` / CLI `1.5.18` | Bundled (zero separate install); enforce via `agy --sandbox` or App **Settings > Agent > Terminal Sandbox** | `agy --help \| grep -- "--sandbox"` | Uses Linux kernel namespaces, macOS `sandbox-exec` (Seatbelt), and Windows AppContainer natively—never build custom chroot/seccomp wrappers | `https://antigravity.google/docs/sandbox.md` |
| **`e2b`** (Python SDK) | PyPI | `2.66.0` (2026-11-26) | `uv add e2b==2.66.0` | `uv run python -c "import e2b; print(e2b.__name__)"` | Thin adapter invoking Firecracker microVMs; never self-host custom KVM wrappers for untrusted code | `https://e2b.dev/resources/best-code-execution-sandboxes-for-ai-agents` |
| **`e2b-code-interpreter`** (Python) | PyPI | `2.11.12` (2026-11-26) | `uv add e2b-code-interpreter==2.11.12` | `uv run python -c "import e2b_code_interpreter; print('ok')"` | Stateful code execution over Firecracker microVMs | `https://pypi.org/project/e2b-code-interpreter/2.11.12/` |
| **`@e2b/code-interpreter`** (TS/JS) | npm | `2.9.1` | `npm install --save-exact @e2b/code-interpreter@2.9.1` | `node -e "require('@e2b/code-interpreter'); console.log('ok')"` | TypeScript Firecracker sandbox client | `https://registry.npmjs.org/@e2b/code-interpreter/2.9.1` |
| **`daytona`** (Python SDK) | PyPI *(replaces deprecated `daytona-sdk`)* | `2.3.0` (2026-11-26) | `uv add daytona==2.3.0` | `uv run python -c "import daytona; print('ok')"` | Stateful forkable cloud sandboxes; do **not** install deprecated `daytona-sdk` (`0.234.0`) | `https://www.daytona.io/` |
| **`@daytonaio/sdk`** (TS/JS) | npm | `0.232.0` | `npm install --save-exact @daytonaio/sdk@0.232.0` | `node -e "import('@daytonaio/sdk').then(() => console.log('ok'))"` | TypeScript client for Daytona forkable workspaces | `https://www.daytona.io/docs` |
| **`modal`** (Python SDK) | PyPI | `1.6.4` (2026-11-12) | `uv add modal==1.6.4` | `uv run modal --version` | High-fan-out gVisor sandboxes & GPU eval rollouts (`modal.Sandbox.create`) | `https://modal.com/blog/top-code-agent-sandbox-products` |
| **`@cloudflare/sandbox`** + **`wrangler`** | npm | `@cloudflare/sandbox` `1.0.3` · `wrangler` `4.168.0` | `npm install --save-exact @cloudflare/sandbox@1.0.3 wrangler@4.168.0` | `npx wrangler --version` | Edge Cloudflare Containers + Durable Objects + Dynamic Workers host-side credential isolation | `https://blog.cloudflare.com/faster-agent-sandboxes` |

### `L1` — Frontier Models, Effort Routing & Local Model Runtimes

| Canonical Upstream | Registry / Channel | Exact Verified Version (2026-11-26) | Clean Pinned Install Command | Post-Install Smoke / Verify Command | Zero-Self-Invention Boundary | Official URL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AGY Hosted Frontier Roster & Orchestrator** | Hosted via AGY Auth (App/CLI/Extensions) | Post-Nov-30 safe lineup: `gemini-4-neon` (512K), `gemini-4-carbon`, `gemini-4-hydrogen`, `Orchestrator`, `claude-opus-5-5`, `claude-sonnet-5-5` | Bundled via `agy` / Antigravity App sign-in (zero package install); **never pin** retiring Nov-30 slugs (`gemini-4-argon`, `gemini-3.8-flash`, `gpt-oss-120b`, `claude-4-6`) | `agy models \| grep -E "gemini-4-(neon\|carbon\|hydrogen)\|claude-(opus\|sonnet)-5-5"` | Use native AGY Orchestrator & `--effort` (`low\|medium\|high\|xhigh`) instead of custom model routers | `https://antigravity.google/docs/models.md` |
| **`litert-lm`** (On-Device Local Runtime) | PyPI *(paired with `google-antigravity==0.1.24`)* | `0.20.0` (2026-11-23; exceeds SDK `>=0.19.1` min) | `uv add --group local-ml litert-lm==0.20.0` | `uv run python -c "import litert_lm; from google.antigravity import LiteRTAgentConfig; print('ok')"` | On-device `.litertlm` checkpoints (e.g., Gemma 4 26B A4B) with automatic Metal/CUDA/NPU detection, vision & KV prefix caching | `https://antigravity.google/docs/sdk/local-models.md` |
| **SDK `LocalOpenAIAgentConfig`** | Bundled in `google-antigravity` | `0.1.24` (2026-11-19 PyPI) | `uv add google-antigravity==0.1.24` *(connects to external Ollama / LM Studio / vLLM endpoint)* | `uv run python -c "from google.antigravity import LocalOpenAIAgentConfig; print('ok')"` | Native SDK loopback bridge with JSON Schema normalization & `Retry-After` handling; zero custom OpenAI proxy glue | `https://antigravity.google/docs/sdk/local-models.md` |

### `L2` — Multi-Surface Developer Harness (AGY 5 Surfaces, 7 IDE Extensions & ACP)

| Canonical Upstream | Registry / Channel | Exact Verified Version (2026-11-26) | Clean Pinned Install Command | Post-Install Smoke / Verify Command | Zero-Self-Invention Boundary | Official URL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Antigravity App (2.0)** | Official OS installer (`antigravity.google/download`) | `2.35.2` (2026-11-25) | macOS ARM64 DMG: `https://storage.googleapis.com/antigravity-public/antigravity-hub/2.35.2-4585983447007232/darwin-arm/Antigravity.dmg` (Intel/Win/Linux on `/download`) | `defaults read /Applications/Antigravity.app/Contents/Info.plist CFBundleShortVersionString` | Desktop multi-agent command center, built-in browser, Voice Mode, SSH, MCP Apps; never fork custom desktop chat shells | `https://antigravity.google/docs/getting-started.md` |
| **Antigravity CLI (`agy`)** | Official installer + GitHub Releases (`google-antigravity/antigravity-cli`) + `mise` | `1.5.18` (2026-11-26 GitHub; `1.5.16` in `changelog.md`) | macOS/Linux: `curl -fsSL https://antigravity.google/cli/install.sh \| bash` (or `mise use -g agy@1.5.18` / Win: `irm https://antigravity.google/cli/install.ps1 \| iex`) | `agy --version && agy acp --help` | Native Go TUI, headless `-p`/`stream-json`, `agy acp` stdio JSON-RPC server; zero custom PTY/CLI wrappers | `https://github.com/google-antigravity/antigravity-cli/releases/tag/1.5.18` |
| **Antigravity Python SDK (`google-antigravity`)** | PyPI (Apache-2.0, binary-coupled wheel) | `0.1.24` (2026-11-19 PyPI; `2026-11-16` changelog) | `uv add google-antigravity==0.1.24` *(always wheel install; never raw GitHub source)* | `uv run python -c "import google.antigravity as ag; print(ag.__name__)"` | Embeds compiled `localharness` with policies, hooks, subagents, `beta.workflows`, OTel tracing | `https://pypi.org/project/google-antigravity/0.1.24/` |
| **Antigravity IDE (Standalone)** | Official installer (`antigravity.google/download`) | `2.8.0` (2026-11-19) | Download standalone IDE installer from `https://antigravity.google/download` *(consumer auth only; no Gemini Enterprise sign-in)* | Launch IDE → **Help > About** (`2.8.0`) | Standalone VS Code-based IDE; use App/CLI/Extensions for Gemini Enterprise | `https://antigravity.google/product/antigravity-ide` |
| **IDE Ext — VS Code** | VS Code Marketplace (`Google.google-antigravity`) | `1.13.0` (2026-11-16; VS Code `1.90+`) | `code --install-extension Google.google-antigravity@1.13.0` | `code --list-extensions --show-versions \| grep -i antigravity` | First-party editor integration, inline diffs, `@terminal` pills, voice dictation | `https://antigravity.google/docs/ide/extensions/vscode.md` |
| **IDE Ext — Visual Studio** | Visual Studio Marketplace (`Google.GoogleAntigravity`) | `1.0.261116.0` (2026-11-16; VS 2022 `17.14+` or VS 2026) | Visual Studio → **Extensions > Manage Extensions** → install `Google.GoogleAntigravity` VSIX (`1.0.261116.0`) | Verify **Antigravity** tool window (`View > Other Windows > Antigravity`) | Native MSBuild/solution inline diffs & chat | `https://antigravity.google/docs/ide/extensions/visual-studio.md` |
| **IDE Ext — Eclipse** | Eclipse Marketplace (`google-antigravity`) | `1.2.0` (2026-11-19; Eclipse `2026-06+`) | Eclipse → **Help > Eclipse Marketplace…** → install `Google Antigravity` (`1.2.0`) | **Antigravity > Toggle Chat** (`Cmd+Option+E` / `Ctrl+Alt+K`) | Native Eclipse compare editor diffs & workspace trust | `https://antigravity.google/docs/ide/extensions/eclipse.md` |
| **IDE Exts — JetBrains, Zed, Xcode, Android Studio (ACP)** | Editor AI/ACP Registries + `agy acp` | `antigravity-acp` `1.5.0` (2026-11-10) / `agy` `1.5.18` | JetBrains (`2026.2.1+`): **JetBrains AI > Settings > Agents**; Zed (`0.140.0+`): **External Agents > Install from Registry**; Xcode (`27 beta 6+`): **Settings > Intelligence**; Android Studio: **Agent > Picker > Google Antigravity** (Enterprise Preview) | `agy acp --help` + open editor agent panel and run `/usage` | Zero custom editor plugins—use standard **ACP** (`agy acp` / ACP Registry) for all ACP-compliant IDEs | `https://antigravity.google/docs/ide/extensions/acp.md` |

### `L3` — Intra-Session Multi-Agent Orchestration

| Canonical Upstream | Registry / Channel | Exact Verified Version (2026-11-26) | Clean Pinned Install Command | Post-Install Smoke / Verify Command | Zero-Self-Invention Boundary | Official URL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AGY Native Orchestration Suite** (Subagents, `/swarm`, `/run-workflow`, `/boost`, `/teamwork`) | Bundled in AGY App, CLI & Python SDK | App `2.35.2` / CLI `1.5.18` / SDK `0.1.24` | Bundled (zero external install; `/run-workflow` unpacks its own bundled Python runtime or respects `ANTIGRAVITY_PYTHON`) | `agy --version && agy agents` | Never build custom multi-agent chat routers, ad-hoc subprocess fan-out managers, or polling loops | `https://antigravity.google/docs/swarm.md`, `https://antigravity.google/docs/dynamic-workflows.md` |

### `L4` — Cross-Session & Federated Messaging

| Canonical Upstream | Registry / Channel | Exact Verified Version (2026-11-26) | Clean Pinned Install Command | Post-Install Smoke / Verify Command | Zero-Self-Invention Boundary | Official URL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AGY `ConversationService`, Sidecars (`agentapi`), Hooks, Remote Control / Agents / SSH** | Bundled in AGY App & CLI | App `2.35.2` (`ConversationService` `v2.35.0+`, SSH `v2.33.0+`) / CLI `1.5.18` (`--remote-agent`, `remote-control`) | Bundled (zero external install); configure declaratively via `.agents/hooks.json` and `~/.gemini/config/sidecars/` | `agy remote-control --help` | Use native Connect HTTP+JSON lifecycle API, `sidecar.json` `agentapi`, and OpenSSH host connections instead of ad-hoc socket daemons | `https://antigravity.google/docs/sidecars.md`, `https://antigravity.google/docs/ssh.md` |
| **`orca`** (Heterogeneous Worktree & Mail Orchestrator) | GitHub Releases (`stablyai/orca`) | `v1.4.278` (GitHub; local host `1.4.277`) | Download pinned release `v1.4.278` from `https://github.com/stablyai/orca/releases/tag/v1.4.278` (use `orca-ide` outside Orca terminals on Linux) | `orca --version && orca status --json` | Cross-agent (AGY/Claude/Codex) worktrees, terminal control, and mail orchestration; never script raw `git worktree` + tmux PTY hacks | `https://github.com/stablyai/orca/releases/tag/v1.4.278` |
| **`a2a-sdk`** (Python A2A v1.0) | PyPI (Linux Foundation AAIF) | `1.3.1` (2026-11-17) | `uv add --group cloud a2a-sdk==1.3.1` | `uv run python -c "import a2a; print(a2a.__name__)"` | Standards-compliant Agent Cards & 9-state A2A task protocol across vendor/org boundaries | `https://pypi.org/project/a2a-sdk/1.3.1/` |
| **`@a2a-js/sdk`** (TypeScript A2A v1.0) | npm (Linux Foundation AAIF) | `1.3.0` | `npm install --save-exact @a2a-js/sdk@1.3.0` | `node -e "import('@a2a-js/sdk').then(() => console.log('ok'))"` | TypeScript A2A v1.0 client/server SDK | `https://github.com/a2aproject/a2a-js` |

### `L5` — Vertical Tool, Data & Interactive UI Protocol (MCP `2026-07-28` + `SEP-1865`)

| Canonical Upstream | Registry / Channel | Exact Verified Version (2026-11-26) | Clean Pinned Install Command | Post-Install Smoke / Verify Command | Zero-Self-Invention Boundary | Official URL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`mcp`** (Python SDK) | PyPI (LF AAIF) | `2.3.0` (2026-10-02) | `uv add mcp==2.3.0` | `uv run python -c "import mcp; print(mcp.__name__)"` | Stateless Streamable HTTP & Stdio MCP servers (`2026-07-28`); **do not** adopt legacy HTTP+SSE transport | `https://pypi.org/project/mcp/2.3.0/` |
| **`@modelcontextprotocol/sdk`** (TS SDK) | npm (LF AAIF) | `1.32.2` | `npm install --save-exact @modelcontextprotocol/sdk@1.32.2` | `node -e "import('@modelcontextprotocol/sdk/server/mcp.js').then(() => console.log('ok'))"` | Official TypeScript MCP client/server SDK (Streamable HTTP, CIMD/RFC 9207) | `https://github.com/modelcontextprotocol/typescript-sdk` |
| **`@modelcontextprotocol/ext-apps`** (MCP Apps `SEP-1865`) | npm (LF AAIF) | `2.0.4` | `npm install --save-exact @modelcontextprotocol/ext-apps@2.0.4` | `node -e "import('@modelcontextprotocol/ext-apps').then(() => console.log('ok'))"` | Sandboxed `ui://` HTML MCP Apps rendering inline, side-panel, full-page, and custom viewers in AGY App `v2.34.0+` | `https://modelcontextprotocol.io/extensions/apps/overview` |

### `L6` — Durable Cloud Workflow Execution & Production Agent Frameworks

| Canonical Upstream | Registry / Channel | Exact Verified Version (2026-11-26) | Clean Pinned Install Command | Post-Install Smoke / Verify Command | Zero-Self-Invention Boundary | Official URL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`dbos`** | PyPI | `3.7.0` (2026-11-24) | `uv add --group cloud dbos==3.7.0` | `uv run python -c "import dbos; print(dbos.__name__)"` | Crash-proof Postgres/SQLite checkpointing without a separate orchestrator cluster | `https://pypi.org/project/dbos/3.7.0/` |
| **`temporalio`** | PyPI | `1.37.0` (2026-11-24) | `uv add temporalio==1.37.0` | `uv run python -c "import temporalio; print(temporalio.__version__)"` | Enterprise deterministic workflow replay & indefinite HITL suspension | `https://pypi.org/project/temporalio/1.37.0/` |
| **`restate-sdk`** | PyPI | `1.5.5` (2026-11-24) | `uv add restate-sdk==1.5.5` | `uv run python -c "import restate; print(restate.__name__)"` | Scale-to-zero pausable/steerable serverless agent execution | `https://pypi.org/project/restate-sdk/1.5.5/` |
| **`google-adk`** | PyPI | `2.15.1` (2026-11-25) | `uv add google-adk==2.15.1` | `uv run adk --version` | First-party GCP/Vertex AI/A2A/MCP multi-agent backend runtime | `https://pypi.org/project/google-adk/2.15.1/` |
| **`pydantic-ai`** | PyPI | `2.75.0` (2026-11-25) | `uv add --group cloud pydantic-ai==2.75.0` | `uv run python -c "import pydantic_ai; print(pydantic_ai.__version__)"` | Strictly typed Python agents with native `DBOSDurability`/`TemporalDurability`/`RestateAgent` | `https://pypi.org/project/pydantic-ai/2.75.0/` |
| **`langgraph`** | PyPI | `1.2.24` (2026-11-20) | `uv add langgraph==1.2.24` | `uv run python -c "import langgraph; print('ok')"` | Explicit cyclical state graphs, checkpointers, HITL interrupts & Temporal plugin | `https://pypi.org/project/langgraph/1.2.24/` |
| **`agent-framework`** / **`Microsoft.Agents.AI`** | PyPI / NuGet | Python `1.26.0` (`agent-framework-core==1.26.0`) · NuGet `1.28.0` (`Microsoft.Agents.AI.Workflows` `1.28.0`) | Python: `uv add agent-framework==1.26.0` · .NET: `dotnet add package Microsoft.Agents.AI --version 1.28.0` | `uv run python -c "import agent_framework; print('ok')"` | Supersedes maintenance-mode AutoGen & Semantic Kernel | `https://pypi.org/project/agent-framework/1.26.0/` |
| **`openai-agents`** / **`@openai/agents`** | PyPI / npm | Python `0.26.0` · npm `0.22.0` | Python: `uv add openai-agents==0.26.0` · TS: `npm install --save-exact @openai/agents@0.22.0` | `uv run python -c "import agents; print('ok')"` | Lightweight OpenAI Handoffs + Guardrails + Hosted Sandboxes | `https://pypi.org/project/openai-agents/0.26.0/` |
| **`claude-agent-sdk`** / **`@anthropic-ai/claude-agent-sdk`** | PyPI / npm | Python `0.2.189` · npm `0.3.332` | Python: `uv add claude-agent-sdk==0.2.189` · TS: `npm install --save-exact @anthropic-ai/claude-agent-sdk@0.3.332` | `uv run python -c "import claude_agent_sdk; print('ok')"` | Programmatic Claude Code loop, hooks, and MCP embedding | `https://pypi.org/project/claude-agent-sdk/0.2.189/` |
| **`strands-agents`** | PyPI | `1.67.0` (2026-11-25) | `uv add strands-agents==1.67.0` | `uv run python -c "import strands; print('ok')"` | In-process model-driven library pairing with Amazon Bedrock AgentCore | `https://pypi.org/project/strands-agents/1.67.0/` |
| **`mastra`** + **`@mastra/core`** | npm | `mastra` `1.40.2` · `@mastra/core` `1.86.0` | `npm install --save-exact mastra@1.40.2 @mastra/core@1.86.0` | `npx mastra --version` | Native TypeScript Zod-typed agents & workflows | `https://mastra.ai` |

### `L7` — Tri-Layer Compounding Memory & Code/Corpus Intelligence

| Canonical Upstream | Registry / Channel | Exact Verified Version (2026-11-26) | Clean Pinned Install Command | Post-Install Smoke / Verify Command | Zero-Self-Invention Boundary | Official URL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`graphiti-core`** | PyPI | `0.32.1` (2026-11-24) | `uv add graphiti-core==0.32.1` | `uv run python -c "import graphiti_core; print('ok')"` | Bi-temporal fact succession (`t_valid`/`t_invalid`) exposed over MCP | `https://pypi.org/project/graphiti-core/0.32.1/` |
| **`letta`** + **`letta-client`** | PyPI | `letta` `0.34.12` · `letta-client` `1.12.1` | `uv add letta==0.34.12 letta-client==1.12.1` | `uv run python -c "import letta_client; print('ok')"` | Self-editing tiered context blocks, Git-backed MemFS, and Sleep-Time Compute | `https://pypi.org/project/letta-client/1.12.1/` |
| **`mem0ai`** | PyPI | `2.2.1` (2026-09-25) | `uv add mem0ai==2.2.1` | `uv run python -c "import mem0; print('ok')"` | Low-latency hybrid vector+graph preference/entity memory | `https://pypi.org/project/mem0ai/2.2.1/` |
| **`xerj`** | GitHub Releases (`xerj-org/xerj`) | `v1.0.0-rc.105` | Download pinned release `v1.0.0-rc.105` from `https://github.com/xerj-org/xerj/releases/tag/v1.0.0-rc.105` (or SHA-256 verified `curl -fsSL https://xerj.org/get \| sh`) | `xerj --version` | Static Rust hybrid BM25+kNN search + `/_memory/{ns}` MCP engine | `https://github.com/xerj-org/xerj/releases/tag/v1.0.0-rc.105` |
| **`codebase-memory-mcp`** | PyPI / npm / GitHub | `0.12.1` (2026-10-16) | `uv tool install codebase-memory-mcp==0.12.1` (or `npm install --save-exact codebase-memory-mcp@0.12.1`) | `codebase-memory-mcp --version` | Native tree-sitter AST/call-graph MCP + `manage_adr` | `https://github.com/DeusData/codebase-memory-mcp/releases/tag/v0.12.1` |

### `L8` — Deterministic Security, Static Analysis & Policy Gates

| Canonical Upstream | Registry / Channel | Exact Verified Version (2026-11-26) | Clean Pinned Install Command | Post-Install Smoke / Verify Command | Zero-Self-Invention Boundary | Official URL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`ruff`** | PyPI / Homebrew / `mise` | `0.17.6` (2026-11-19) | `uv tool install ruff==0.17.6` (or `mise use ruff@0.17.6`) | `ruff --version` | Sub-second Rust Python linter/formatter for `PostToolUse` & CI | `https://docs.astral.sh/ruff/` |
| **`ty`** | PyPI | `0.0.112` (2026-11-26) | `uv tool install ty==0.0.112` (or `mise use uv:ty@0.0.112`) | `ty --version` | Fast Rust Python static type verification | `https://github.com/astral-sh/ty/` |
| **`ast-grep`** (`ast-grep-cli` / `@ast-grep/cli`) | PyPI / npm / Homebrew | `0.51.3` (2026-11-16) | `uv tool install ast-grep-cli==0.51.3` (or `npm install --save-exact @ast-grep/cli@0.51.3`) | `ast-grep --version` | Structural AST rules escalating repeated prose rule violations to CI | `https://ast-grep.github.io/` |
| **`gitleaks`** | GitHub / Homebrew / `mise` | `8.30.1` (`v8.30.1`) | `mise use gitleaks@8.30.1` | `gitleaks version` | Deterministic secret leak prevention in pre-commit & CI | `https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1` |
| **`trivy`** | GitHub / Homebrew / `mise` | `0.76.2` (`v0.76.2`) | `mise use trivy@0.76.2` | `trivy --version` | Unified CVE, container, and IaC scanning | `https://github.com/aquasecurity/trivy/releases/tag/v0.76.2` |
| **`osv-scanner`** | GitHub / Homebrew / `mise` | `2.7.1` (`v2.7.1`) | `mise use osv-scanner@2.7.1` | `osv-scanner --version` | OSV database lockfile vulnerability gating (`uv.lock`, `package-lock.json`) | `https://github.com/google/osv-scanner/releases/tag/v2.7.1` |
| **`shellcheck`** | GitHub / Homebrew / `mise` | `0.11.0` (`v0.11.0`) | `mise use shellcheck@0.11.0` | `shellcheck --version` | Static verification of hook and automation shell scripts | `https://github.com/koalaman/shellcheck/releases/tag/v0.11.0` |
| **`zizmor`** | PyPI / GitHub / Homebrew | `1.33.1` (2026-11-22) | `uv tool install zizmor==1.33.1` (or `mise use zizmor@1.33.1`) | `zizmor --version` | Static security audit of `.github/workflows/*.yml` | `https://docs.zizmor.sh/` |
| **`syft`** | GitHub / Homebrew / `mise` | `1.57.2` (`v1.57.2`) | `mise use syft@1.57.2` | `syft version` | CycloneDX/SPDX SBOM provenance generation | `https://github.com/anchore/syft/releases/tag/v1.57.2` |

### `L9` — Adversarial Evaluation, Red-Teaming & Trace-to-Skill Optimization

| Canonical Upstream | Registry / Channel | Exact Verified Version (2026-11-26) | Clean Pinned Install Command | Post-Install Smoke / Verify Command | Zero-Self-Invention Boundary | Official URL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`inspect-ai`** + **`inspect-harbor`** | PyPI | `inspect-ai` `0.3.292` · `inspect-harbor` `1.0.0` | `uv add --group eval inspect-ai==0.3.292 inspect-harbor==1.0.0` | `uv run inspect --version` | Isolated Docker/K8s frontier eval framework by UK AISI & Meridian Labs | `https://inspect.aisi.org.uk/` |
| **`harbor`** | PyPI | `0.27.0` (2026-11-21) | `uv add --group eval harbor==0.27.0` | `uv run harbor --help` | Multi-sandbox eval & rollout harness powering Terminal-Bench 2.0 | `https://www.harborframework.com/` |
| **`promptfoo`** | npm | `0.126.0` | `npm install --save-exact --save-dev promptfoo@0.126.0` | `npx promptfoo --version` | Automated prompt-injection red-teaming & SDK regression gates | `https://promptfoo.dev` |
| **`dspy`** | PyPI | `3.5.0` (2026-11-10) | `uv add --group eval dspy==3.5.0` | `uv run python -c "import dspy; print(dspy.__version__)"` | Metric-driven module/prompt compilation | `https://pypi.org/project/dspy/3.5.0/` |
| **`gepa`** | PyPI | `0.1.4` (2026-07-15) | `uv add --group eval gepa==0.1.4` | `uv run python -c "import gepa; print('ok')"` | Trace-level LLM reflection optimizer (`arXiv:2507.19457`) | `https://github.com/gepa-ai/gepa` |
| **`skillevaluator`** | PyPI / GitHub (`NVIDIA/SkillEvaluator`) | `1.2.1` (2026-11-25) | `uv tool install --python 3.13 "skillevaluator[all]==1.2.1"` | `skillevaluator --version` | Multi-tier (`Tier 1–3`) static, security/PII, dedup, and live A/B `skill_lift` CI gating | `https://github.com/NVIDIA/SkillEvaluator/releases/tag/v1.2.1` |

### `L10` — Telemetry, Provenance & ADR Documentation Portal

| Canonical Upstream | Registry / Channel | Exact Verified Version (2026-11-26) | Clean Pinned Install Command | Post-Install Smoke / Verify Command | Zero-Self-Invention Boundary | Official URL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`opentelemetry-sdk`** + **`opentelemetry-exporter-otlp`** + **`opentelemetry-semantic-conventions`** | PyPI *(complements native AGY SDK `v0.1.5+` OTel)* | `opentelemetry-sdk` `1.45.2` · `opentelemetry-exporter-otlp` `1.45.2` · `opentelemetry-semantic-conventions` `0.66b2` | `uv add opentelemetry-sdk==1.45.2 opentelemetry-exporter-otlp==1.45.2 opentelemetry-semantic-conventions==0.66b2` | `uv run python -c "import opentelemetry.sdk; print('ok')"` | Vendor-neutral OTel GenAI spans (`invoke_agent`, `execute_tool`, `traceparent` over MCP `params._meta`) | `https://github.com/open-telemetry/semantic-conventions-genai` |
| **`zensical`** | PyPI / GitHub (`zensical/zensical`) | `0.1.3` (2026-11-20) | `uv tool install zensical==0.1.3` | `zensical --version` | Modern static documentation & MADR 4.0.0 ADR portal | `https://github.com/zensical/zensical/releases/tag/v0.1.3` |

---

## 3. Observed Workstation Pin-Parity Baseline (2026-11-26)

Verified on macOS `arm64` using native package managers only (`mise`, isolated `uv tool`, and SHA-256-verified official GitHub releases; zero `sudo`, zero global `pip`). All **`9/9`** [`../mise.toml`](../mise.toml) tools and **`16/17`** workstation CLIs (**`17/18`** total CLI/App surfaces including `Antigravity.app`) are at exact 1:1 registry parity:

| CLI / Surface | Verified Local Output (`2026-11-26`) | Registry Pin | Provisioning Channel & Parity Status |
| :--- | :--- | :--- | :---: |
| **`Antigravity.app`** | `2.35.2` | `2.35.2` | Official macOS DMG — **`EXACT PARITY`** |
| **`agy`** | `1.5.18` | `1.5.18` | `mise` (`agy@1.5.18`) — **`EXACT PARITY`** |
| **`mise`** | `2026.11.14 macos-arm64 (2026-11-24)` | `2026.11.14` | `mise self-update 2026.11.14` — **`EXACT PARITY`** |
| **`uv`** | `uv 0.13.10 (e3e7c1eac 2026-11-24 aarch64-apple-darwin)` | `0.13.10` | `mise use -g uv@0.13.10` — **`EXACT PARITY`** |
| **`ty`** | `ty 0.0.112 (77bf17505 2026-11-26)` | `0.0.112` | `mise use -g ty@0.0.112` + `uv tool install ty==0.0.112` — **`EXACT PARITY`** |
| **`ruff`** | `ruff 0.17.6` | `0.17.6` | `mise` + `uv tool` — **`EXACT PARITY`** |
| **`ast-grep`** | `ast-grep 0.51.3` | `0.51.3` | `mise` + `uv tool` — **`EXACT PARITY`** |
| **`zizmor`** | `zizmor 1.33.1` | `1.33.1` | `uv tool install zizmor==1.33.1` — **`EXACT PARITY`** |
| **`zensical`** | `0.1.3` | `0.1.3` | `uv tool install zensical==0.1.3` — **`EXACT PARITY`** |
| **`gitleaks`** | `8.30.1` | `8.30.1` | `mise` — **`EXACT PARITY`** |
| **`trivy`** | `Version: 0.76.2` | `0.76.2` | `mise` — **`EXACT PARITY`** |
| **`osv-scanner`** | `osv-scanner version: 2.7.1` | `2.7.1` | `mise use -g osv-scanner@2.7.1` — **`EXACT PARITY`** |
| **`shellcheck`** | `version: 0.11.0` | `0.11.0` | `mise` — **`EXACT PARITY`** |
| **`syft`** | `1.57.2` | `1.57.2` | `mise use -g syft@1.57.2` — **`EXACT PARITY`** |
| **`skillevaluator`** | `skillevaluator, version 1.2.1` | `1.2.1` | `uv tool install --python 3.13 skillevaluator==1.2.1` — **`EXACT PARITY`** |
| **`codebase-memory-mcp`** | `codebase-memory-mcp 0.12.1` | `0.12.1` | `mise` — **`EXACT PARITY`** |
| **`xerj`** | `xerj v1.0.0-rc.105` | `v1.0.0-rc.105` | Official `aarch64-apple-darwin.tar.gz` (SHA-256 verified) — **`EXACT PARITY`** |
| **`orca`** | `1.4.277` | `v1.4.278` | Symlinked to `/Applications/Orca.app/Contents/Resources/bin/orca` (no standalone macOS CLI asset; update via Orca Desktop in-app updater on restart) — **`APP-MANAGED HOLD`** |

**Safe Zero-Secret CLI Settings Check (`~/.gemini/antigravity-cli/settings.json`):** Boolean-only inspection of model-selection keys (`model`, `defaultModel`, `orchestrator`, `models`) confirmed `settings_json_exists: true` and **`retiring_model_hits_count: 0`** against the `2026-11-30` sunset regex (zero raw config contents or credentials accessed).

