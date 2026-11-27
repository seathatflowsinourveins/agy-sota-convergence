---
id: ADR-0008
layer: L6
status: accepted
date: 2026-11-26
decision-makers: SOTA Convergence Swarm (Verified 2026-11-26)
consulted: [sota-ecosystem, cross-session, changelogs, best-practices]
informed: [verifier, coordinator]
---

# ADR-0008: L6 — Durable Cloud Workflow Execution and Production Agent Frameworks

## Context and Problem Statement

Interactive developer harnesses (`L2`/`L3`) excel at laptop-local and short-to-medium coding loops, but production backend agent pipelines routinely run across hours or weeks, hit `429` rate limits, survive container restarts and rolling deploys, and suspend indefinitely waiting on human approvals or external A2A/webhook signals. Re-running non-idempotent side-effect tools or re-burning millions of prompt tokens after a pod eviction is operationally unacceptable. Meanwhile, legacy multi-agent frameworks (`AutoGen`, `Semantic Kernel`) entered maintenance mode in 2026 in favor of typed, durable-execution-native stacks. How should Layer `L6` pair durable execution engines with typed application frameworks without overlapping `L3` (intra-session orchestration) or `L7` (semantic/temporal memory)?

## Decision Drivers

- **Crash-Proof Event-Sourced Replay:** Long-running agent loops must resume at the exact post-tool checkpoint after host crashes, OOM kills, or deployments with zero duplicate side-effect execution.
- **Zero-Compute Indefinite HITL Suspension:** Multi-day human approval gates and async external webhooks must not hold idle worker containers or open HTTP sockets.
- **Right-Sized Operational Footprint:** Single-database teams need zero-cluster durability (`DBOS`), serverless edge/event teams need replicated-log scale-to-zero (`Restate`), and enterprise multi-service fleets need battle-tested replay orchestration (`Temporal`).
- **Typed Framework Convergence (Zero Legacy Debt):** Select strictly active, production-typed frameworks (**Google ADK**, **PydanticAI v2**, **LangGraph 1.0**, **Mastra 1.0**, **Microsoft Agent Framework 1.0 GA**, **OpenAI Agents SDK**, **Claude Agent SDK**, **AWS Strands Agents**) and ban maintenance-mode `AutoGen` / `Semantic Kernel` for greenfield work.
- **Strict Layer Disjointness (`L6` vs. `L7`):** `L6` owns execution checkpointing and activity replay; cross-session semantic/bi-temporal knowledge stays exclusively in `L7`.

## Considered Options

1. **Option 1 (Chosen): Layered Upstream Durability (`DBOS` / `Restate` / `Temporal`) Hosting Typed Production Frameworks (`Google ADK`, `PydanticAI v2`, `LangGraph 1.0`, `Mastra 1.0`, `MAF 1.0`)** — with AGY App `v2.35.1` auto-resume + SDK `LocalAgentConfig(save_dir, conversation_id)` reserved strictly for single-node local persistence.
2. **Option 2 (Rejected): Maintenance-Mode Legacy Frameworks (`AutoGen` / `Semantic Kernel`) or Bare In-Memory Async Loops with Cron/SQL Polling Retries.**
3. **Option 3 (Rejected): Custom In-House Distributed Workflow / State-Machine Queue Engine Built on Redis/Postgres.**

## Decision Outcome

Chosen option: **Option 1 — Layered Upstream Durability (`DBOS` / `Restate` / `Temporal`) Hosting Typed Production Frameworks**, selecting the durability engine by operational scale and the application framework by runtime ecosystem:

- **Durability Engine Selection (Disjoint by Scale):**
  - **Lightweight / Zero-Cluster (Postgres/SQLite already present):** **`DBOS`** (`dbos==3.7.0`) — checkpoints every LLM/tool/MCP call directly into Postgres or SQLite; pairs natively with PydanticAI (`DBOSDurability`) and LangGraph.
  - **Serverless / Scale-to-Zero Event Services:** **`Restate`** (`restate-sdk==1.5.5`) — replicated execution log + embedded KV state for pausable, steerable agents (OpenAI Agents SDK, PydanticAI `RestateAgent`).
  - **Enterprise Multi-Service / Multi-Week Workflows:** **`Temporal`** (`temporalio==1.37.0`) — gold-standard deterministic event-sourced replay wrapping LLM/tool calls as Activities with native Signals for indefinite HITL pauses (Temporal LangGraph Plugin, PydanticAI `TemporalDurability`, OpenAI Agents SDK).
  - **Single-Node Local SDK Persistence (Non-Clustered):** AGY App `v2.35.1` restart auto-resume + `google-antigravity==0.1.24` `LocalAgentConfig(save_dir=..., conversation_id=...)` (strictly `>= 32` chars, `[A-Za-z0-9-]` only, no underscores).
- **Typed Framework Selection (Disjoint by Stack):**
  - **Google Cloud / Polyglot / Native A2A+MCP:** **Google ADK** (`google-adk==2.15.1`).
  - **Python Strict Type Safety + Multi-Durability Adapters:** **PydanticAI v2** (`pydantic-ai==2.75.0`, 9 native durability adapters).
  - **Explicit Cyclical State Graphs + Time-Travel Checkpoints:** **LangGraph 1.0** (`langgraph==1.2.24` / `@langchain/langgraph@1.7.5`).
  - **TypeScript Full-Stack (Next.js/Node):** **Mastra 1.0** (`mastra@1.40.2`, `@mastra/core@1.86.0`).
  - **Microsoft / .NET / Azure Enterprise:** **Microsoft Agent Framework 1.0 GA** (`agent-framework==1.26.0`, NuGet `Microsoft.Agents.AI 1.28.0`, officially superseding AutoGen + Semantic Kernel).
  - **First-Party Lab / AWS Cloud Native:** **OpenAI Agents SDK** (`openai-agents==0.26.0`), **Claude Agent SDK** (`claude-agent-sdk==0.2.189`), **AWS Strands Agents** (`strands-agents==1.67.0`).

### Consequences

- **Good:** Eliminates crash-induced duplicate tool side effects and lost multi-hour progress; cleanly separates deterministic orchestration replay from non-deterministic LLM/tool Activities; eliminates legacy maintenance debt from deprecated `AutoGen` and `Semantic Kernel`.
- **Good:** Native first-party integrations (Temporal LangGraph Plugin, PydanticAI `TemporalDurability`/`DBOSDurability`/`RestateAgent`) require minimal glue code and emit OTel GenAI traces (`L10`).
- **Bad:** Deterministic workflow replay (Temporal/Restate) requires strict discipline—no unguarded `datetime.now()`, random UUIDs, or direct network I/O outside durable Activities/steps; Temporal clusters carry operational overhead unwarranted for simple single-machine jobs (use DBOS or AGY SDK persistence there).
- **Neutral:** Framework choice inside `L6` remains cleanly swappable because tools (`L5`), inter-agent calls (`L4`), memory (`L7`), and telemetry (`L10`) sit behind open AAIF/CNCF protocol boundaries.

### Confirmation

Run the following executable fitness gates from the repository root:

```bash
# 1. Verify zero legacy maintenance-mode AutoGen or Semantic Kernel dependencies in project manifests
! grep -rnE "(pyautogen|autogen-agentchat|semantic-kernel)" pyproject.toml requirements*.txt package.json 2>/dev/null

# 2. Verify AGY SDK persistence conversation_id conforms to >=32-char alphanumeric+hyphen rule (no underscores)
python3 -c '
import re
sample_id = "session-12345678901234567890123456789012"
assert re.fullmatch(r"[A-Za-z0-9-]{32,}", sample_id), "Invalid AGY SDK conversation_id"
print("L6_SDK_CONVERSATION_ID_RULE_OK")
'

# 3. Verify manifest seal & L6 clean-install registry pins pass cleanly
python3 scripts/verify_manifest.py --verify
```

## Pros and Cons of the Options

### Option 1: Layered Upstream Durability (`DBOS`/`Restate`/`Temporal`) + Typed Production Frameworks
- **Pros:** Proven crash recovery, zero-compute HITL suspension, clean scaling ladder from SQLite (`DBOS`) to enterprise distributed clusters (`Temporal`), full type safety, zero vendor lock-in; passes the 5-Question Zero-Self-Invention test.
- **Cons:** Developers must respect deterministic workflow-code vs. side-effect Activity boundaries.

### Option 2: Maintenance-Mode Legacy Frameworks (`AutoGen`/`Semantic Kernel`) or Bare Async Loops
- **Pros:** Low initial learning curve for throwaway prototypes.
- **Cons:** **Rejected** — `AutoGen` and `Semantic Kernel` are officially superseded by Microsoft Agent Framework 1.0 GA; bare async loops lose state on pod eviction, duplicate side effects on retry, and tie up compute during human approval pauses.

### Option 3: Custom In-House Postgres/Redis Job-Queue State Machine
- **Pros:** No external workflow SDK dependency.
- **Cons:** **Rejected (Fails Zero-Self-Invention Gate)** — inevitably recreates a buggy subset of DBOS/Restate/Temporal (handling partial retries, poison pills, signal races, replay versioning, and dead-letter recovery) with high ongoing maintenance drag.

## Clean Upstream Installation & Adapter Boundary

| Scope | Canonical Upstream | Registry / Channel | Exact Verified Version (`2026-11-26`) | Clean Pinned Install Command | Post-Install Smoke / Verify Command |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Zero-Cluster Durability** | DBOS Python (`dbos`) | PyPI | `3.7.0` (`2026-11-24`) | `uv add "dbos==3.7.0"` | `uv run python -c "import dbos; print(dbos.__version__)"` |
| **Enterprise Durability** | Temporal Python SDK (`temporalio`) | PyPI | `1.37.0` (`2026-11-24`) | `uv add "temporalio==1.37.0"` | `uv run python -c "import temporalio; print(temporalio.__version__)"` |
| **Serverless Durability** | Restate Python SDK (`restate-sdk`) | PyPI | `1.5.5` (`2026-11-24`) | `uv add "restate-sdk==1.5.5"` | `uv run python -c "import restate; print(restate.__file__)"` |
| **Google Cloud / Polyglot** | Google ADK (`google-adk`) | PyPI | `2.15.1` (`2026-11-25`) | `uv add "google-adk==2.15.1"` | `uv run adk --version` |
| **Typed Python + 9 Durability Adapters** | PydanticAI v2 (`pydantic-ai`) | PyPI | `2.75.0` (`2026-11-25`) | `uv add "pydantic-ai==2.75.0"` | `uv run python -c "import pydantic_ai; print(pydantic_ai.__version__)"` |
| **Cyclical State Graph** | LangGraph 1.0 (`langgraph` / `@langchain/langgraph`) | PyPI / npm | `1.2.24` (`2026-11-20`) / `1.7.5` | `uv add "langgraph==1.2.24"` *(TS: `npm install --save-exact @langchain/langgraph@1.7.5`)* | `uv run python -c "import langgraph; print(langgraph.__file__)"` |
| **Microsoft Enterprise** | Microsoft Agent Framework 1.0 (`agent-framework`) | PyPI | `1.26.0` (`2026-11-12`) | `uv add "agent-framework==1.26.0"` | `uv run python -c "import agent_framework; print(agent_framework.__file__)"` |
| **TypeScript Full-Stack** | Mastra 1.0 (`mastra`, `@mastra/core`) | npm | `1.40.2` / `1.86.0` | `npm install --save-exact mastra@1.40.2 @mastra/core@1.86.0` | `npx mastra --version` |
| **Lab / AWS SDKs** | `openai-agents` / `claude-agent-sdk` / `strands-agents` | PyPI | `0.26.0` / `0.2.189` / `1.67.0` | `uv add "openai-agents==0.26.0"` *(or `"claude-agent-sdk==0.2.189"`, `"strands-agents==1.67.0"`)* | `uv run python -c "import agents; print(agents.__file__)"` |

**Thin-Adapter Boundary:** Application code defines only declarative typed schemas/graphs and thin Activity/Step wrappers binding chosen `L6` frameworks to `DBOS`/`Restate`/`Temporal` (or local AGY SDK `save_dir` + `conversation_id`). Never write custom replay logs, distributed lock managers, or retry state machines.

## More Information

- Temporal AI & Temporal LangGraph Plugin: `https://docs.temporal.io/ai`, `https://temporal.io/blog/temporal-langgraph-plugin-durable-execution`
- Restate Durable Orchestration: `https://www.restate.dev/blog/durable-orchestration-for-ai-agents-with-restate-and-openai-sdk`
- DBOS Crash-Proof AI Agents: `https://www.dbos.dev/blog/durable-execution-crashproof-ai-agents`
- LangGraph Persistence & Checkpointers: `https://docs.langchain.com/oss/python/langgraph/persistence`
- PydanticAI v2 & Durable Execution Adapters: `https://pydantic.dev/articles/pydantic-ai-v2`, `https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/`
- Microsoft Agent Framework 1.0 (superseding AutoGen/SK): `https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-at-build-2026-announce/`
- Google ADK & Mastra 1.0: `https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/`, `https://mastra.ai/blog/announcing-mastra-1`
- Antigravity SDK Session Persistence: `https://antigravity.google/docs/sdk/lifecycle.md`, `https://github.com/google-antigravity/antigravity-sdk-python/blob/main/examples/getting_started/persistence.py`
- Repository Architecture & Registry: [Convergence Stack](../convergence-stack.md), [Clean Upstream Installation Registry](../clean-install-registry.md), [Manifest Guide](../manifest-guide.md)
