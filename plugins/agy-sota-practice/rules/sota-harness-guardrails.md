---
trigger: model_decision
description: Apply when designing agent harnesses, orchestration workflows, MCP integrations, security hooks, or cross-session handoffs in AGY 2.0 repositories.
---

# SOTA Harness & Native-First Guardrails

1. **Native-First, Zero Wrapper Daemons:** Use native AGY 2.0 primitives (`/goal`, `/swarm` with zero-token `swarm_wait`, `/teamwork`, `/boost`, `/run-workflow`, `/plan`, `/grill-me`, `ConversationService`, Sidecars, `agy acp`) and `Orca` typed mail for heterogeneous worktrees. Never install stateful meta-harness wrappers (`oh-my-claudecode`, `oh-my-codex`, `oh-my-openagent`, `oh-my-antigravity`, `ruflo`, `claude-flow`, `hcom`, `BMAD-METHOD`).
2. **Fail-Closed Policy & Isolation:** Enforce `Deny > Ask > Allow` with resolved absolute paths (never unexpanded `~/` in AGY deny rules). Security `PreToolUse` hooks must catch every error and exit `0` with `{"decision":"deny"}`. Bind local bridges strictly to loopback (`127.0.0.1`), never `0.0.0.0`.
3. **Context & Sunset Discipline:** Keep `AGENTS.md <= 45` lines and `<= 1,600` chars (`0` HTML comments), rule files `<= 24,000 B`, skill descriptions `<= 1,024` chars, and eager MCP tools `<= 3`. Ban retiring `2026-11-30` models, MCP `SEP-2577` (Roots/Sampling/Logging), and unverified claims.
