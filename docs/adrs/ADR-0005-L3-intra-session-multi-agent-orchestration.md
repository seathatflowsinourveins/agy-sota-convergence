---
id: ADR-0005
layer: L3
status: accepted
date: 2026-11-26
decision-makers: SOTA Convergence Swarm (Verified 2026-11-26)
consulted: [sota-ecosystem, cross-session, changelogs, best-practices]
informed: [verifier, coordinator]
---

# ADR-0005: L3 — Intra-Session Multi-Agent Orchestration (AGY 4-Tier Native Routing)

## Context and Problem Statement

Complex software engineering, research, and audit tasks routinely outgrow a single linear context window: exploratory reads bloat token budgets, sequential file audits stall wall-clock throughput, and a single author reviewing its own edits suffers from confirmation bias. However, deploying a single multi-agent pattern for every task either wastes quota (spawning full swarms for a 20-second lookup) or collapses into brittle custom thread pools. How should Layer `L3` standardize **intra-session** multi-agent coordination cleanly without encroaching on `L4` (cross-session/cross-host messaging) or `L6` (multi-day crash-proof cloud durability)?

## Decision Drivers

- **Task-Shape Alignment:** Distinct workload shapes (focused side-lookup, peer-collaborative feature split, deterministic N-file fan-out, adversarial deep debugging, multi-milestone repo migration) demand purpose-built coordination topologies.
- **Zero-Token Idle Waiting & Context Hygiene:** Idle workers must sleep without burning generation tokens; verbose tool outputs must stay isolated from the coordinator's main context window.
- **Filesystem Safety for Parallel Edits:** Concurrent editors must operate on exclusive file slices or isolated working copies (`workspace: "branch"` / `"share"`) and land changes before worker teardown.
- **Independent Verification:** Multi-worker outputs must pass an independent verifier (`@verifier`, adversarial improvement rounds, or milestone audit gates) before returning to the user.
- **Zero Self-Invention:** Eliminate bespoke Python `asyncio.gather` LLM fan-out harnesses when AGY natively ships Subagents, `/swarm`, `/run-workflow`, `/boost`, and `/teamwork`.

## Considered Options

1. **Option 1 (Chosen): AGY 4-Tier Native Intra-Session Orchestration Matrix** — strictly routing by task shape across **Subagents** (`invoke_subagent`/`send_message`), **Native Swarms** (`/swarm`), **Dynamic Python Workflows** (`/run-workflow` & SDK `beta.workflows`), and **Specialized Paid Orchestrators** (`/boost` & `/teamwork`).
2. **Option 2 (Rejected): Single-Agent Monolithic Context with Manual `/compact` Only.**
3. **Option 3 (Rejected): Custom In-House Python `ThreadPoolExecutor` / `asyncio` Multi-Agent Orchestrator Calling Raw Model APIs.**

## Decision Outcome

Chosen option: **Option 1 — AGY 4-Tier Native Intra-Session Orchestration Matrix**, routing every intra-session multi-agent task deterministically by shape:

- **Focused side delegation (seconds–minutes):** Built-in or `.agents/agents/*.md` **Subagents** (`invoke_subagent`, `send_message`, `manage_subagents`; max 10-level nesting depth; clean context; `Running`/`Idle`/`Killed` lifecycle).
- **Broad peer-collaborative work (minutes–hours):** **Native Swarm (`/swarm`)** — coordinator + named workers/pools + `@verifier` + `@monitor` (`swarm_monitor` skill with `*/3 * * * *` `IsDaemon: true` stall detection) on an ordered public board with `@mentions` (wakeup doorbells, never CCs), optional channels, `fork`, zero-token `swarm_wait{since: LAST}`, and history-preserving `swarm{action:"model"}` quota recovery.
- **Deterministic scripted fan-out / staged pipelines:** **Dynamic Python Workflows (`/run-workflow` / SDK `beta.workflows`)** — launched in SDK `v0.1.22` (Oct 12, 2026), expanded in SDK `v0.1.23` (Oct 26, 2026: `call_tool`, stateful multi-turn `WorkflowAgent`, `args`), and shipped in App `v2.32.0` (Nov 13, 2026) and CLI `v1.5.9` (Nov 14, 2026). Uses `phase()`, `parallel()` (fail-fast), `pipeline()`, `await trajectory()`, and JSON Schema `finish` outputs so isolated agents never pollute the parent context.
- **Hard algorithmic/concurrency bugs or multi-milestone campaigns (paid plans):** **`/boost`** (`Orchestrator` -> `DeepCoder`/`DeepInvestigator` -> challenge/fix rounds) for depth, and **`/teamwork`** (`Sentinel`, `Project Orchestrator` with milestone successor rotation, `Critic`, `Challenger`, `Auditor`, `Success Auditor` in `~/teamwork_projects/{PROJECT_NAME}`) for multi-day campaigns.

### Consequences

- **Good:** Zero custom orchestration infrastructure; idle swarm workers cost zero tokens (`swarm_wait`); workflow agents return strictly JSON-Schema-validated payloads; parallel edit isolation (`workspace: "branch"|"share"`) prevents merge corruption; CLI `v1.5.16` fixed `/swarm` wakeup attribution to `"system"` preventing compaction/timer collisions.
- **Good:** Clean separation from `L4` (cross-session/cross-host) and `L6` (durable cloud crash-replay), with zero overlapping responsibility.
- **Bad:** Parallel workers consume model quota proportionally faster than a single thread; `run_workflow`'s `call_tool()` cannot interactively prompt the user (ungranted calls raise `ToolError` with `.denied == True`); `parallel()` cancels all sibling agents on a single failure; `/boost` and `/teamwork` require paid plans.
- **Neutral:** Killing a subagent or swarm worker permanently deletes its `share`/`branch` working copy—changes must always be merged/landed before `kill`.

### Confirmation

Run the following executable fitness checks from the repository root:

```bash
# 1. Verify custom agent markdown definitions (when present) have valid YAML frontmatter
python3 -c '
import pathlib, re
for p in pathlib.Path(".agents/agents").glob("*.md") if pathlib.Path(".agents/agents").exists() else []:
    txt = p.read_text(encoding="utf-8")
    assert txt.startswith("---\n") and re.search(r"^name:\s*\S+", txt, re.M), f"Invalid agent frontmatter: {p}"
print("L3_CUSTOM_AGENTS_OK")
'

# 2. Validate saved Dynamic Workflow Python scripts (when present) parse cleanly
python3 -c '
import ast, pathlib
for p in pathlib.Path(".agents/workflows").glob("*.py") if pathlib.Path(".agents/workflows").exists() else []:
    ast.parse(p.read_text(encoding="utf-8"))
print("L3_WORKFLOW_SCRIPTS_OK")
'

# 3. Ensure no custom polling loops target read_board or subagent status in .agents/
! grep -rnE "while\s+True.*(read_board|manage_subagents)" .agents/

# 4. Verify manifest seal & L3 disjointness gate pass cleanly
python3 scripts/verify_manifest.py --verify
```

## Pros and Cons of the Options

### Option 1: AGY 4-Tier Native Intra-Session Orchestration Matrix
- **Pros:** Covers every intra-session topology natively across App `v2.35.2`, CLI `v1.5.18`, and SDK `v0.1.24`; enforces structured schemas (`run_workflow`), public audit trails (`/swarm`), and adversarial verification (`@verifier`, `/boost`, `/teamwork`); passes the 5-Question Zero-Self-Invention test completely (declarative `.agents/agents/*.md` and short workflow scripts only).
- **Cons:** Requires operator discipline to pick the lightest sufficient tier (avoiding `/swarm` for single-file edits or `run_workflow` when peers need organic mid-flight negotiation).

### Option 2: Single-Agent Monolithic Context with Manual `/compact` Only
- **Pros:** Lowest token burn for simple, sequential edits.
- **Cons:** **Rejected** — fails on broad parallel audits and multi-package implementations due to context rot, lossy repeated compactions, lack of independent verification, and serialized wall-clock latency.

### Option 3: Custom Python `asyncio` / Thread-Pool Multi-Agent Orchestrator
- **Pros:** Arbitrary low-level control over HTTP requests.
- **Cons:** **Rejected (Fails Zero-Self-Invention Gate)** — duplicates AGY's native `run_workflow` (`parallel`/`pipeline`/JSON Schema `finish`/bundled Python), loses native UI cards, permission bubbling (`Alt+J`/`Ctrl+K`), OS sandboxing (`L0`), and OTel spans (`L10`), and creates chronic maintenance drag against upstream releases.

## Clean Upstream Installation & Adapter Boundary

| Scope | Canonical Upstream | Registry / Channel | Exact Verified Version (`2026-11-26`) | Clean Pinned Install Command | Post-Install Smoke / Verify Command |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Interactive App / CLI** | AGY Subagents, `/swarm`, `/run-workflow`, `/boost`, `/teamwork` | Bundled in AGY App & `agy` CLI | App `2.35.2` / CLI `1.5.18` *(docs `1.5.16`)* | Bundled in Antigravity App & `agy` (bundled Python 3.8+ runtime included; optional `ANTIGRAVITY_PYTHON` override) | `agy --version && agy agents` |
| **Programmatic Python** | `google-antigravity` SDK (`SubagentConfig`, `beta.workflows`) | PyPI | `0.1.24` (`2026-11-19`) | `uv add "google-antigravity==0.1.24"` *(wheel includes compiled `localharness` binary)* | `uv run python -c "import google.antigravity as ag; print(ag.__file__)"` |

**Thin-Adapter Boundary:** Repositories contain only declarative `.agents/agents/<name>.md` personas (verifying exact tool names to avoid known hangs on misspelled tools) and concise `run_workflow` `.py` + `workflow.json` scripts (using `agent()`, `parallel()`, `pipeline()`, `call_tool()`, `trajectory()`). Zero custom agent-loop runners or polling supervisors.

## More Information

- Antigravity Swarm (`/swarm`): `https://antigravity.google/docs/swarm.md`
- Antigravity Dynamic Workflows (`/run-workflow`): `https://antigravity.google/docs/dynamic-workflows.md`
- Antigravity Custom Subagents: `https://antigravity.google/docs/subagents.md`
- Antigravity Boost (`/boost`) & Teamwork (`/teamwork`): `https://antigravity.google/docs/boost.md`, `https://antigravity.google/docs/teamwork.md`
- Antigravity SDK Subagents: `https://antigravity.google/docs/sdk/subagents.md`
- Repository Architecture & Registry: [Convergence Stack](../convergence-stack.md), [Clean Upstream Installation Registry](../clean-install-registry.md), [Manifest Guide](../manifest-guide.md)
