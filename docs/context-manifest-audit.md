# SOTA Context & Manifest Audit Standard

This guide codifies the quantitative context-budget ratchets, prompt-cache stability rules, skill quality gates, and automated zero-secret scorecard enforced across this repository and compatible Google Antigravity (AGY) workstations.

---

## 1. Context-Budget & Prompt-Cache Ratchets

Grounded in ETH Zurich's `AGENTS.md` empirical study (`arXiv:2602.11988`), SkillsBench (`arXiv:2602.12670`), ACE (`arXiv:2510.04618`), and AGY runtime limits:

| Context Surface | Hard Ratchet / Target | Cache & Token Rationale | Enforcement Gate |
| :--- | :--- | :--- | :--- |
| **Global & Repo Charters (`GEMINI.md` / `AGENTS.md`)** | `<= 45` lines AND `<= 1,600` chars; **`0` HTML comment waste** (`<!-- ... -->`) | Always-on tokens pay on every turn; static, comment-free rules keep combined rules `< 5%` of AGY's `20,000`-token ceiling and preserve Gemini 4 implicit KV-cache prefixes (`>= 4,096` tokens). | `scripts/verify_manifest.py` Gate `[15]` + `scripts/audit_ecosystem_hygiene.py` |
| **Conditional Rules (`.agents/rules/*.md`)** | `<= 24,000` bytes/file; valid snake_case `trigger:` (`glob`, `model_decision`, `manual`, `always_on`) | AGY truncates rule bodies above `24,000` bytes; glob scoping prevents irrelevant rules from entering unrelated turns. | `scripts/verify_manifest.py` Gate `[15]` |
| **Skill Descriptions (`.agents/skills/*/SKILL.md`)** | `<= 1,024` chars hard cap; **`< 950` chars headroom** (`<= 200` chars optimal for Tier-1 Discoverability); `"Use when ..."` in first `57` chars | Only `name` + `description` load upfront; tight, third-person descriptions with explicit negative triggers prevent trigger collisions and context bloat. | `scripts/verify_manifest.py` Gate `[15]` + `skillevaluator tier1 --no-llm` |
| **Skill Body & Companion Links** | Body `< 5,000` est. tokens (`< 24,000` bytes); `0` broken local links; `Grade A >= 90/100`, `0` HIGH/CRIT | Dead companion links fail `skillevaluator` Code Integrity; oversized bodies trigger silent truncation at `24,000` bytes. | `skillevaluator tier1 --no-llm` + `agy plugin validate --strict` |
| **MCP Lazy Schema Footprint** | `<= 3` eager tools/server; switch servers exceeding **`20–30` tools** to Code Mode / Programmatic Tool Calling (PTC) or workspace scoping | AGY's lazy schema cache avoids injecting tens of thousands of JSON schema tokens upfront (typically `>95%` savings), while Code Mode caps large catalogs in `<1,000` tokens. | `scripts/audit_ecosystem_hygiene.py` `mcp_cached_servers` scorecard |
| **Delete-to-Add Prose Escalation** | Delete redundant prose whenever a rule graduates to a `PreToolUse` hook, `ast-grep` rule, or CI test | Prevents monotonic charter drift and keeps steady-state context density constant as reliability compounds. | `manifest/compounding_manifest.v2.json` (`delete_to_add_policy: true`) |

---

## 2. Automated Zero-Secret Scorecard (`scripts/audit_ecosystem_hygiene.py`)

`scripts/audit_ecosystem_hygiene.py` (`schema_version: "1.1.0"`) audits local AGY customization surfaces read-only while strictly refusing to open `.env*`, `config.json`, `mcp_config.json`, `settings.json`, `mcp_oauth_tokens.json`, `auth.json`, or `~/Documents/upstream/` (`security_boundary.secrets_accessed == false`).

### Usage

```bash
# Structured JSON scorecard (strict exits 1 on any HIGH finding)
python3 scripts/audit_ecosystem_hygiene.py --json --strict

# Human-readable terminal summary
python3 scripts/audit_ecosystem_hygiene.py

# Deterministic CI test against an isolated temporary home directory
python3 scripts/audit_ecosystem_hygiene.py --json --home /tmp/isolated-home
```

### `context_manifest_scorecard` Fields

| Field | Meaning |
| :--- | :--- |
| `global_charter` | `{lines, chars, est_tokens, html_comment_chars, within_45L_1600c}` for active always-on global charter files. |
| `global_skills` | `{count, total_desc_chars, est_desc_tokens, near_cap_over_950c}` across deduplicated canonical user skills. |
| `plugins_count` / `sidecars_count` | Installed user plugins and scheduled/command sidecars under `~/.gemini/config/`. |
| `mcp_cached_servers` | Per-server count of deferred `.json` tool schemas under `~/.gemini/antigravity/mcp/` (zero secrets read). |
| `mcp_total_cached_tools` | Total deferred MCP tool schemas across all cached servers. |
| `mcp_lazy_index_est_tokens` | Estimated upfront tokens for cached tool names + server `instructions.md` files. |
| `mcp_deferred_schema_est_tokens` | Estimated full JSON schema tokens saved via AGY lazy loading. |
| `total_startup_context_est_tokens` | Combined estimated always-on startup context (`global_charter` + `global_skills` + `mcp_lazy_index`). |

---

## 3. Keyless Skill Quality & Cross-Skill Overlap Protocol

1. **Keyless Tier-1 Gate:** Evaluate every workspace skill via:
   ```bash
   skillevaluator tier1 .agents/skills/sota-convergence-audit --no-llm --output-dir /tmp/se-tier1
   ```
   Require `exit 0`, `0` HIGH/CRITICAL security or PII findings, and Quality Grade **`A` (`>= 90/100`)**.
2. **Trigger Hygiene:** Keep descriptions third-person, concrete (avoid vague words such as `"general"`), include explicit `"Use when ..."` within the first `57` characters plus a clear `"Do not use for ..."` boundary, and include `metadata.author` and `metadata.tags`.
3. **Cross-Skill Collision Check:** Confirm pairwise token-Jaccard description overlap stays well below `0.30` across active global and repo skills so routing remains unambiguous.

---

## 4. Advisory Workstation Hygiene Checklist

Run periodically alongside `scripts/audit_ecosystem_hygiene.py --json --strict`:

- **Single Canonical Skill Root:** Keep user-global skills in one canonical directory (`~/.agents/skills/`) symlinked into `~/.gemini/config/skills/` with `~/.gemini/skills/` empty (zero hard-copy duplicates, zero CLI shadow drift).
- **Zero Dead Companion Links:** Run `skillevaluator tier1 <skill-dir> --no-llm` across custom user skills to catch broken relative Markdown references and bodies exceeding `5,000` estimated tokens.
- **Description Headroom:** Keep every skill description below `950` chars (`near_cap_over_950c == []`) so minor edits cannot silently trip the `1,024`-char spec limit.
- **Plugin Truncation Audit:** Run `agy plugin validate` on installed plugins to detect skill bodies exceeding AGY's `24,000`-byte truncation threshold.
- **High-Fan-Out MCP Scoping:** Whenever a server's cached tool count in `mcp_cached_servers` exceeds `20–30` tools, scope it to specific workspaces or front it with Code Mode / Programmatic Tool Calling.
