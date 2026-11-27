# GitHub SOTA Workflows & Unified 4-Repo Governance Standard

**As-of Date:** 2026-11-26  
**Manifest Baseline:** `v3.1.0` (`ADR-0001`, `ADR-0010`, `ADR-0012`)

This guide defines the fail-closed GitHub Actions, supply-chain hardening, and reusable workflow standard shared across the four converged engineering repositories in our workspace ecosystem.

---

## 1. Unified 4-Repository Workspace Ecosystem

Every repository in the ecosystem adheres to one non-overlapping ownership boundary, one pinned CLI toolchain (`2026-11-26`), and one deterministic GitHub supply-chain baseline:

| Repository | Exclusive Role | Primary CI & Docs Workflows | Governance Anchor |
| :--- | :--- | :--- | :--- |
| **`dot-github`** | Organization-wide profile, shared governance ADRs (`ADR-0045`), and `ECOSYSTEM_ORG_MANIFEST.json` linking sibling repo seals. | Org-level standards & cross-repo manifest verification. | Organization governance ledger |
| **`agy-sota-convergence`** *(this repo)* | Definitive Google Antigravity (`AGY 2.0`) SOTA practice, bounded 12-ADR MADR 4.0.0 architecture, 63-pin `UPSTREAM.md`, drop-in `.agents/` pack, and reusable GitHub practice gate. | `sota-convergence-gates.yml`, `sota-docs-pages.yml`, `reusable-agy-sota-practice-gate.yml` | `manifest/compounding_manifest.v2.json` (`v3.1.0`, 17 gates) |
| **`sota-research-convergence`** | 7-plane scientific & research-engineering convergence stack (`UPSTREAM.md` + `upstream-map.toml`, Marimo notebooks, Zensical portal, fail-closed `check.sh`). | `convergence-ci.yml`, `convergence-docs-pages.yml` | Sealed research convergence manifest (`11/11` native checks) |
| **`tier0-quant`** | Quantitative research and execution-sandbox repository subject to strict zero-live-broker isolation and AGY charter/CI compliance. | `tier0-ci.yml`, `tier0-docs-pages.yml`, `tier0-workstation-dispatch.yml` | Audited continuously against `v3.1.0` AGY practice & SHA-pin rules |

---

## 2. Mandatory GitHub SOTA Security Controls

Every workflow under `.github/workflows/*.yml` MUST satisfy all eight deterministic supply-chain controls, enforced mechanically by `scripts/verify_manifest.py` Gate `[17]` and `zizmor --offline .github/workflows/`:

1. **40-Character Commit SHA Pinning (Zero Floating Tags):** Every external `uses:` reference MUST pin an exact immutable 40-hex commit SHA accompanied by a version comment (never `@v4`, `@main`, or floating branches).
2. **Runtime Egress Hardening (`step-security/harden-runner`):** Every job starts with `step-security/harden-runner@e14015d583714f6e62063499dc959a02595150a1 # v2.21.1` configured with `egress-policy: audit` (or strict allowlist for locked-down release jobs).
3. **Least-Privilege Token Scoping:** Declare top-level `permissions: {}` and grant only the minimum per-job scope required (typically `permissions: { contents: read }`). Always set `persist-credentials: false` on `actions/checkout`.
4. **Zero Template Injection (`zizmor` Clean):** Never interpolate `${{ inputs.* }}`, `${{ github.event.* }}`, or untrusted context expressions directly inside `run:` shell scripts. Pass all dynamic values via `env:` variables and quote them safely.
5. **Bounded Concurrency & Timeouts:** Declare `concurrency` (`cancel-in-progress: ${{ github.event_name == 'pull_request' }}`) and explicit `timeout-minutes` (`<= 15`) on every job to prevent runaway runners.
6. **Weekday Scheduled Drift Sweeps + Manual Dispatch:** Primary CI gates run on `push` (`main`), `pull_request`, weekday `schedule` (`0 13 * * 1-5`), and `workflow_dispatch` so sunset or upstream drift is caught even during quiet periods.
7. **Pinned Security & Supply-Chain Tooling (`2026-11-26`):**
   - `zizmor==1.33.1` (`--offline .github/workflows/` scanning every workflow file, `0` findings)
   - `gitleaks@8.30.1` (`git --redact .` + `detect --no-git --redact --source .`, `0` secrets)
   - `syft@1.57.2` -> `osv-scanner@2.7.1` (CycloneDX SBOM piped into OSV-Scanner, `0` CVEs)
   - `skillevaluator==1.2.1` (`tier1 --no-llm` keyless quality & security gate, Grade `A`)
   - `ruff==0.17.6`, `ty==0.0.112`, `ast-grep-cli==0.51.3`, `shellcheck@0.11.0`, `zensical==0.1.3`
8. **Repository Governance Metadata:** Every repository ships `.github/CODEOWNERS`, `.github/dependabot.yml` (weekly `uv` + `github-actions`, `open-pull-requests-limit: 5`), and `.github/pull_request_template.md`.

### Pinned GitHub Action Reference Table (`2026-11-26`)

| Action | Immutable 40-Char SHA Pin | Release Comment | Role |
| :--- | :--- | :--- | :--- |
| `step-security/harden-runner` | `e14015d583714f6e62063499dc959a02595150a1` | `# v2.21.1` | Runner network egress telemetry & hardening |
| `actions/checkout` | `3d3c42e5aac5ba805825da76410c181273ba90b1` | `# v7.0.1` | Repo checkout (`persist-credentials: false`) |
| `actions/setup-python` | `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` | `# v7.1.0` | Python `3.12` runtime setup |
| `astral-sh/setup-uv` | `1db35dd8eee11c5894872e0b383ae6c406cf738d` | `# v10.4.0` | Pinned `uv 0.13.10` isolated runner |
| `jdx/mise-action` | `924e7c586e33d7d4bae9c14e26c5d22e2beb6e78` | `# v5.3.0` | Pinned `mise.toml` CLI toolchain provisioning |
| `actions/upload-artifact` | `cf430e030ddbb5b0abf93d22962f4752f3646cd9` | `# v7.0.2` | Zensical strict portal artifact (`retention-days: 14`) |

---

## 3. Repository Workflow Inventory

| Workflow File | Triggers | What It Enforces |
| :--- | :--- | :--- |
| `.github/workflows/sota-convergence-gates.yml` | `push` (`main`), `pull_request`, weekday `schedule` (`0 13 * * 1-5`), `workflow_dispatch` | Double `17/17` manifest `--verify`, `39/39` `unittest`, `ast-grep` (+ hidden `.agents/`), `ruff`, `ty`, `shellcheck`, `gitleaks` (`git` + `--no-git`), `skillevaluator`, `syft`->`osv-scanner`, `zizmor --offline .github/workflows/`, and strict `zensical` build. |
| `.github/workflows/sota-docs-pages.yml` | Path-filtered `push`/`pull_request` (`docs/**`, `zensical.toml`, `UPSTREAM.md`) + `workflow_dispatch` | Strict `zensical==0.1.3 build --clean --strict` generating the full 25-HTML-page portal and uploading a 14-day artifact. |
| `.github/workflows/reusable-agy-sota-practice-gate.yml` | `workflow_call` (`check-docs`, `skill-path` inputs) | Portable drop-in compliance gate for any repository enforcing `AGENTS.md` (`<=45L/1,600c`, `0` HTML comments), `.agents/rules/*.md` (snake_case `trigger:`, `<=24KB`), `.agents/skills/*/SKILL.md` (`<=1,024c` + `skillevaluator`), `0` `~/` deny rules, `0` Nov-30 retiring models, 40-char SHA workflow pins, SHA-256-verified `gitleaks v8.30.1`, `zizmor v1.33.1`, and optional Zensical build. |

---

## 4. Adopting the Reusable Practice Gate in Sibling Repositories

Once `agy-sota-convergence` is hosted on GitHub under your organization, any sibling repository (`sota-research-convergence`, `tier0-quant`, or new projects) can invoke the shared gate by pinning the exact 40-char commit SHA of `reusable-agy-sota-practice-gate.yml`:

```yaml
name: AGY SOTA Practice Compliance

on:
  pull_request:
  push:
    branches: [main]
  workflow_dispatch:

permissions: {}

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  agy-practice:
    permissions:
      contents: read
    uses: <org>/agy-sota-convergence/.github/workflows/reusable-agy-sota-practice-gate.yml@<40-char-commit-sha>
    with:
      check-docs: true
      skill-path: ".agents/skills/my-skill"
```

### Local Parity Verification

Run the exact same workflow and repository supply-chain checks locally before opening a pull request:

```bash
# Run full 12-step local verification suite (including zizmor across all .github/workflows/)
bash scripts/check.sh

# Or inspect GitHub Actions supply-chain hygiene standalone
zizmor --offline .github/workflows/
```
