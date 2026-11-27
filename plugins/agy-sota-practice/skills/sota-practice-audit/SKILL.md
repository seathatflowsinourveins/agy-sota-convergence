---
name: sota-practice-audit
description: Use when auditing any repository or AGY workstation for SOTA harness, context-budget, hook, or supply-chain compliance. Do not use for application feature coding or secret files.
metadata:
  author: Antigravity SOTA Convergence Team <sota-convergence@antigravity.local>
  tags: [antigravity, audit, harness, security, supply-chain]
---

# SOTA Practice Audit Runbook

## Purpose

Execute a portable, deterministic, zero-secret compliance audit across any repository or Google Antigravity (`AGY 2.0`) workstation, checking charter context budgets, progressive-disclosure rules and skills, fail-closed hooks, zero-wrapper discipline, and GitHub Actions supply-chain controls.

## Prerequisites

- Python `>= 3.12` (stdlib-only for local structural checks).
- Pinned static and security CLIs provisioned cleanly via `mise` or `uv tool`: `ruff==0.17.6`, `ty==0.0.112`, `ast-grep-cli==0.51.3`, `gitleaks@8.30.1`, `shellcheck@0.11.0`, `zizmor==1.33.1`, `syft@1.57.2`, `osv-scanner@2.7.1`, and `skillevaluator==1.2.1`.
- Read-only access to the target workspace with zero reads of secret files, credentials, or private host configs.

## Instructions

1. **Audit charter and customization budgets (`AGENTS.md <= 45L / <= 1,600c`, `0` HTML comments, snake_case rules, `0` tilde deny paths):**
   ```bash
   python3 -c '
   from pathlib import Path
   p = Path("AGENTS.md")
   t = p.read_text(encoding="utf-8")
   assert len(t.splitlines()) <= 45 and len(t) <= 1600 and (chr(60) + "!--") not in t
   print(f"CHARTER_OK: {len(t.splitlines())}L/{len(t)}c")
   '
   ```
2. **Verify zero wrapper daemons and run static code, type, shell, and AST gates:**
   ```bash
   ruff check . && ruff format --check .
   ty check
   shellcheck scripts/*.sh
   ast-grep scan && ast-grep scan .agents/scripts
   ```
3. **Run secret scanning, GitHub Actions supply-chain checks, and keyless SkillEvaluator Tier 1:**
   ```bash
   gitleaks detect --no-git --redact --source .
   zizmor --offline .github/workflows/
   skillevaluator tier1 .agents/skills --no-llm --output-dir /tmp/se-audit
   ```
   Remove the temporary `/tmp/se-audit` directory once reviewed.
4. **Validate SBOM advisories and native AGY plugin packaging when present:**
   ```bash
   syft dir:. -o cyclonedx-json=/tmp/sbom.cdx.json && osv-scanner scan source -L /tmp/sbom.cdx.json
   agy plugin validate --strict --json plugins/agy-sota-practice
   ```
   Remove the temporary `/tmp/sbom.cdx.json` file once reviewed.

## Examples

### Example 1: Auditing GitHub Actions supply-chain hygiene

```bash
zizmor --offline .github/workflows/
# Expected: No findings to report. Good job!
```

### Example 2: Running the unified repository check script

```bash
bash scripts/check.sh
# Expected: exit 0 with verbatim pass counts across every gate
```

## Limitations

- Strictly read-only with respect to private credentials, environment files, OAuth token caches, runtime host config stores, and immutable upstream mirror roots.
- `skillevaluator tier1 --no-llm` evaluates static schema, security, hygiene, and quality heuristics; live A/B behavioral Skill Lift requires Tier 3 containerized evaluation with an LLM provider.
- Does not auto-mutate repository files or push changes to Git remotes without explicit user direction.

## Troubleshooting

| Symptom / Error | Root Cause | Resolution |
| :--- | :--- | :--- |
| `zizmor` flags `unpinned-uses` or `template-injection` | Floating action tag or `${{ inputs.* }}` interpolated inside `run:`. | Pin every external `uses:` to a 40-char commit SHA and pass dynamic inputs strictly via `env:`. |
| `agy plugin validate --strict` fails on `hooks/hooks.json` | Native AGY plugins only read root `<plugin-root>/hooks.json`. | Move hooks to `<plugin-root>/hooks.json` with relative `./scripts/*.py` commands and `"enabled": false`. |
| `osv-scanner scan source -r .` exits `128` | Repository has no package lockfile. | Generate a CycloneDX SBOM with `syft dir:.` and scan via `osv-scanner scan source -L`. |
| `AGENTS.md` exceeds `1,600` chars or contains HTML comments | Rationales or checklists drifted into the always-on charter. | Strip HTML comments and move conditional guidance into `.agents/rules/*.md` or `SKILL.md`. |
