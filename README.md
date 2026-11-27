# AGY SOTA Convergence Repository

A clean, self-contained, cryptographically sealed **SOTA Convergence & Compounding Engineering** repository for **Google Antigravity (AGY 2.0)** and the late-2026 open AI agent ecosystem (`as-of 2026-11-26`).

Built strictly under the **Upstream-Only, Native-First Thin Layer** doctrine ([`ADR-0001`](docs/adrs/ADR-0001-meta-adr-convergence-and-zero-self-invention.md)): **11 strictly disjoint layers (`L0`–`L10`)**, **12 bounded MADR 4.0.0 ADRs**, **63 live-verified upstream install pins** (`UPSTREAM.md` + `upstream-map.toml`), **5 `ast-grep` structural ban rules** (including `CVE-2026-59726` wildcard-bind protection), a **drop-in fail-closed `.agents/` harness pack**, a **distributable zero-wrapper native AGY Practice Plugin (`plugins/agy-sota-practice/`, `agy plugin validate --strict` `0` findings)**, a **reusable `/run-workflow` audit pipeline**, a **full 3-workflow GitHub SOTA supply-chain suite** (`40`-char SHA-pinned + `harden-runner v2.23.0` + `workflow_call`), a **strict-verified 26-page Zensical (`0.1.3`) portal**, a **one-command 13-step verifier (`scripts/check.sh`)**, and an **18-gate SHA-256 sealed manifest verifier (`v3.2.0`)**.

---

## Repository Layout

```text
agy-sota-convergence/
├── AGENTS.md                         # Minimal cross-harness repo charter (<=45L, <=1,600c)
├── README.md                         # This overview & unified verification quickstart
├── LICENSE                           # MIT License (2026)
├── SECURITY.md                       # Fail-closed security policy & immutable boundaries
├── UPSTREAM.md                       # Canonical 63-entry L0-L10 upstream & SPDX registry
├── upstream-map.toml                 # Machine-verified 1:1 runtime .py -> upstream mapping
├── Makefile                          # Shortcuts (check, seal, sync-plugin, audit, docs, sbom)
├── orca.yaml                         # Orca worktree lifecycle automation (no defaultTabs)
├── .gitleaks.toml                    # Custom Gitleaks secret scanning config
├── .gitignore                        # Ignores site/, .cache/, .venv/, sbom*.json & reports/
├── pyproject.toml                    # Segregated uv dependency groups + ruff/ty config
├── mise.toml                         # Pinned CLI toolchain versions (2026-11-26)
├── sgconfig.yml                      # ast-grep (0.51.3) rule discovery configuration
├── zensical.toml                     # Zensical (0.1.3) MADR 4.0 docs portal config (25 nav pages)
├── .agents/
│   ├── hooks.json                    # Fail-closed PreToolUse + dedup SessionStart/Stop hooks
│   ├── rules/                        # Path-scoped ADR & manifest rules (snake_case trigger:)
│   ├── skills/                       # Progressive-disclosure AAIF skills (SKILL.md, Grade A 100)
│   ├── scripts/                      # Fail-closed PreToolUse & cross-session hook scripts
│   ├── schemas/                      # Typed 15-field handoff_packet.schema.json
│   └── templates/                    # Resolved-path permissions & sidecar templates
├── plugins/
│   └── agy-sota-practice/            # Distributable zero-wrapper AGY plugin pack (19 files, 0 findings)
├── rules/ast-grep/                   # 5 structural AST ban rules (models/brokers/MCP/hooks/0.0.0.0)
├── workflows/                        # Reusable AGY /run-workflow programmatic audit pipeline
├── docs/
│   ├── index.md                      # Zensical portal landing page
│   ├── adr-and-convergence-practice.md
│   ├── agy-surfaces-and-changelogs.md    # 5 AGY surfaces, 7 extensions & 2026 changelogs
│   ├── cross-session-and-agy-practice.md # 9-route messaging, security & operational playbooks
│   ├── ecosystem-frameworks-matrix.md    # Late-2026 sandboxes, runtimes, memory & eval matrix
│   ├── agy-harness-frameworks-and-full-landscape.md # 19-project meta-harness audit & 6-pillar practice
│   ├── convergence-stack.md          # Disjoint L0-L10 stack & cross-session routing
│   ├── compounding-flywheel.md       # 7-stage flywheel, anti-bloat ratchets & KPIs
│   ├── clean-install-registry.md     # 63 live-verified L0-L10 upstream install pins
│   ├── context-manifest-audit.md     # Startup context telemetry & zero-secret scorecard
│   ├── github-sota-workflows.md      # Live public ecosystem GitHub SOTA workflow & reusable gate guide
│   ├── manifest-guide.md             # Sealed manifest v3.2.0 SHA-256 ledger & verifier guide
│   └── adrs/
│       ├── CATALOG.md                # Indexed catalog across all 12 bounded ADRs
│       └── ADR-0001..ADR-0012.md     # Bounded 12-ADR MADR 4.0.0 set (META + L0-L10)
├── manifest/
│   ├── compounding_manifest.v2.schema.json
│   └── compounding_manifest.v2.json  # Cryptographically sealed canonical manifest (v3.2.0)
├── scripts/
│   ├── check.sh                      # One-command 13-step fail-closed verification harness
│   ├── verify_manifest.py            # Stdlib-only 18-gate --seal / --verify engine
│   └── audit_ecosystem_hygiene.py    # Read-only zero-secret host hygiene auditor
├── tests/
│   ├── test_hooks_and_handoff.py     # Fail-closed hook, dedup, Stop & template tests (12)
│   ├── test_manifest_v2.py           # 18-gate pass + 17 adversarial guards + scorecard (19)
│   ├── test_plugin_pack_contract.py  # Native plugin pack parity, hook & agy validate suite (3)
│   └── test_host_shim_contract.py    # Portable live workstation PreToolUse shim suite (10)
└── .github/
    ├── CODEOWNERS                    # Repository ownership (@seathatflowsinourveins)
    ├── dependabot.yml                # Weekly uv & github-actions updates (limit 5)
    ├── pull_request_template.md      # 5-item AGY SOTA merge checklist
    └── workflows/
        ├── sota-convergence-gates.yml           # Hardened 18-gate CI + weekday schedule
        ├── sota-docs-pages.yml                  # Path-filtered Zensical strict artifact build
        └── reusable-agy-sota-practice-gate.yml  # Portable workflow_call compliance gate
```

---

## Quickstart Verification (One-Command 13-Step Suite)

Run the complete fail-closed verification harness directly from the repository root:

```bash
# Run all 13 empirical verification steps in one command (or `make check`)
bash scripts/check.sh
```

Or invoke individual gates directly:

```bash
# 1. Verify all 18 cryptographic, MADR 4.0.0 bijection, upstream parity, workflow & plugin gates
python3 scripts/verify_manifest.py --verify && python3 scripts/verify_manifest.py --verify

# 2. Run all 44 unit, adversarial manifest mutation, plugin contract, and live host-shim tests
python3 -m unittest discover -s tests -v

# 3. Validate the zero-wrapper AGY Practice Plugin Pack strictly
agy plugin validate --strict --json plugins/agy-sota-practice

# 4. Run the read-only zero-secret local host customization hygiene audit
python3 scripts/audit_ecosystem_hygiene.py --json --strict

# 5. Run ast-grep structural ban rules across scripts, workflows, plugins, and hidden .agents/ hooks
ast-grep scan && ast-grep scan --no-ignore hidden

# 6. Build the Zensical (0.1.3) MADR 4.0 portal in strict mode (zero warnings, 26 HTML pages)
zensical build --clean --strict

# 7. Run static code, type, shell, secret, skill, SBOM/OSV, and CI-workflow security gates
ruff check . && ruff format --check . && ty check
shellcheck scripts/*.sh
gitleaks detect --no-git --redact --source . && gitleaks git --redact .
zizmor --offline .github/workflows/
```

### Re-Sealing After an Authorized ADR or Manifest Update

```bash
make seal
# Equivalent to:
# python3 scripts/verify_manifest.py --seal && python3 scripts/verify_manifest.py --verify && python3 scripts/verify_manifest.py --verify
```

---

## Publishing the Zensical ADR Portal

This repository ships a strict-verified `zensical.toml` configuration targeting **Zensical `0.1.3`** (the Rust-core successor to Material for MkDocs):

```bash
# Provision Zensical cleanly in an isolated tool environment (zero global pip)
uv tool install "zensical==0.1.3" && zensical --version

# Preview locally with live reload or execute a strict CI build (outputs to ignored site/)
make docs-serve   # zensical serve
make docs         # zensical build --clean --strict
```

---

## Key Documentation Entry Points

* **Portal Index:** [`docs/index.md`](docs/index.md)
* **ADR Catalog (`12/12` Bounded ADRs):** [`docs/adrs/CATALOG.md`](docs/adrs/CATALOG.md)
* **Canonical Upstream Registry (`63` Pins & SPDX):** [`UPSTREAM.md`](UPSTREAM.md) + [`upstream-map.toml`](upstream-map.toml)
* **AGY Surfaces, Extensions & Changelogs:** [`docs/agy-surfaces-and-changelogs.md`](docs/agy-surfaces-and-changelogs.md)
* **Cross-Session Messaging & Operational Practice:** [`docs/cross-session-and-agy-practice.md`](docs/cross-session-and-agy-practice.md)
* **Late-2026 Ecosystem & Frameworks Matrix:** [`docs/ecosystem-frameworks-matrix.md`](docs/ecosystem-frameworks-matrix.md)
* **AGY Harness Frameworks & Full-Landscape Practice:** [`docs/agy-harness-frameworks-and-full-landscape.md`](docs/agy-harness-frameworks-and-full-landscape.md)
* **Zero-Wrapper AGY Practice Plugin Pack:** [`plugins/agy-sota-practice/README.md`](plugins/agy-sota-practice/README.md)
* **Disjoint `L0`–`L10` Convergence Stack:** [`docs/convergence-stack.md`](docs/convergence-stack.md)
* **7-Stage Compounding Flywheel & KPIs:** [`docs/compounding-flywheel.md`](docs/compounding-flywheel.md)
* **ADR Practice, Saturation Gate & Zero-Self-Invention Rubric:** [`docs/adr-and-convergence-practice.md`](docs/adr-and-convergence-practice.md)
* **Clean Upstream Installation Registry (`63` Pins):** [`docs/clean-install-registry.md`](docs/clean-install-registry.md)
* **Context Telemetry & Scorecard Audit:** [`docs/context-manifest-audit.md`](docs/context-manifest-audit.md)
* **GitHub SOTA Workflows & Reusable Gate:** [`docs/github-sota-workflows.md`](docs/github-sota-workflows.md)
* **Manifest v3.2.0 Cryptographic Guide:** [`docs/manifest-guide.md`](docs/manifest-guide.md)
* **Security Policy:** [`SECURITY.md`](SECURITY.md)
* **Meta-ADR (`ADR-0001`):** [`docs/adrs/ADR-0001-meta-adr-convergence-and-zero-self-invention.md`](docs/adrs/ADR-0001-meta-adr-convergence-and-zero-self-invention.md)
