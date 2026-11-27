# Security Policy

This repository enforces a **fail-closed, zero-secret, upstream-only** security posture across all scripts, hooks, templates, workflows, and architectural records (see [`docs/adrs/ADR-0010-L8-deterministic-security-and-fail-closed-gates.md`](docs/adrs/ADR-0010-L8-deterministic-security-and-fail-closed-gates.md)).

## Immutable Security Boundaries

1. **Zero Committed Secrets:** Never read, print, commit, or embed credentials, API keys, `.env*` files, `auth.json`, `mcp_oauth_tokens.json`, private SSH/AWS keys, or runtime token stores. Enforced mechanically via `gitleaks` (`.gitleaks.toml`), `.agents/scripts/pre_tool_fail_closed.py`, and CI gates.
2. **Immutable Host & Upstream Perimeters:** Tooling in this repository operates strictly read-only on non-secret local customization surfaces and NEVER reads or modifies `~/.gemini/config/config.json`, `~/.gemini/config/mcp_config.json`, `~/.gemini/antigravity-cli/settings.json`, `~/.agents/security-policy.toml`, `~/.agents/hooks/**`, or immutable upstream pins (`~/Documents/upstream/`).
3. **Zero Live Broker Endpoints:** Live real-money broker endpoints (`api.alpaca.markets`, IBKR ports `:4001`, `:7496`, `:8798`, `:8796`, or `paper=False`) are forbidden across all runtime scripts and enforced statically by `rules/ast-grep/no-live-broker-ports.yml` and `.agents/scripts/pre_tool_fail_closed.py`.
4. **Fail-Closed `PreToolUse` Hook Contract:** Antigravity's hook runtime fails open when a hook process exits non-zero. Therefore, every security `PreToolUse` hook MUST trap all exceptions, malformed JSON, empty stdin, and timeouts and emit valid JSON `{"decision":"deny","reason":"..."}` with **exit code `0`**. Enforced statically by `rules/ast-grep/no-fail-open-hook-exit.yml` and verified dynamically by `tests/test_hooks_and_handoff.py` and `tests/test_host_shim_contract.py`.
5. **Resolved Absolute Deny Paths & Least-Privilege CI:** Standing permission baselines MUST use resolved absolute paths (never unexpanded `(~/`). GitHub Actions workflows MUST declare `permissions: {}` at top level, minimal `contents: read` per job, `persist-credentials: false`, full 40-character commit SHA pins, and pass `zizmor --offline` with `0` findings.

## Verifying Security Gates Locally

Run the full fail-closed verification suite from the repository root:

```bash
bash scripts/check.sh
```

## Reporting a Vulnerability

If you discover a bypass in any fail-closed hook, manifest verification gate, `ast-grep` rule, or CI workflow, open a private security advisory or submit a minimal failing regression test against `tests/test_hooks_and_handoff.py` or `tests/test_manifest_v2.py` without including real credentials or sensitive host data.
