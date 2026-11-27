---
name: sota-convergence-audit
description: Use when auditing or re-sealing the SOTA convergence manifest, ADRs, hooks, or host context hygiene. Do not use for application feature coding, secret files, or upstream forks.
metadata:
  author: Antigravity SOTA Convergence Team <sota-convergence@antigravity.local>
  tags: [antigravity, adr, manifest, compliance, security]
---

# SOTA Convergence Audit Runbook

## Purpose

Provide a deterministic, fail-closed verification and cryptographic re-sealing runbook for the Google Antigravity (AGY) SOTA Convergence repository, covering its 17-gate manifest verifier, bounded 12-ADR MADR 4.0.0 ledger, `UPSTREAM.md`/`upstream-map.toml` provenance parity, unit and mutation tests, static security gates, SBOM vulnerability scans, and zero-secret host context scorecard.

## Prerequisites

- Python `>= 3.12` (stdlib-only for `scripts/verify_manifest.py`, `scripts/audit_ecosystem_hygiene.py`, and `tests/`).
- Pinned static and security CLIs provisioned cleanly via `mise.toml` or `uv tool`: `ruff==0.17.6`, `ty==0.0.112`, `ast-grep-cli==0.51.3`, `gitleaks@8.30.1`, `shellcheck@0.11.0`, `zizmor==1.33.1`, `syft@1.57.2`, `osv-scanner@2.7.1`, `skillevaluator==1.2.1`, and `zensical==0.1.3`.
- Execution from the repository root with zero access to secret files or credentials.

## Instructions

1. **Verify the sealed manifest twice for determinism (`17/17` `[PASS]`, `exit 0`):**
   ```bash
   python3 scripts/verify_manifest.py --verify
   python3 scripts/verify_manifest.py --verify
   ```
   After any authorized edit to `docs/adrs/ADR-*.md` or `manifest/compounding_manifest.v2.json`, re-embed all 12 ADR SHA-256 hashes and re-seal the canonical root digest, then sync `docs/manifest-guide.md`:
   ```bash
   python3 scripts/verify_manifest.py --seal
   ```
2. **Run the complete stdlib `unittest` suite (hooks, handoff, host-shim contract, live manifest, 14 adversarial mutations, and scorecard):**
   ```bash
   python3 -m unittest discover -s tests -v
   ```
3. **Run static lint, formatting, typing, shell, structural `ast-grep`, GitHub Actions, and secret gates:**
   ```bash
   ruff check . && ruff format --check .
   ty check
   shellcheck scripts/*.sh
   ast-grep scan && ast-grep scan .agents/scripts
   zizmor --offline .github/workflows/sota-convergence-gates.yml
   gitleaks git --redact . && gitleaks detect --no-git --redact --source .
   ```
4. **Run keyless SkillEvaluator Tier 1, Syft CycloneDX SBOM -> OSV-Scanner, and read-only host context scorecard:**
   ```bash
   skillevaluator tier1 .agents/skills/sota-convergence-audit --no-llm --output-dir /tmp/se-tier1
   syft dir:. -o cyclonedx-json=/tmp/sbom.cdx.json && osv-scanner scan source -L /tmp/sbom.cdx.json
   python3 scripts/audit_ecosystem_hygiene.py --json --strict
   ```
   Remove the temporary `/tmp/sbom.cdx.json` and `/tmp/se-tier1` artifacts once reviewed.
5. **Validate and strictly build the Zensical MADR 4.0.0 documentation portal:**
   ```bash
   zensical build --strict
   ```

## Examples

### Example 1: Verifying after an ADR update

```bash
python3 scripts/verify_manifest.py --seal
python3 scripts/verify_manifest.py --verify
# Expected: CHECKS : 17/17 passed | RESULT : VERIFIED PASS
```

### Example 2: Inspecting the zero-secret startup context scorecard

```bash
python3 scripts/audit_ecosystem_hygiene.py --json --strict
# Expected: "status": "PASS", "secrets_accessed": false, "total_findings": 0
```

## Limitations

- Strictly read-only with respect to credentials and private settings: never inspects private environment files, runtime configuration stores, OAuth token caches, plugin auth files, or immutable upstream mirror roots.
- `skillevaluator tier1 --no-llm` validates static schema, security, PII, license, secrets, and quality heuristics only; full behavioral A/B `skill_lift` requires Tier 3 containerized Harbor evaluation with an LLM provider.
- `audit_ecosystem_hygiene.py` checks local host symlink parity and lazy MCP schema caches without mutating host files or packages.

## Troubleshooting

| Symptom / Error | Root Cause | Resolution |
| :--- | :--- | :--- |
| `[10][FAIL] sha256_integrity_seal` or `[12][FAIL] adr_files_sha256_parity` | An ADR or manifest file was edited without re-sealing. | Run `python3 scripts/verify_manifest.py --seal`, update `docs/manifest-guide.md`, and re-run `--verify`. |
| `osv-scanner scan source -r .` exits `128` | Stdlib-only repository contains no lockfile (`uv.lock`/`package-lock.json`). | Pipe a Syft CycloneDX SBOM via `syft dir:. -o cyclonedx-json=/tmp/sbom.cdx.json && osv-scanner scan source -L /tmp/sbom.cdx.json`. |
| `ast-grep scan` skips `.agents/` hooks | `ast-grep` skips dot-directories unless explicitly targeted. | Always pair `ast-grep scan` with an explicit path target `ast-grep scan .agents/scripts`. |
| `skillevaluator` creates a local `reports/` directory | Default `--output-dir` points to `./reports`. | Pass `--output-dir /tmp/se-tier1` and remove temporary reports after checking. |
