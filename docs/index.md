# AGY SOTA Convergence Portal

Welcome to the **Google Antigravity (AGY 2.0) SOTA Convergence & Compounding Engineering** documentation portal (`as-of 2026-11-26`).

This portal publishes a strictly disjoint **11-layer upstream-only architecture (`L0`–`L10`)**, governed by **12 bounded MADR 4.0.0 ADRs**, backed by **63 live-verified package pins** (synchronized 1:1 with `UPSTREAM.md` and `upstream-map.toml`), hardened by a **3-workflow GitHub SOTA supply-chain suite**, and sealed cryptographically via `manifest/compounding_manifest.v2.json` (`v3.1.0`, 17 automated gates).

---

## Core Architecture Guides

| Guide | Scope |
| :--- | :--- |
| [ADR & Convergence Practice](adr-and-convergence-practice.md) | MADR 4.0.0 governance, 7-Criterion Saturation Exit Gate, 5-Question Zero-Self-Invention Gate, and 5-Artifact Truth-Division Matrix. |
| [AGY Surfaces & Changelogs](agy-surfaces-and-changelogs.md) | 5 official Google Antigravity products, 7 IDE extensions, `2026-11-30` model sunset audit, and full 2026 changelog evolution. |
| [Cross-Session & AGY Operational Practice](cross-session-and-agy-practice.md) | 9-route cross-session messaging matrix, customization precedence, context/token engineering, browser/sandbox security, and daily workflows. |
| [Ecosystem & Frameworks Matrix](ecosystem-frameworks-matrix.md) | Late-2026 SOTA comparison across sandboxes, durable runtimes, typed agent frameworks, bi-temporal memory, evals, and protocols. |
| [Disjoint L0–L10 Convergence Stack](convergence-stack.md) | Zero-overlap layer ownership, Mermaid architecture diagrams, cross-session routing, and drop-in `.agents/` safety templates. |
| [Compounding Flywheel & KPIs](compounding-flywheel.md) | 2025–2026 compounding & self-improving harness research, 7-stage flywheel, probabilistic-to-deterministic escalation ladder, anti-bloat ratchets, and operational KPIs. |
| [Clean Upstream Install Registry](clean-install-registry.md) | Exact `2026-11-26` pinned versions, isolated `uv`/`mise`/`npm` install commands, and post-install smoke checks across `L0`–`L10`. |
| [Context & Manifest Audit](context-manifest-audit.md) | Empirical startup token telemetry, zero-secret `context_manifest_scorecard`, and live workstation parity evidence. |
| [GitHub SOTA Workflows](github-sota-workflows.md) | Unified 4-repo ecosystem governance, 40-char SHA pins, `harden-runner`, `zizmor`, and reusable `workflow_call` adoption guide. |
| [Sealed Manifest v3.1 Guide](manifest-guide.md) | Canonical SHA-256 seal, 12/12 ADR hash ledger, 17-gate `--verify` instructions, and adversarial negative-guard evidence. |

---

## Bounded 12-ADR Architecture Ledger (`META` + `L0`–`L10`)

Browse the full indexed summary in the [ADR Catalog (`docs/adrs/CATALOG.md`)](adrs/CATALOG.md), or open any individual MADR 4.0.0 decision record below:

| ADR | Layer | Architectural Scope |
| :--- | :--- | :--- |
| [ADR-0001](adrs/ADR-0001-meta-adr-convergence-and-zero-self-invention.md) | `META` | Bounded 12-ADR MADR 4.0.0 governance, Zero-Self-Invention Gate & cryptographic manifest sealing |
| [ADR-0002](adrs/ADR-0002-L0-execution-isolation-and-sandboxes.md) | `L0` | Local OS-native sandboxes (namespaces / Seatbelt / Windows AppContainer) & cloud Firecracker/gVisor microVMs |
| [ADR-0003](adrs/ADR-0003-L1-frontier-models-routing-and-sunsets.md) | `L1` | Frontier Gemini 4 (`Neon`/`Carbon`/`Hydrogen`), Orchestrator routing, Claude 5.5, local LiteRT & Nov-30 sunset gate |
| [ADR-0004](adrs/ADR-0004-L2-multi-surface-agy-harness-and-acp.md) | `L2` | Unified 5 AGY surfaces (App 2.0, Go `agy` CLI, IDE, 7 IDE extensions, Python SDK) & native `agy acp` |
| [ADR-0005](adrs/ADR-0005-L3-intra-session-multi-agent-orchestration.md) | `L3` | Tiered intra-session orchestration: subagents, `/swarm`, `/run-workflow`, `/boost`, `/teamwork` |
| [ADR-0006](adrs/ADR-0006-L4-cross-session-and-federated-messaging.md) | `L4` | `ConversationService`, Sidecars `agentapi`, Hooks, Remote/SSH, Orca mail/worktrees & A2A v1.0 |
| [ADR-0007](adrs/ADR-0007-L5-vertical-mcp-apps-and-code-mode.md) | `L5` | MCP `2026-07-28` stateless core, Tasks extension, MCP Apps (`SEP-1865`), Code Mode/PTC & `SEP-2577` ban |
| [ADR-0008](adrs/ADR-0008-L6-durable-cloud-workflows-and-frameworks.md) | `L6` | Production frameworks (ADK, PydanticAI v2, LangGraph 1.0, MAF 1.0, Mastra 1.0) + DBOS/Restate/Temporal durability |
| [ADR-0009](adrs/ADR-0009-L7-tri-layer-compounding-memory.md) | `L7` | Tri-layer memory: procedural (`AGENTS.md`/`SKILL.md`/`/learn`), episodic (transcripts/MemFS), semantic MCP (`graphiti-core`/`mem0ai`/`xerj`/`codebase-memory-mcp`) |
| [ADR-0010](adrs/ADR-0010-L8-deterministic-security-and-fail-closed-gates.md) | `L8` | `Deny > Ask > Allow`, fail-closed `PreToolUse` hooks, AST/secret/supply-chain CI gates (`ruff`/`ty`/`gitleaks`/`zizmor`) |
| [ADR-0011](adrs/ADR-0011-L9-adversarial-evals-and-trace-optimization.md) | `L9` | `SkillEvaluator` Tiers 1–3, `inspect-ai` + `harbor` isolated verifiers, `promptfoo` red-teaming & `dspy`/`gepa` trace reflection |
| [ADR-0012](adrs/ADR-0012-L10-telemetry-provenance-and-compounding-manifest.md) | `L10` | OTel GenAI semantic tracing (incl. native SDK), provenance/hygiene auditing & 17-gate SHA-256 manifest governance |

---

## Verification Fitness Gate

```bash
bash scripts/check.sh
```
