---
id: ADR-0006
layer: L4
status: accepted
date: 2026-11-26
decision-makers: SOTA Convergence Swarm (Verified 2026-11-26)
consulted: [sota-ecosystem, cross-session, changelogs, best-practices]
informed: [verifier, coordinator]
---

# ADR-0006: L4 — Cross-Session, Multi-Host, and Federated Agent Messaging

## Context and Problem Statement

Agent work routinely crosses session boundaries, machine boundaries, vendor harnesses, and organizational perimeters: scheduled morning triage jobs must hand verified findings to interactive developer sessions; laptop sleep must not abort remote Linux engineering sessions; heterogeneous teams mix AGY, Claude Code, and Codex CLI across Git worktrees; and external enterprise services must delegate long-running tasks across organizational walls. Critically, AGY's local `ConversationService` (`v2.35.0`) manages session lifecycle and spawning (`Create`/`List`/`Get`/`Update`/`Delete`) but **intentionally omits a `SendMessage` RPC** for follow-up turn injection. How should Layer `L4` unify cross-session, cross-host, and cross-org messaging cleanly with strict idempotency and trust isolation?

## Decision Drivers

- **Exact Channel Routing Without Conflation:** Map every cross-session boundary to its exact native transport rather than forcing one brittle bridge onto every scope.
- **Messages Are Input, Never Authority:** Cross-session payloads, search snippets, and peer mail must never self-approve tool execution, mutate `hooks.json`/`mcp_config.json`, or bypass `L8`.
- **Reactive Wakeups & Idempotent Delivery:** Eliminate polling loops that waste tokens or consume inbox mail; enforce idempotency watermarks, `--retry-launch <operationId>`, and SHA-256 verified `handoff_packet.json` contracts.
- **Permission-Clean Sidecar State Boundaries:** Respect the exact runtime boundary between sidecar process state (`$ANTIGRAVITY_EXECUTABLE_DATA_DIR` for `command` sidecars) and unattended spawned agent workspaces (`${repo_dir}/.agents/scratch/` for `builtin: "schedule"` automations).
- **Open Cross-Org Interoperability:** Standardize cross-vendor / cross-org agent delegation on Linux Foundation AAIF **A2A v1.0** (`contextId`, 9-state lifecycle, SSE/webhooks).

## Considered Options

1. **Option 1 (Chosen): Scoped Upstream Cross-Session Transport Matrix** — native AGY (`ConversationService` for lifecycle/spawning, Sidecars `agentapi new-conversation` & `agentapi send-message` for daemons/cron, Lifecycle Hooks `SessionStart`/`PreInvocation`/`Stop` for hash-deduped hydration, Remote Control / Connect over SSH / Remote Agents / CLI `stream-json` for remote & CI continuity) + **Orca CLI/Orchestration** for heterogeneous local/paired-server multi-vendor harnesses + **Google A2A v1.0** (`a2a-sdk` / `@a2a-js/sdk`) for cross-org federated delegation, all passing typed `handoff_packet.json` paths (`L7`).
2. **Option 2 (Rejected): Terminal PTY Scraping & Raw `terminal send` Text Injection Across Agent Panes.**
3. **Option 3 (Rejected): Custom Local/Cloud HTTP Relay Broker Duplicating `agentapi`, Orca Mail, and A2A v1.0.**

## Decision Outcome

Chosen option: **Option 1 — Scoped Upstream Cross-Session Transport Matrix**, enforcing strict separation across four cross-session scopes:

1. **Local AGY Lifecycle & Tag/Group Management:** `product.v1.ConversationService` Connect HTTP+JSON (`POST http://$ANTIGRAVITY_LS_ADDRESS/product.v1.ConversationService/<Method>` with `Connect-Protocol-Version: 1` and `x-antigravity-csrf-token: $ANTIGRAVITY_CSRF_TOKEN`; explicit `projectId: "$ANTIGRAVITY_PROJECT_ID"`; rerun outside sandbox if loopback returns HTTP `403` / `"Port ... not allowed for HTTP"`). Never attempt follow-up turn injection via `ConversationService`.
2. **Local AGY Unattended Scheduling & Follow-Up Injection:**
   - Recurring unattended runs (`.agents/templates/sidecar.scheduled.json`: `"builtin": "schedule"`, `CRON_TZ=<IANA zone>`, `restart_policy: "always"`, `agentapi new-conversation -- "<prompt>"`) persist watermarks inside `${repo_dir}/.agents/scratch/` (covered by `workspace_uris`) and pre-validate minimal `access_grants` (zero wildcards).
   - Persistent event-driven daemons (`.agents/templates/sidecar.relay.json`: `"command"` sidecars) persist deduplication cursors in `$ANTIGRAVITY_EXECUTABLE_DATA_DIR` (`~/.gemini/antigravity/sidecar_data/<sidecarId>/data/`) and inject follow-ups via `agentapi send-message <conversation_id> <prompt>`.
   - Session hydration uses `.agents/hooks.json` + `.agents/scripts/cross_session_hooks.py` (`SessionStart` + SHA-256 hash-deduplicated `PreInvocation` + loop-safe `Stop` guarding `continuationActive` and `executionNum`).
3. **Cross-Machine & Headless Continuity:** AGY **Connect over SSH** (`v2.33.0+`, `~/.antigravity-hub-server/`, `ForwardAgent=no`, separate `$HOME` per host), **Remote Control** (`/remote-control` or `agy remote-control start` OS daemon), **Remote Agents** (`agy --remote-agent`, respecting partitioned cloud history), and headless CLI (`agy -p ... --conversation <id>` / `-r <id>` or bidirectional `--input-format stream-json --output-format stream-json`).
4. **Heterogeneous Multi-Vendor & Cross-Org Federation:** **Orca CLI & Orchestration** (`orca worktree create --no-parent --agent ...` for fire-and-forget handoffs; `orca orchestration worker-start` / `send` / `reply` with `--retry-launch <operationId>`, `input_accepted` vs `turn_started` proofs, and `unverifiable` liveness discipline) across Codex/Claude/AGY/paired servers; **Google A2A Protocol v1.0** (`AgentCard`, `contextId` grouping, 9 states = 8 operational states `SUBMITTED`/`WORKING`/`INPUT_REQUIRED`/`AUTH_REQUIRED`/`COMPLETED`/`FAILED`/`CANCELED`/`REJECTED` + `TASK_STATE_UNSPECIFIED`, SSE `SendStreamingMessage`, webhook `TaskPushNotificationConfig`) across organizational or framework boundaries.

### Consequences

- **Good:** Eliminates duplicate dispatch, prompt corruption, and polling token burn; preserves strict privilege separation ("messages are input, never authority"); handles follow-up turn delivery cleanly despite `ConversationService`'s deliberate omission of `SendMessage`.
- **Good:** Typed `.agents/schemas/handoff_packet.schema.json` (15 required fields with `payload_sha256`, `conversation://` link, git commits, and timestamped default-FAIL `verified_evidence`) cuts cross-session context transfer from tens of thousands of transcript tokens to a verified compact pointer.
- **Bad:** Operators must learn distinct local channels (`ConversationService` vs. sidecar `agentapi` vs. CLI `stream-json` vs. Orca mail) rather than one monolithic IPC socket; AGY sidecars remain Antigravity App-only.
- **Neutral:** Cross-session links (`conversation://<uuid>`) and App `@conversation:` mentions rely on local retention (unlimited by default as of App `v2.35.0` / CLI `v1.5.15`).

### Confirmation

Run the following executable fitness gates from the repository root:

```bash
# 1. Execute full unit test suite validating hooks.json, hash dedup, Stop guards, handoff schema & sidecar templates
python3 -m unittest tests/test_hooks_and_handoff.py -v

# 2. Ensure no script uses raw terminal send or CSRF token echoing
! grep -rnE "(terminal send|echo.*ANTIGRAVITY_CSRF_TOKEN)" .agents/ scripts/

# 3. Verify Orca CLI version where installed locally
orca --version

# 4. Verify manifest seal & cross-session routing invariants
python3 scripts/verify_manifest.py --verify
```

## Pros and Cons of the Options

### Option 1: Scoped Upstream Cross-Session Transport Matrix
- **Pros:** Respects native security, idempotency, and liveness invariants at every perimeter (local App/CLI, SSH/Remote Control, Orca multi-vendor, A2A cross-org); passes the 5-Question Zero-Self-Invention test (declarative `.agents/hooks.json`, `.agents/templates/sidecar.*.json`, `.agents/schemas/handoff_packet.schema.json`, and thin upstream SDK clients only).
- **Cons:** Requires documenting channel selection clearly (addressed in [Convergence Stack](../convergence-stack.md)).

### Option 2: Terminal PTY Scraping & Raw `terminal send` Injection
- **Pros:** Works superficially on arbitrary CLI TUIs without protocol integration.
- **Cons:** **Rejected** — corrupts interactive prompts and permission menus, loses structured delivery receipts (`input_accepted` vs. `turn_started`), fails entirely on chat-surface agents with no PTY, and violates Orca's and AGY's explicit safety boundaries.

### Option 3: Custom HTTP Relay Broker Duplicating `agentapi`, Orca, and A2A
- **Pros:** Single bespoke API surface.
- **Cons:** **Rejected (Fails Zero-Self-Invention Gate)** — re-invents solved CSRF/OAuth auth, push notifications, durable replay receipts, and multi-org discovery already standardized by `agentapi`, Orca, and LF AAIF A2A v1.0.

## Clean Upstream Installation & Adapter Boundary

| Scope | Canonical Upstream | Registry / Channel | Exact Verified Version (`2026-11-26`) | Clean Pinned Install Command | Post-Install Smoke / Verify Command |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Local AGY Messaging** | `ConversationService`, Sidecars (`agentapi`), Hooks, Remote Control, SSH, CLI `stream-json` | Bundled in AGY App / `agy` CLI | App `2.35.2` / CLI `1.5.18` *(docs `1.5.16`)* | Bundled in Antigravity App & `agy` (enable sidecars via App **Automations** dashboard; never hand-edit `config.json`) | `agy --version && agy remote-control --help` |
| **Heterogeneous Local / Paired Host** | Orca CLI & Orchestration (`orca`) | GitHub Releases (`stablyai/orca`) | `v1.4.278` *(GitHub; local host `1.4.277`)* | Install official Orca app & CLI binary (resolve via `ORCA_CLI_COMMAND` / `orca`) | `orca --version && orca skills get orchestration \| head -n 5` |
| **Cross-Org Federation (Python)** | Official A2A Python SDK (`a2a-sdk`) | PyPI | `1.3.1` (`2026-11-17`) | `uv add "a2a-sdk==1.3.1"` | `uv run python -c "import a2a; print(a2a.__file__)"` |
| **Cross-Org Federation (TypeScript)** | Official A2A JS/TS SDK (`@a2a-js/sdk`) | npm | `1.3.0` | `npm install --save-exact @a2a-js/sdk@1.3.0` | `node -e "console.log(require.resolve('@a2a-js/sdk'))"` |

**Thin-Adapter Boundary:** Project repositories supply only `.agents/schemas/handoff_packet.schema.json`, `.agents/hooks.json` + `.agents/scripts/cross_session_hooks.py`, `.agents/templates/sidecar.*.json`, and thin A2A `AgentCard`/client handlers wrapping `a2a-sdk` or `@a2a-js/sdk`. Zero custom message brokers or PTY scrapers.

## More Information

- Antigravity Sidecars (`agentapi`) & Automations: `https://antigravity.google/docs/sidecars.md`, `https://antigravity.google/docs/commands/automation.md`
- Antigravity Hooks, Remote Control, Remote Agents, SSH & CLI Headless: `https://antigravity.google/docs/hooks.md`, `https://antigravity.google/docs/remote-control.md`, `https://antigravity.google/docs/remote-agents.md`, `https://antigravity.google/docs/ssh.md`, `https://antigravity.google/docs/cli/headless.md`
- Agent2Agent (A2A) Protocol v1.0 & SDKs: `https://github.com/a2aproject/A2A`, `https://pypi.org/project/a2a-sdk/1.3.1/`, `https://github.com/a2aproject/a2a-js`
- Repository Architecture & Registry: [Convergence Stack](../convergence-stack.md), [Clean Upstream Installation Registry](../clean-install-registry.md), [Manifest Guide](../manifest-guide.md)
