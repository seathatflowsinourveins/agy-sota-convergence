---
id: ADR-0007
layer: L5
status: accepted
date: 2026-11-26
decision-makers: SOTA Convergence Swarm (Verified 2026-11-26)
consulted: [sota-ecosystem, cross-session, changelogs, best-practices]
informed: [verifier, coordinator]
---

# ADR-0007: L5 — Vertical Tool, Data, and UI Protocol (MCP 2026-07-28 Stateless Core, MCP Apps & Code Mode)

## Context and Problem Statement

Connecting AI agents downward to databases, issue trackers, cloud APIs, memory servers, and interactive rich UIs historically suffered from N×M custom tool integrations, massive prompt-token inflation from upfront tool schemas, brittle stateful SSE connections that failed behind cloud load balancers, and insecure server-to-client model borrowing. With the Linux Foundation AAIF **Model Context Protocol (MCP) `2026-07-28` specification** establishing a stateless core, formalizing the **Tasks** and **MCP Apps (`SEP-1865`)** extensions, and formally deprecating **Roots, Sampling, and Logging (`SEP-2577`)**, how should Layer `L5` govern vertical tool, data, and UI connectivity across AGY and cloud runtimes?

## Decision Drivers

- **Stateless Horizontal Scale:** Cloud MCP servers must run behind standard load balancers without sticky session affinity (`Mcp-Session-Id` retired; self-describing `_meta` and `Mcp-Method`/`Mcp-Name` gateway headers).
- **Prompt-Cache & Token Budget Discipline:** Avoid stuffing hundreds of tool schemas into every turn by defaulting to AGY lazy loading (`call_mcp_tool`), enforcing `<= 3` `"eager": true` tools, and adopting Programmatic Tool Calling / Cloudflare Code Mode for large API catalogs.
- **Sandboxed Interactive UI Without Custom Frontends:** Deliver rich visual workflows via standardized CSP-isolated **MCP Apps (`SEP-1865`, `2026-01-26`)** (`ui://` resources + AGY App `v2.34.0+` `aux_pane`/`global` entrypoints).
- **Zero `SEP-2577` & Legacy Transport Debt:** Prohibit new implementations from adopting `SEP-2577` deprecated primitives (**Roots**, **Sampling**, **Logging**) or legacy HTTP+SSE (`McpSseServer` removed in AGY SDK `v0.1.2`), and standardize OAuth 2.1 on **RFC 8707 / RFC 9207** + **CIMD** (away from DCR).
- **Strict Layer Disjointness (`L5` vs. `L4`):** MCP handles vertical agent-to-tool/UI calls; horizontal peer agent delegation stays exclusively in `L4` (A2A / Orca / AGY messaging).

## Considered Options

1. **Option 1 (Chosen): MCP `2026-07-28` Stateless Core + Formal Extensions (`Tasks` & `MCP Apps SEP-1865`) + Lazy Loading / Code Mode** — with strict bans on `SEP-2577` (`Roots`/`Sampling`/`Logging`), legacy HTTP+SSE, and `> 3` eager tools.
2. **Option 2 (Rejected): Legacy Stateful MCP (`2025-11-25` / HTTP+SSE) Using Server-Initiated Sampling, Roots, and Eager Full-Catalog Loading.**
3. **Option 3 (Rejected): Custom Per-Service Python/REST Glue Wrappers & Bespoke Standalone React Sidecar Dashboards.**

## Decision Outcome

Chosen option: **Option 1 — MCP `2026-07-28` Stateless Core + Formal Extensions (`Tasks` & `MCP Apps SEP-1865`) + Lazy Loading / Code Mode**, because it aligns 1:1 with Linux Foundation AAIF governance, AGY App `v2.34.0+` / CLI / SDK native MCP support, and late-2026 token-efficiency economics (up to 99.9% schema overhead reduction via Code Mode / lazy loading).

### Consequences

- **Good:** Stateless Streamable HTTP servers scale horizontally with zero sticky sessions; cacheable deterministic `tools/list` results preserve upstream LLM prompt caches; W3C `traceparent` propagates end-to-end in `params._meta` (`L10`); long-running tool calls use the formal **MCP Tasks Extension** (`io.modelcontextprotocol/tasks`: `tasks/get`, `tasks/update`, `tasks/cancel`) and stateless **MRTR Elicitation** (`input_required` payloads).
- **Good:** Interactive visualizations render natively inside AGY App (`v2.34.0+`) via `@modelcontextprotocol/ext-apps` (`ui://` CSP-isolated iframes, 10 MiB HTML cap, 1 MiB persisted `CallToolResult`) without maintaining bespoke standalone web apps.
- **Bad:** Antigravity CLI ignores `_meta.ui.visibility` hiding and does not render interactive MCP App iframes, so MCP App tools must return clean text/JSON fallbacks for CLI callers; migrating legacy `2025-11-25` servers off `Sampling`/`Roots`/`Logging` and `tasks/result` requires engineering effort ahead of the **2027-07-28** 12-month deprecation window.
- **Neutral:** Trivial local project CLI utilities remain faster and cleaner as `SKILL.md` `scripts/` (`L7`) rather than full MCP servers.

### Confirmation

Run the following executable fitness gates from the repository root:

```bash
# 1. Lint workspace mcp_config.json (when present): <= 3 eager, zero secrets, zero deprecated SSE
python3 -c '
import json, pathlib, re
p = pathlib.Path(".agents/mcp_config.json")
if p.exists():
    raw = p.read_text(encoding="utf-8")
    assert not re.search(r"(Bearer\s+[A-Za-z0-9._-]{16,}|sk-[A-Za-z0-9]{16,}|AIza[0-9A-Za-z_-]{20,})", raw), f"Secret token in {p}"
    cfg = json.loads(raw)
    eager = sum(1 for srv in (cfg.get("mcpServers") or {}).values() if srv.get("eager") is True)
    assert all(srv.get("transport") != "sse" for srv in (cfg.get("mcpServers") or {}).values()), "Deprecated SSE transport"
    assert eager <= 3, f"Eager MCP count ({eager}) exceeds anti-bloat cap of 3"
print("L5_MCP_CONFIG_OK")
'

# 2. Enforce zero SEP-2577 deprecated Roots/Sampling/Logging or legacy McpSseServer adoption in code
! grep -rnE "(McpSseServer|sampling/createMessage|roots/list|logging/setLevel|tasks/result)" scripts/ .agents/ 2>/dev/null

# 3. Verify manifest seal & L5 MCP/SEP-2577 invariants
python3 scripts/verify_manifest.py --verify
```

## Pros and Cons of the Options

### Option 1: MCP `2026-07-28` Stateless Core + Extensions + Lazy Loading / Code Mode
- **Pros:** Industry-standard vertical connectivity (>1B cumulative TS/Python SDK downloads); stateless cloud load balancing; RFC 8707/9207 + CIMD OAuth hardening; CSP-isolated MCP Apps UI; massive prompt-token savings via lazy loading (`call_mcp_tool`) and Cloudflare Code Mode / Anthropic PTC; passes the 5-Question Zero-Self-Invention test cleanly.
- **Cons:** Requires dual text+UI tool responses when targeting both AGY App and AGY CLI; requires refactoring pre-2026 stateful servers.

### Option 2: Legacy Stateful MCP (`2025-11-25`) + `SEP-2577` Primitives + Eager Loading
- **Pros:** Short-term backward compatibility with 2025 tutorials.
- **Cons:** **Rejected** — directly violates `SEP-2577` (*"New implementations shouldn't adopt them"* ahead of the `2027-07-28` sunset window), fails behind stateless cloud gateways, breaks AGY SDK `v0.1.2+` (which removed `McpSseServer`), and inflates per-turn context windows with unused schemas.

### Option 3: Custom Per-Service REST Wrappers & Bespoke Sidecar Webapps
- **Pros:** Full control over custom wire formats and CSS.
- **Cons:** **Rejected (Fails Zero-Self-Invention Gate)** — forces N×M glue maintenance across AGY, Claude Code, Codex, and cloud agents, bypasses unified AGY `mcp(server/tool)` permission policies (`L8`) and OAuth account management, and duplicates CSP-sandboxed `MCP Apps` (`SEP-1865`).

## Clean Upstream Installation & Adapter Boundary

| Scope | Canonical Upstream | Registry / Channel | Exact Verified Version (`2026-11-26`) | Clean Pinned Install Command | Post-Install Smoke / Verify Command |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **MCP Python SDK** | Official MCP Python SDK (`mcp`) | PyPI | `2.3.0` (`2026-10-02`) | `uv add "mcp==2.3.0"` | `uv run python -c "import mcp; print(mcp.__file__)"` |
| **MCP TypeScript SDK** | Official MCP TypeScript SDK (`@modelcontextprotocol/sdk`) | npm | `1.32.2` | `npm install --save-exact @modelcontextprotocol/sdk@1.32.2` | `node -e "console.log(require.resolve('@modelcontextprotocol/sdk'))"` |
| **MCP Apps (`SEP-1865`)** | Official MCP Apps Extension (`@modelcontextprotocol/ext-apps`) | npm | `2.0.4` | `npm install --save-exact @modelcontextprotocol/ext-apps@2.0.4` | `node -e "console.log(require.resolve('@modelcontextprotocol/ext-apps'))"` |
| **AGY MCP Client & Apps Host** | Antigravity MCP Client + MCP Apps Host (`aux_pane`/`global`) | Bundled in AGY App / CLI / SDK | App `2.35.2` / CLI `1.5.18` / SDK `0.1.24` | Bundled; declare servers in `.agents/mcp_config.json` or plugin `mcp_config.json` with OAuth PKCE / CIMD / ADC | `agy plugin validate --strict <plugin-dir>` |

**Thin-Adapter Boundary:** Custom code in `L5` is restricted to thin declarative `mcp_config.json` bindings (using `enabledTools` allowlists, lazy default, and `${PLUGIN_ROOT}`/`${PLUGIN_DATA}` variables) and domain-specific MCP tool/resource handlers built directly on `mcp==2.3.0`, `@modelcontextprotocol/sdk@1.32.2`, and `@modelcontextprotocol/ext-apps@2.0.4`. Zero custom JSON-RPC transports, zero hardcoded secrets, zero `SEP-2577` primitives.

## More Information

- MCP `2026-07-28` Specification & Release Notes: `https://modelcontextprotocol.io/specification/2026-07-28`, `https://blog.modelcontextprotocol.io/posts/2026-07-28/`
- MCP Apps Extension (`SEP-1865`): `https://modelcontextprotocol.io/extensions/apps/overview`
- Antigravity MCP & MCP Apps Docs: `https://antigravity.google/docs/mcp.md`, `https://antigravity.google/docs/mcp-apps.md`
- Anthropic Code Execution with MCP & Programmatic Tool Calling: `https://www.anthropic.com/research/code-execution-with-mcp`, `https://www.anthropic.com/research/advanced-tool-use`
- Cloudflare Code Mode for MCP: `https://blog.cloudflare.com/code-mode-mcp`
- Repository Architecture & Registry: [Convergence Stack](../convergence-stack.md), [Clean Upstream Installation Registry](../clean-install-registry.md), [Manifest Guide](../manifest-guide.md)
