# SOTA Convergence Practice (`agy-sota-practice`)

A **zero-wrapper, zero-daemon, zero-idle-token** native Google Antigravity (`AGY 2.0`) practice plugin pack extracted directly from [`seathatflowsinourveins/agy-sota-convergence`](https://github.com/seathatflowsinourveins/agy-sota-convergence).

## What Is Bundled

- **2 Progressive-Disclosure Rules (`rules/`):** `sota-harness-guardrails.md` (`trigger: model_decision`) and `governance-files-guard.md` (`trigger: glob`). Intentionally ships **no** `rules/AGENTS.md` (`0` idle tokens on unrelated turns).
- **3 Orthogonal Grade-A Skills (`skills/`):**
  - `/sota-practice-audit` — Cross-repo SOTA harness, context-budget, hook, and supply-chain compliance audit.
  - `/adr-madr4-review` — Bounded `1..12` MADR 4.0.0 ADR authoring and 5-Question Zero-Self-Invention Gate.
  - `/cross-session-handoff` — Typed SHA-256 `handoff_packet.json` creation and 9-route continuity selection.
- **2 Least-Privilege Read-Only Subagents (`agents/`):** `sota-auditor` (`commandExecutionPolicy: sandbox`, no write tools) and `adr-steward` (`commandExecutionPolicy: off`, `inheritMcp: false`).
- **Opt-In Fail-Closed & Continuity Hooks (`hooks.json` + `scripts/`):** Ships with `"enabled": false` on both hook groups so installing the plugin never collides with an existing host security policy.
- **Reusable `/run-workflow` Pipeline & Templates (`workflows/`, `templates/`):** Byte-for-byte synced via `make sync-plugin` and verified cryptographically in CI.

## Install & Validate

```bash
# Validate strictly with AGY CLI (expects exit 0 and findings: [])
agy plugin validate --strict --json plugins/agy-sota-practice

# Install from GitHub into any AGY 2.0 workstation
agy plugin install https://github.com/seathatflowsinourveins/agy-sota-convergence/tree/main/plugins/agy-sota-practice
```
