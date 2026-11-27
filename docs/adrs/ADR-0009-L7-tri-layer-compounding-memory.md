---
id: ADR-0009
layer: L7
status: accepted
date: 2026-11-26
decision-makers: SOTA Convergence Swarm (Verified 2026-11-26)
consulted: [sota-ecosystem, cross-session, changelogs, best-practices]
informed: [verifier, coordinator]
---

# ADR-0009: L7 Tri-Layer Compounding Memory (Procedural, Episodic & Bi-Temporal Semantic MCP)

## Context and Problem Statement

Autonomous coding agents operating across sessions, hosts, and multi-day projects face three distinct memory requirements that single-mechanism solutions consistently fail to satisfy: (1) **procedural memory** (durable repo invariants and reusable workflows), (2) **episodic memory** (auditable session traces, handoff packets, and git-versioned working memory), and (3) **semantic, temporal & structural memory** (evolving enterprise facts where truth changes over time, plus code call-graphs and documentation search). Empirical 2025–2026 studies demonstrate that naive approaches actively harm agents: ETH Zurich ([arXiv:2602.11988](https://arxiv.org/abs/2602.11988), Feb 12, 2026) showed boilerplate `AGENTS.md` files inflate inference cost by **>20%** while failing to improve task success; Stanford/SambaNova/Berkeley's ACE ([arXiv:2510.04618](https://arxiv.org/abs/2510.04618), Oct 6, 2025) proved monolithic LLM rewrites cause **brevity bias** and **context collapse**; and naive vector RAG retrieves contradictory superseded facts simultaneously. How should Layer `L7` architect compounding memory cleanly without bloat, drift, or custom memory-engine self-invention?

## Decision Drivers

* Maintain strict separation between **procedural** (rules/skills), **episodic** (transcripts/handoffs/MemFS), and **semantic/temporal/structural** (bi-temporal KG, entity facts, AST/BM25+kNN search) memory planes.
* Enforce hard anti-bloat ratchets (`AGENTS.md <= 45` lines / `1,600` chars, `rule_file_max_bytes: 24000`, `rules_aggregate_budget_tokens: 20000`, `delete_to_add_policy: true`) and **non-destructive bi-temporal invalidation** (`t_valid` / `t_invalid`) so outdated facts never poison future runs.
* Prevent context collapse via **itemized structured deltas** and Git-backed diffs rather than whole-file LLM summarization rewrites.
* Mount all external memory backends exclusively over standard **MCP `2026-07-28`** interfaces (strictly excluding deprecated `SEP-2577` Roots/Sampling/Logging) so memory stays portable across AGY App, CLI, IDE, and cloud frameworks.
* Satisfy the **5-Question Zero-Self-Invention Gate** (`ADR-0001`) by adopting pinned upstream memory engines rather than building custom vector/graph databases.

## Considered Options

* **Option 1 (Chosen): Strictly Partitioned Tri-Layer Compounding Memory — Procedural (`AGENTS.md` + `SKILL.md` + AGY `/learn`), Episodic (AGY JSONL Transcripts + Typed Handoff Packets + Letta Sleep-Time/MemFS), and Semantic/Temporal/Structural via MCP (`graphiti-core`, `mem0ai`, `xerj`, `codebase-memory-mcp`).**
* **Option 2: Monolithic Always-On Context Files (`AGENTS.md` / `CLAUDE.md` Dump) Rewritten Periodically by an LLM.**
* **Option 3: Unstructured Append-Only Vector RAG Database (Flat Chroma/FAISS Dump without Temporal Invalidation).**
* **Option 4: Custom In-House SQLite + Embedding + Graph Memory Server.**

## Decision Outcome

Chosen option: **"Option 1: Strictly Partitioned Tri-Layer Compounding Memory"**, because each memory modality has fundamentally different access, mutation, and decay semantics:
1. **Procedural Plane (Native AGY + AAIF Standards):** Keep `AGENTS.md` strictly minimal (`<= 45` lines, `<= 1,600` chars; non-discoverable invariants only), package reusable procedures as progressive-disclosure `SKILL.md` directories (`agentskills.io`), capture session lessons via AGY `/learn` (human-reviewed `learning_proposal.md` -> `L9` eval gate), and escalate repeated violations into `L8` deterministic hooks/linters (deleting superseded prose). Eliminate hard-copied multi-root skill drift by keeping `~/.gemini/config/skills/` as one canonical root symlinked to `~/.agents/skills/` and `~/.gemini/skills/`.
2. **Episodic Plane (Trace Continuity & Offline Consolidation):** Retain immutable AGY `transcript.jsonl` / `transcript_full.jsonl` logs and typed `handoff_packet` artifacts (`L4`) for cross-session continuity; for long-lived autonomous background workers requiring self-editing memory, adopt **Letta (`0.34.12`)** Git-backed **MemFS / Context Repositories** with asynchronous **Sleep-Time Compute** consolidation ([arXiv:2504.13171](https://arxiv.org/abs/2504.13171), [Context Repos](https://www.letta.com/blog/context-repositories/)).
3. **Semantic, Temporal & Structural Plane (MCP-Mounted Upstream Engines):** Adopt **`graphiti-core` (`0.32.1`)** for bi-temporal knowledge graphs (`t_valid`/`t_invalid` fact succession; [arXiv:2501.13956](https://arxiv.org/html/2501.13956v1)), **`mem0ai` (`2.2.1`)** for lightweight per-user preference/entity extraction ([arXiv:2504.19413](https://arxiv.org/abs/2504.19413)), **`codebase-memory-mcp` (`0.12.1`)** for tree-sitter AST/call-graph + `manage_adr` queries, and **`xerj` (`v1.0.0-rc.105`)** for local hybrid BM25+kNN documentation/corpus search—all queried on demand via MCP.

### Consequences

* Good, because `AGENTS.md` and always-on rules stay compact (`<= 45L / 1,600c` charter; `<= 24 KB` per rule file; `<= 20,000` aggregate tokens), avoiding ETH Zurich's `>20%` context-bloat tax while preserving high-lift progressive-disclosure skills (`+16.6 pp` in SkillsBench).
* Good, because bi-temporal edge invalidation (`graphiti-core`) and Git-backed diffs (`MemFS`) preserve full audit trails ("what was true on date $T$?") and allow instant rollback of corrupt memory edits.
* Good, because offline sleep-time consolidation and ACE-style itemized deltas prevent both latency spikes on live turns and catastrophic context collapse.
* Bad, because operating optional cloud/graph backends (`graphiti-core` requiring a graph store such as Neo4j/FalkorDB, or `letta` server) introduces external storage dependencies when enabled beyond local AGY + `codebase-memory-mcp` + `xerj`.
* Neutral, because local single-developer workflows only need AGY native procedural/episodic memory plus `codebase-memory-mcp` and `xerj`, activating `graphiti-core`/`letta`/`mem0ai` progressively when multi-entity temporal timelines or autonomous background workers are required.

### Confirmation

Verify repository procedural anti-bloat budgets (`AGENTS.md` + `.agents/rules/*.md`), read-only host hygiene, and clean upstream memory tool availability from the repository root:

```bash
# 1. Verify AGENTS.md & .agents/rules budgets via Gate [15] and standalone host hygiene audit
python3 scripts/verify_manifest.py --verify && python3 scripts/audit_ecosystem_hygiene.py --json

# 2. Verify pinned local structural & hybrid-search MCP binaries respond cleanly
codebase-memory-mcp --version && xerj --version

# 3. Verify optional Python temporal/semantic memory libraries import cleanly in isolated uv env
uv run python -c 'import graphiti_core, mem0; print("OK: graphiti-core & mem0ai importable")'
```

## Pros and Cons of the Options

### Option 1: Tri-Layer Compounding Memory (Native Procedural/Episodic + MCP Temporal/Structural Upstreams)

* Good, because each layer uses the exact right data structure (Git-checked Markdown for rules/skills, append-only JSONL + MemFS for episodes, bi-temporal graphs for evolving facts, tree-sitter/BM25+kNN for code/docs).
* Good, because it passes all 5 questions of the **Zero-Self-Invention Gate** (`ADR-0001`): adopts pinned upstream `graphiti-core==0.32.1`, `letta==0.34.12`, `mem0ai==2.2.1`, `codebase-memory-mcp==0.12.1`, and `xerj` `v1.0.0-rc.105` via declarative MCP configs with zero custom storage engines.
* Bad, because teams must maintain discipline on the boundary between `AGENTS.md` (invariants) vs. `SKILL.md` (procedures) vs. temporal KG (facts).

### Option 2: Monolithic Always-On Context Files Rewritten by LLMs

* Good, because it requires zero external services.
* Bad, because ETH Zurich ([arXiv:2602.11988](https://arxiv.org/abs/2602.11988)) empirically proved bloated repo-level context files inflate cost `>20%` and degrade/stall task success, while ACE ([arXiv:2510.04618](https://arxiv.org/abs/2510.04618)) showed iterative monolithic LLM rewrites suffer brevity bias and sudden context collapse.

### Option 3: Flat Append-Only Vector RAG Dump

* Good, because basic cosine similarity over chunked chat transcripts is trivial to prototype.
* Bad, because flat vector stores lack temporal invalidation (`t_invalid`)—retrieving obsolete API patterns or retired Nov-30 model directives alongside current ones with equal cosine similarity and poisoning agent runs.

### Option 4: Custom In-House Memory Server

* Good, because schemas can be tailored arbitrarily.
* Bad, because it fails **Q1 (Upstream Existence)**, **Q2 (LOC Ratchet)**, and **Q4 (Clean Install Without Fork)** of `ADR-0001`, duplicating years of upstream bi-temporal graph (`graphiti-core`), sleep-time MemFS (`letta`), and hybrid Rust search (`xerj`) engineering.

## Clean Upstream Installation & Adapter Boundary

All `L7` memory engines are installed from exact pinned official releases (zero unpinned version specs, zero vendored forks, zero custom vector/graph engines):

| Memory Modality & Upstream | Exact Pinned Version (`2026-11-26`) | Official Clean Install Command | Post-Install Verify Command | Thin-Adapter Boundary |
| :--- | :--- | :--- | :--- | :--- |
| **Procedural / Episodic Base** *(AGY native `/learn`, `AGENTS.md`, `SKILL.md`, transcripts)* | Bundled in AGY App `2.35.2` / CLI `1.5.18` | Native (zero separate install) | `agy --version` | Repo-checked `AGENTS.md` (`<= 45L / 1,600c`), `.agents/skills/*/SKILL.md`, and `L4` `handoff_packet` JSON. |
| **Bi-Temporal Knowledge Graph** *(`graphiti-core`)* | `0.32.1` (PyPI, `2026-11-24`) | `uv add "graphiti-core==0.32.1"` | `uv run python -c "import graphiti_core; print(graphiti_core.__file__)"` | Declarative MCP server config + graph-store env URI; zero custom temporal resolution engine. |
| **Self-Editing / Sleep-Time MemFS** *(`letta` / `letta-client`)* | `letta==0.34.12` (`2026-10-12`); `letta-client==1.12.1` (`2026-06-02`) | `uv tool install "letta==0.34.12"` / `uv add "letta-client==1.12.1"` | `letta --version` / `uv run python -c "import letta_client; print('ok')"` | Declarative `/memfs` & `/sleeptime` config; zero custom context-paging OS. |
| **Entity / User Preference Memory** *(`mem0ai` / OpenMemory)* | `2.2.1` (PyPI, `2026-09-25`) | `uv add "mem0ai==2.2.1"` | `uv run python -c "import mem0; print(mem0.__version__)"` | Mounted over MCP (`OpenMemory`); zero custom fact-extraction pipeline. |
| **AST / Call-Graph & ADR Memory** *(`codebase-memory-mcp`)* | `0.12.1` (PyPI / GitHub, `2026-10-16`) | `uv tool install "codebase-memory-mcp==0.12.1"` | `codebase-memory-mcp --version` | Mounted in `mcp_config.json`; exposes `search_graph`, `trace_call_path`, `manage_adr`. |
| **Hybrid BM25+kNN Docs/Corpus Search** *(`xerj`)* | `v1.0.0-rc.105` (GitHub release) | `nix run github:xerj-org/xerj/v1.0.0-rc.105 -- --version` *(or pinned `v1.0.0-rc.105` binary from GitHub Releases; interactive: `curl -fsSL https://xerj.org/get \| sh`)* | `xerj --version` | Mounted via MCP + `xerj autoindex`; zero custom search index code. |

## More Information

* [Zep / Graphiti: A Temporal Knowledge Graph Architecture (arXiv:2501.13956)](https://arxiv.org/html/2501.13956v1) & [Graphiti Docs](https://help.getzep.com/graphiti/graphiti/overview)
* [Letta Sleep-Time Compute (arXiv:2504.13171)](https://arxiv.org/abs/2504.13171), [Context Repositories / MemFS (Feb 12, 2026)](https://www.letta.com/blog/context-repositories/) & [Memory & Dreaming Docs](https://docs.letta.com/configuration/memory)
* [Mem0 Scalable Long-Term Memory (arXiv:2504.19413)](https://arxiv.org/abs/2504.19413) & [PyPI `mem0ai`](https://pypi.org/project/mem0ai/)
* [ACE: Agentic Context Engineering (arXiv:2510.04618, Oct 6, 2025)](https://arxiv.org/abs/2510.04618)
* [ETH Zurich: Evaluating AGENTS.md (arXiv:2602.11988, Feb 12, 2026)](https://arxiv.org/abs/2602.11988)
* [Google Antigravity `/learn` Docs](https://antigravity.google/docs/commands/learn) | [codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) | [XERJ](https://github.com/xerj-org/xerj/releases/tag/v1.0.0-rc.105)
* Repository Guides: [`docs/compounding-flywheel.md`](../compounding-flywheel.md), [`docs/convergence-stack.md`](../convergence-stack.md), [`docs/clean-install-registry.md`](../clean-install-registry.md)
