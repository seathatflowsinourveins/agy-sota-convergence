# Architecture Decision Record Catalog (Bounded 12-ADR MADR 4.0.0 Set)

**Catalog Baseline:** 2026-11-26  
**Governance Invariant:** Strictly **12** accepted MADR 4.0.0 records — `ADR-0001` (`META`) plus a 1:1 bijection between `ADR-0002`..`ADR-0012` and architectural layers `L0`–`L10`. Revise or supersede in place; never spawn `ADR-0013` or duplicate layer decisions.

---

## 1. Structural & Cryptographic Verification Contract

Every ADR linked in this catalog is mechanically verified by `scripts/verify_manifest.py --verify` (`Gate [11]` `adr_12_bounded_bijection_and_madr4` structural contract + `Gate [12]` `adr_files_sha256_parity` per-file SHA-256 parity against `manifest/compounding_manifest.v2.json`):

1. **7-Key YAML Frontmatter:** `id`, `layer`, `status: accepted`, `date: 2026-11-26`, `decision-makers`, `consulted`, `informed`.
2. **9 Ordered MADR 4.0.0 Headings:** `## Context and Problem Statement`, `## Decision Drivers`, `## Considered Options`, `## Decision Outcome`, `### Consequences`, `### Confirmation`, `## Pros and Cons of the Options`, `## Clean Upstream Installation & Adapter Boundary`, and `## More Information`.
3. **Zero-Self-Invention & Repo-Relative Fitness Checks:** Every ADR passes the 5-Question Zero-Self-Invention Gate (`ADR-0001`) and includes executable repo-relative `### Confirmation` commands.

---

## 2. Master 12-ADR Decision Matrix (`ADR-0001`–`ADR-0012`)

| ADR | Layer | Status & Date | Title | Canonical Decision Outcome | Primary Pinned Upstreams |
| :--- | :---: | :---: | :--- | :--- | :--- |
| [**ADR-0001**](ADR-0001-meta-adr-convergence-and-zero-self-invention.md) | `META` | `accepted` (`2026-11-26`) | Bounded 12-ADR MADR 4.0.0 Governance, Zero-Self-Invention Gate & Cryptographic Convergence Manifest | Enforce a bounded 12-ADR MADR 4.0.0 bijection (`META` + `L0`–`L10`), mandatory 5-Question Zero-Self-Invention Gate, and SHA-256 sealed compounding manifest. | `zensical 0.1.3`, `verify_manifest.py` (stdlib) |
| [**ADR-0002**](ADR-0002-L0-execution-isolation-and-sandboxes.md) | `L0` | `accepted` (`2026-11-26`) | Execution Isolation and Sandboxes (OS-Native Local + MicroVM/gVisor Cloud) | Split isolation cleanly: AGY OS-native terminal sandboxes locally (macOS Seatbelt, Linux namespaces, Windows AppContainer) + Firecracker/gVisor/Edge sandboxes in cloud. | AGY Sandbox (`App 2.35.2` / `agy 1.5.18`), `e2b 2.66.0`, `daytona 2.3.0`, `modal 1.6.4`, `@cloudflare/sandbox 1.0.3` |
| [**ADR-0003**](ADR-0003-L1-frontier-models-routing-and-sunsets.md) | `L1` | `accepted` (`2026-11-26`) | Frontier Models, Thinking Effort Routing, Local Runtimes & Sunset Enforcement | Standardize on post-Nov-30 AGY frontier models (`gemini-4-neon`, `gemini-4-carbon`, `gemini-4-hydrogen`, `claude-opus-5-5`, `claude-sonnet-5-5`), native `Orchestrator` + effort tiers, and SDK local runtimes; hard-ban Nov-30 retiring slugs. | AGY Hosted Models & `Orchestrator`, `litert-lm 0.20.0`, `google-antigravity 0.1.24` |
| [**ADR-0004**](ADR-0004-L2-multi-surface-agy-harness-and-acp.md) | `L2` | `accepted` (`2026-11-26`) | Multi-Surface Google Antigravity Harness, 7 IDE Extensions & ACP Interoperability | Standardize on the unified AGY harness (`App`, `agy`, 7 IDE extensions via `agy acp`, Python SDK) sharing `.agents/` & `~/.gemini/config/`; exclude standalone IDE from Enterprise and retire consumer `gemini-cli`. | `App 2.35.2`, `agy 1.5.18`, `google-antigravity 0.1.24`, `antigravity-acp 1.5.0`, VS Code `1.13.0`, VS `1.0.261116.0`, Eclipse `1.2.0` |
| [**ADR-0005**](ADR-0005-L3-intra-session-multi-agent-orchestration.md) | `L3` | `accepted` (`2026-11-26`) | Intra-Session Multi-Agent Orchestration (AGY 4-Tier Native Routing) | Route intra-session multi-agent tasks deterministically by shape across AGY's four native tiers: `Subagents`, `/run-workflow` (Dynamic Workflows), `/swarm` (Shared Board), and `/teamwork` / `/boost`. | Native AGY `invoke_subagent`, `run_workflow`, `swarm`, `workflows/sota_convergence_audit.py` |
| [**ADR-0006**](ADR-0006-L4-cross-session-and-federated-messaging.md) | `L4` | `accepted` (`2026-11-26`) | Cross-Session, Multi-Host, and Federated Agent Messaging | Partition cross-session transport strictly by scope: `ConversationService` + typed SHA-256 handoff packets + Sidecars (`agentapi`) + deduplicated Hooks locally; SSH/Remote Agents cross-host; `orca` for heterogeneous worktrees; `A2A v1.0` across orgs. | AGY `ConversationService` (`v2.35.0+`), Sidecars, `orca v1.4.278`, `a2a-sdk 1.3.1`, `@a2a-js/sdk 1.3.0` |
| [**ADR-0007**](ADR-0007-L5-vertical-mcp-apps-and-code-mode.md) | `L5` | `accepted` (`2026-11-26`) | Vertical Tool, Data, and UI Protocol (MCP 2026-07-28 Stateless Core, MCP Apps & Code Mode) | Adopt MCP `2026-07-28` Stateless Streamable HTTP, CIMD/RFC 9207 auth, MCP Apps (`SEP-1865`), and lazy loading / Code Mode above 20–30 endpoints; ban legacy HTTP+SSE (`McpSseServer`). | `mcp 2.3.0`, `@modelcontextprotocol/sdk 1.32.2`, `@modelcontextprotocol/ext-apps 2.0.4` |
| [**ADR-0008**](ADR-0008-L6-durable-cloud-workflows-and-frameworks.md) | `L6` | `accepted` (`2026-11-26`) | Durable Cloud Workflow Execution and Production Agent Frameworks | Layer durable cloud execution (`DBOS` / `Restate` / `Temporal`) beneath typed production frameworks (`google-adk`, `pydantic-ai`, `langgraph`, `agent-framework`, `mastra`, `openai-agents`, `claude-agent-sdk`, `strands-agents`); ban maintenance-mode AutoGen & Semantic Kernel. | `dbos 3.7.0`, `temporalio 1.37.0`, `restate-sdk 1.5.5`, `google-adk 2.15.1`, `pydantic-ai 2.75.0`, `langgraph 1.2.24`, `agent-framework 1.26.0` |
| [**ADR-0009**](ADR-0009-L7-tri-layer-compounding-memory.md) | `L7` | `accepted` (`2026-11-26`) | Tri-Layer Compounding Memory (Procedural, Episodic & Bi-Temporal Semantic MCP) | Partition memory into three non-overlapping layers: procedural (`AGENTS.md`, `.agents/rules/`, `SKILL.md`), episodic/code-corpus (`codebase-memory-mcp`, `xerj`, SQLite conversations), and bi-temporal semantic MCP (`graphiti-core`, `letta`, `mem0ai`). | `codebase-memory-mcp 0.12.1`, `xerj v1.0.0-rc.105`, `graphiti-core 0.32.1`, `letta 0.34.12`, `mem0ai 2.2.1` |
| [**ADR-0010**](ADR-0010-L8-deterministic-security-and-fail-closed-gates.md) | `L8` | `accepted` (`2026-11-26`) | Deterministic Security, Permissions, and Fail-Closed Policy Gates | Combine AGY native permissions (resolved absolute paths, zero `~/`), fail-closed `PreToolUse` hooks (`exit 0` + `{"decision":"deny"}`), structural `ast-grep` bans, and pinned static security scanners (`ruff`, `ty`, `gitleaks`, `trivy`, `osv-scanner`, `shellcheck`, `zizmor`, `syft`). | `ruff 0.17.6`, `ty 0.0.112`, `ast-grep 0.51.3`, `gitleaks 8.30.1`, `trivy 0.76.2`, `osv-scanner 2.7.1`, `shellcheck 0.11.0`, `zizmor 1.33.1`, `syft 1.57.2` |
| [**ADR-0011**](ADR-0011-L9-adversarial-evals-and-trace-optimization.md) | `L9` | `accepted` (`2026-11-26`) | Adversarial Evaluation, Isolated Sandboxed Verification & Trace-to-Skill Optimization | Enforce four-pillar isolated evaluation & optimization: `Inspect AI` + `Harbor` (Terminal-Bench 2.0 / SWE-bench Pro V2), `Promptfoo` red-teaming, `SkillEvaluator` Tier 1–3 skill CI gating, and `DSPy` + `GEPA` trace reflection. | `inspect-ai 0.3.292`, `harbor 0.27.0`, `promptfoo 0.126.0`, `dspy 3.5.0`, `gepa 0.1.4`, `skillevaluator 1.2.1` |
| [**ADR-0012**](ADR-0012-L10-telemetry-provenance-and-compounding-manifest.md) | `L10` | `accepted` (`2026-11-26`) | Telemetry, Provenance, ADR Governance, and Cryptographic Compounding Manifest | Unify OpenTelemetry GenAI semantic conventions, Zensical strict MADR 4.0.0 publishing, and the stdlib SHA-256 sealed Compounding Manifest (`scripts/verify_manifest.py`) for deterministic compounding governance. | `opentelemetry-sdk 1.45.2`, `zensical 0.1.3`, `scripts/verify_manifest.py` |

---

## 3. Executable Confirmation & Re-Seal Quick Reference

Run the unified fail-closed local gate runner from the repository root to verify all 12 ADRs, hooks, static bans, security scanners, SkillEvaluator Tier 1, SBOM/OSV, and the strict Zensical portal in one pass:

```bash
# Unified full verification suite (all local gates)
bash scripts/check.sh

# Or via Makefile
make check
```

### Targeted Per-Domain Confirmation Commands

| Scope | Executable Command (Run From Repository Root) |
| :--- | :--- |
| **Bounded 12-ADR + Cryptographic Manifest (`ADR-0001`, `ADR-0012`)** | `python3 scripts/verify_manifest.py --verify && python3 scripts/verify_manifest.py --verify` |
| **Re-Seal After Authorized ADR / Manifest Edit (`ADR-0001`, `ADR-0012`)** | `python3 scripts/verify_manifest.py --seal && python3 scripts/verify_manifest.py --verify` |
| **Sandboxes, Hooks, Handoff Schema & Live Host Shim (`ADR-0002`, `ADR-0006`, `ADR-0010`)** | `python3 -m unittest discover -s tests -v` |
| **Sunset Models, Live Broker Ports, Legacy Imports & Fail-Open Hook Exits (`ADR-0003`, `ADR-0007`, `ADR-0008`, `ADR-0010`)** | `ast-grep scan && ast-grep scan --no-ignore hidden` |
| **Multi-Surface Harness & ACP Availability (`ADR-0004`)** | `agy --version && agy acp --help >/dev/null` |
| **Read-Only Host Ecosystem & Context Scorecard (`ADR-0009`, `ADR-0010`)** | `python3 scripts/audit_ecosystem_hygiene.py --json --strict` |
| **Static Lint, Type, Shell, Actions, Secret & SBOM/OSV Gates (`ADR-0010`)** | `ruff check . && ruff format --check . && ty check && shellcheck scripts/*.sh && zizmor --offline .github/workflows/ && gitleaks detect --no-git --redact --source .` |
| **Keyless SkillEvaluator Tier-1 Gate (`ADR-0011`)** | `make skill-eval` *(runs `skillevaluator tier1 .agents/skills/sota-convergence-audit --no-llm` in a temporary output directory)* |
| **Strict MADR 4.0.0 Documentation Portal (`ADR-0001`, `ADR-0012`)** | `zensical build --clean --strict` |

---

## 4. Related Repository Guides

- [Overview](../index.md)
- [Convergence Stack (`L0`–`L10`)](../convergence-stack.md)
- [AGY Surfaces, Changelogs & Sunsets](../agy-surfaces-and-changelogs.md)
- [Clean Upstream Install Registry](../clean-install-registry.md)
- [ADR & Convergence Practice](../adr-and-convergence-practice.md)
- [Compounding Manifest Guide](../manifest-guide.md)
