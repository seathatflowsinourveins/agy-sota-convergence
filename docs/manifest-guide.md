# Compounding Convergence Manifest `v3.0.0` — Operational & Verification Guide

- **As of:** `2026-11-26`
- **Manifest Version:** `3.0.0` (`schema_version`: `2.1.0`, JSON Schema Draft 2020-12 strict)
- **Architecture Doctrine:** `upstream_only_zero_self_invention` (`strict_ratchet_fail_closed`)
- **Saturation Status:** `saturated` (`0` unresolved contradictions, `0` unverified claims, `61` tracked repository files, `12/12` MADR 4.0.0 ADRs sealed under `docs/adrs/`, `11/11` disjoint `L0`–`L10` layers with `38` exclusive domains and `0` overlaps, `63/63` live-verified clean-install pins synchronized 1:1 with `UPSTREAM.md`, `5/5` runtime `.py` adapters mapped 1:1 in `upstream-map.toml`, `17/17` automated manifest gates passing, `38/38` unit/contract/mutation/scorecard tests passing, `0` host hygiene findings, live `skillevaluator` Tier-1 Grade `A 100.0/100`, live `zensical==0.1.3` strict portal build `24` HTML pages passing, live `ast-grep` + `shellcheck` + `ruff` + `ty` + `gitleaks` + `zizmor` + `syft`/`osv-scanner` passing via `bash scripts/check.sh` `12/12`)
- **Verified Canonical Root SHA-256 Seal (`100,991` canonical UTF-8 bytes):** `642ed427ab0eed77a382dd9fc4c9575fb4942310bffe075e4883722501ad8afc`

---

## 1. Repository Governance Pack Inventory

| Path | Role | Verification Contract |
| :--- | :--- | :--- |
| `manifest/compounding_manifest.v2.schema.json` | Strict Draft 2020-12 JSON Schema | Enforces `additionalProperties: false` across all **11** top-level blocks (`metadata`, `surfaces`, `layers`, `cross_session_routing`, `compounding_flywheel`, `deprecations_and_sunsets`, `security_invariants`, `adr_governance`, `clean_install_registry`, `saturation_proof`, `integrity`). |
| `manifest/compounding_manifest.v2.json` | Canonical sealed manifest (`v3.0.0`) | Single machine-readable source of truth binding 5 AGY products / 7 IDE extensions, 11 disjoint layers (`38` domains), 9 cross-session routes + 15-field `handoff_packet`, 7-stage compounding flywheel, 10 sunsets + 4 doc drifts, fail-closed security invariants, **12/12 repo ADR SHA-256 hashes**, **63 pinned clean-install entries**, and **7-criterion saturation proof** across all `61` tracked files. |
| `UPSTREAM.md` + `upstream-map.toml` | Upstream Provenance & Adapter Bijection | `UPSTREAM.md` records 100% (`63/63`) of manifest winners with SPDX licenses and HTTPS URLs; `upstream-map.toml` enforces exact `5/5` bijection across every runtime `.py` file (`scripts/`, `workflows/`, `.agents/scripts/`). |
| `scripts/verify_manifest.py` | Stdlib-only Python 3 **17-gate** sealer & verifier | Zero external dependencies. Auto-embeds 12/12 live `docs/adrs/ADR-*.md` SHA-256 digests on `--seal`, seals canonical root SHA-256, and verifies all **17 gates** (`exit 0` only on `17/17` `[PASS]`; `exit 1` on any defect). |
| `scripts/check.sh` + `Makefile` | Unified 12-step fail-closed verification harness | Executes double `--verify`, `unittest`, host hygiene, `ast-grep`, `ruff`, `ty`, `shellcheck`, `gitleaks`, `zizmor`, `skillevaluator`, `syft`->`osv-scanner`, and `zensical build --clean --strict` with temp cleanup trap. |
| `tests/test_manifest_v2.py` | Stdlib `unittest` suite (`16` tests) | Verifies live `17/17` pass, **14** isolated temp-directory adversarial mutations (`exit 1` fail-closed, including Gates `[16]` & `[17]`), and isolated zero-secret `context_manifest_scorecard` validation. |
| `tests/test_hooks_and_handoff.py` | Stdlib `unittest` suite (`12` tests) | Verifies `.agents/scripts/pre_tool_fail_closed.py`, `.agents/scripts/cross_session_hooks.py`, `.agents/hooks.json`, `handoff_packet.schema.json`, and all 3 templates. |
| `tests/test_host_shim_contract.py` | Portable host security shim contract tests (`10` tests) | Live-verifies host `agy-hook-shim.py` / `policy_core.py` / `security-policy.toml` fail-closed guards (`@unittest.skipUnless` portable in CI; `10/10 OK` live on hardened host). |
| `sgconfig.yml` + `rules/ast-grep/*.yml` | Structural `ast-grep` (`0.51.3`) ban rules (`4` files / `6` rules) | Mechanically bans retiring Nov-30 model slugs, live broker ports, deprecated `McpSseServer`/AutoGen/SK imports, and fail-open non-zero hook exits (`0` findings on clean repo). |
| `workflows/sota_convergence_audit.py` + `workflows/workflow.json` | Reusable AGY `/run-workflow` programmatic audit pipeline | Orchestrates parallel manifest, host hygiene, `ast-grep`, and unit-test checks without bloating main session context. |
| `scripts/audit_ecosystem_hygiene.py` | Stdlib read-only zero-secret host auditor | Audits live user charter, global skill roots/symlinks/caps, hooks, sidecar permissions, and non-secret `.md` sunset hygiene without opening secret files (`HIGH=0, MEDIUM=0, LOW=0`). |

---

## 2. Two-Level Cryptographic Seal & All 17 Manifest Gates

1. **Level 1 — 12/12 ADR File Digests (`adr_governance.adrs[].sha256`):** Every `docs/adrs/ADR-0001..0012.md` file is hashed byte-for-byte via SHA-256. Any single-byte tamper breaks Gate `[12]`.
2. **Level 2 — Canonical Manifest Root Digest (`integrity.sha256`):** With `integrity.sha256` excluded (retaining `algorithm`, `canonicalization`, and `payload_scope`), the full JSON object—including all 12 ADR hashes—is canonically serialized (`sort_keys=True, separators=(",", ":"), ensure_ascii=False`) as UTF-8 bytes and hashed via SHA-256. Any single-byte manifest tamper breaks Gate `[10]`.

| Gate | Name | Enforced Invariant |
| :--- | :--- | :--- |
| `[01]` | `schema_draft_2020_12` | `$schema == "https://json-schema.org/draft/2020-12/schema"` |
| `[02]` | `schema_validation` | Recursive Draft 2020-12 validation across all 11 blocks (`additionalProperties: false`, `0` errors) |
| `[03]` | `disjoint_L0_L10_layers` | Exact 11 unique layers `L0`–`L10`, `38` mutually exclusive domains, `0` overlaps |
| `[04]` | `zero_retiring_nov30_models_active` | Dot/hyphen/underscore normalized scan (`3[._-]8`, `4[._-]6`, `gemini[-_ ]?4[-_ ]?argon`, `gpt[-_ ]?oss[-_ ]?120b`) across every root block except `deprecations_and_sunsets` |
| `[05]` | `zero_unpinned_placeholders` | Zero unpinned stub/floating tokens across the entire manifest |
| `[06]` | `cross_session_9_routes_complete` | All 9 canonical cross-session routes uniquely present |
| `[07]` | `compounding_7_stages_and_ratchets` | Exact 7 ordered flywheel stages (`1..7`), SkillEvaluator T1/T3 gates, and hard anti-bloat ratchets (`24KB` / `20k` / `<=3` eager MCP / `delete_to_add_policy` / `temporal_invalidation_required`) |
| `[08]` | `security_and_sandbox_invariants` | OS sandbox required (Linux kernel namespaces — zero `bubblewrap` claim on AGY Linux; macOS Seatbelt; Win 11 24H2+ AppContainer), `Deny > Ask > Allow`, resolved absolute deny paths (zero `(~/`), fail-closed hooks, host-verified facts, zero secrets |
| `[09]` | `agy_5_surfaces_7_extensions` | 5 official AGY products, 7 IDE extensions, `agy acp`, standalone IDE `enterprise_supported: false` |
| `[10]` | `sha256_integrity_seal` | Recomputed canonical UTF-8 sorted-key JSON SHA-256 matches `integrity.sha256` (`100,991` bytes) |
| `[11]` | `adr_12_bounded_bijection_and_madr4` | Exact 12 ADRs under `docs/adrs/` (`ADR-0001` `META` + 1:1 bijection `ADR-0002`..`ADR-0012` <-> `L0`..`L10`), 7-key YAML frontmatter (`status: accepted`, `date: 2026-11-26`), H1 prefix `# ADR-00XX:`, and all 9 required MADR 4.0 headings in order |
| `[12]` | `adr_files_sha256_parity` | 12/12 `docs/adrs/ADR-*.md` files match recorded `adr_governance.adrs[].sha256` byte-for-byte |
| `[13]` | `clean_install_registry_coverage` | `11/11` layers (`L0`–`L10`) covered across `63` unique pinned clean-install entries (`0` unpinned/floating tags) |
| `[14]` | `saturation_proof_invariants` | `saturation_status == "saturated"`, `zero_self_invention_verified == true`, `unresolved_contradictions == 0`, `unverified_claims == 0`, `adr_count == 12`, `layer_count == 11`, `disjoint_overlap_count == 0`, `clean_install_layers_covered == 11` |
| `[15]` | `repo_hygiene_and_anti_bloat_ratchet` | `AGENTS.md` `<=45` lines and `<=1,600` chars (`11L/1,501c`), every `.agents/skills/*/SKILL.md` valid frontmatter with `name == dir` and `description <= 1,024` chars (`176c`), every `.agents/rules/*.md` snake_case `trigger:` and `<=24,000B`, `.agents/hooks.json` valid JSON object, and `0` unexpanded `(~/` deny rules in `.agents/**/*.json` |
| `[16]` | `upstream_registry_and_map_parity` | `UPSTREAM.md` matches `63/63` manifest `clean_install_registry` winner IDs & layers with valid SPDX licenses & HTTPS URLs; `upstream-map.toml` enforces exact `5/5` bijection with all runtime `.py` files under `scripts/`, `workflows/`, and `.agents/scripts/` |
| `[17]` | `repo_scaffolding_and_portal_integrity` | All `11/11` first-class scaffolding files exist (`LICENSE`, `SECURITY.md`, `.gitleaks.toml`, `.gitignore`, `orca.yaml`, `Makefile`, `scripts/check.sh`, `UPSTREAM.md`, `upstream-map.toml`, `zensical.toml`, `docs/adrs/CATALOG.md`), `scripts/check.sh` is executable, `.gitleaks.toml` parses as valid TOML, `orca.yaml` omits `defaultTabs`, and `zensical.toml` resolves `23/23` `nav` docs on disk |

---

## 3. Sealed 12/12 Repository ADR SHA-256 Ledger

| ID | Layer | Owner | Repository File | Bytes | Verified File SHA-256 |
| :--- | :--- | :--- | :--- | ---: | :--- |
| `ADR-0001` | `META` | `sota-ecosystem` | [`docs/adrs/ADR-0001-meta-adr-convergence-and-zero-self-invention.md`](adrs/ADR-0001-meta-adr-convergence-and-zero-self-invention.md) | `10,477` | `ed9252ee5800a9dd60613581d3426aa51bd482d2042f08085caea6630474a653` |
| `ADR-0002` | `L0` | `cross-session` | [`docs/adrs/ADR-0002-L0-execution-isolation-and-sandboxes.md`](adrs/ADR-0002-L0-execution-isolation-and-sandboxes.md) | `9,135` | `bd654bf7ad0db72d6a1c6c48dab5fd3855dc45b5c02bb87cedc8d78c0bf6989d` |
| `ADR-0003` | `L1` | `changelogs` | [`docs/adrs/ADR-0003-L1-frontier-models-routing-and-sunsets.md`](adrs/ADR-0003-L1-frontier-models-routing-and-sunsets.md) | `12,616` | `812e990ea1d2b926df33a96dd74feafeb5152a4f7085733f4f3854ce4db35adc` |
| `ADR-0004` | `L2` | `changelogs` | [`docs/adrs/ADR-0004-L2-multi-surface-agy-harness-and-acp.md`](adrs/ADR-0004-L2-multi-surface-agy-harness-and-acp.md) | `13,785` | `206e6557ffd06b7416ea5e765edad0641f286b3a1f3dfd5d1ca8e6dcfb824994` |
| `ADR-0005` | `L3` | `cross-session` | [`docs/adrs/ADR-0005-L3-intra-session-multi-agent-orchestration.md`](adrs/ADR-0005-L3-intra-session-multi-agent-orchestration.md) | `9,877` | `ce695e707b6995468bde18074893a56ab9c20ca098c4ae1055f2731b63b585e8` |
| `ADR-0006` | `L4` | `cross-session` | [`docs/adrs/ADR-0006-L4-cross-session-and-federated-messaging.md`](adrs/ADR-0006-L4-cross-session-and-federated-messaging.md) | `11,272` | `1217c589a1dacf0d990a3aaab57ac3220dac587deece6d2827588c28dbb08a4c` |
| `ADR-0007` | `L5` | `cross-session` | [`docs/adrs/ADR-0007-L5-vertical-mcp-apps-and-code-mode.md`](adrs/ADR-0007-L5-vertical-mcp-apps-and-code-mode.md) | `9,676` | `0d464fa46f5f404af4381d31f68376a38a09dbbaba791fcf9a298b186b9d09b1` |
| `ADR-0008` | `L6` | `cross-session` | [`docs/adrs/ADR-0008-L6-durable-cloud-workflows-and-frameworks.md`](adrs/ADR-0008-L6-durable-cloud-workflows-and-frameworks.md) | `12,166` | `e18e59fb7e12444aa81ad764c84735d6969e85f6d1fe7be320dc0873dbd05740` |
| `ADR-0009` | `L7` | `sota-ecosystem` | [`docs/adrs/ADR-0009-L7-tri-layer-compounding-memory.md`](adrs/ADR-0009-L7-tri-layer-compounding-memory.md) | `12,599` | `6208a36ae3aefb10e10fbd0cec7c89f6dd516c608397a57d40edbe495908136c` |
| `ADR-0010` | `L8` | `best-practices` | [`docs/adrs/ADR-0010-L8-deterministic-security-and-fail-closed-gates.md`](adrs/ADR-0010-L8-deterministic-security-and-fail-closed-gates.md) | `13,796` | `0983d85ac7f565ada9a9f9d34fb51982362f79d2ad14bdf44a6aa8616a621cb4` |
| `ADR-0011` | `L9` | `sota-ecosystem` | [`docs/adrs/ADR-0011-L9-adversarial-evals-and-trace-optimization.md`](adrs/ADR-0011-L9-adversarial-evals-and-trace-optimization.md) | `12,439` | `a34d6a140bbb9ed06efb65e25d78c8effb207a233d6be9eb67bd4ec94d0d8d89` |
| `ADR-0012` | `L10` | `best-practices` | [`docs/adrs/ADR-0012-L10-telemetry-provenance-and-compounding-manifest.md`](adrs/ADR-0012-L10-telemetry-provenance-and-compounding-manifest.md) | `13,264` | `7df038638e38ff98a9c6e36eed8e59924155482da2cb9b3d430c9a1819b4beb2` |

---

## 4. Verbatim 12-Step Unified Verification Evidence (`v3.0.0`)

Executed live via `bash scripts/check.sh` from the repository root on `2026-11-26`:

```text
=== [1/12] python3 scripts/verify_manifest.py --verify (Run 1 & Run 2 identical) ===
Manifest  : <repo-root>/manifest/compounding_manifest.v2.json
Schema    : <repo-root>/manifest/compounding_manifest.v2.schema.json
Repo Root : <repo-root>
[01][PASS] schema_draft_2020_12: https://json-schema.org/draft/2020-12/schema
[02][PASS] schema_validation: 0 errors
[03][PASS] disjoint_L0_L10_layers: 11 unique layers L0-L10, 38 exclusive domains, 0 overlaps
[04][PASS] zero_retiring_nov30_models_active: 0 retiring Nov 30, 2026 models in active slots (dot/hyphen/underscore normalized)
[05][PASS] zero_unpinned_placeholders: 0 TBD/TODO/FIXME/XXX/PLACEHOLDER/latest tokens across entire manifest
[06][PASS] cross_session_9_routes_complete: All 9 canonical cross-session routes present uniquely
[07][PASS] compounding_7_stages_and_ratchets: 7 stages (1..7), promotion gates (T1>=70/0 HIGH+CRIT, T3>=0.50/lift>=0.05), ratchets (24KB/20k/<=3 eager/delete-to-add)
[08][PASS] security_and_sandbox_invariants: OS sandbox required (Linux namespaces/macOS Seatbelt/Win AppContainer), Deny>Ask>Allow, resolved deny paths, fail-closed hooks, host-verified facts, zero secrets
[09][PASS] agy_5_surfaces_7_extensions: 5 AGY products, 7 IDE extensions, `agy acp`, standalone IDE enterprise_supported=false
[10][PASS] sha256_integrity_seal: verified (100991 canonical bytes) sha256=642ed427ab0eed77a382dd9fc4c9575fb4942310bffe075e4883722501ad8afc
[11][PASS] adr_12_bounded_bijection_and_madr4: 12/12 bounded MADR 4.0.0 ADRs (ADR-0001 META + ADR-0002..0012 <-> L0..L10), frontmatter & 9 headings verified
[12][PASS] adr_files_sha256_parity: 12/12 ADR markdown files verified byte-for-byte SHA-256 parity
[13][PASS] clean_install_registry_coverage: 11/11 layers (L0-L10) covered across 63 pinned clean-install upstream entries (0 unpinned/latest)
[14][PASS] saturation_proof_invariants: saturation_status='saturated', zero_self_invention_verified=true, 0 contradictions, 0 unverified claims, 12/12 ADRs, 11/11 layers, 0 overlaps
[15][PASS] repo_hygiene_and_anti_bloat_ratchet: AGENTS.md (11L/1501c), 1 skill(s) <=1024c, 1 rule(s) snake_case <=24KB, .agents/hooks.json valid, 0 tilde deny rules
[16][PASS] upstream_registry_and_map_parity: UPSTREAM.md 63/63 manifest winners (SPDX + HTTPS verified); upstream-map.toml 5/5 runtime .py adapters exact 1:1 bijection
[17][PASS] repo_scaffolding_and_portal_integrity: 11/11 repo scaffolding files present, scripts/check.sh executable, .gitleaks.toml valid, orca.yaml clean (no defaultTabs), zensical.toml 23/23 nav docs verified
CHECKS    : 17/17 passed
RESULT    : VERIFIED PASS

=== [2/12] python3 -m unittest discover -s tests -v ===
Ran 38 tests — OK (12 hook/handoff + 10 live host-shim contract + 16 manifest/14-mutation/scorecard, 0 skipped)

=== [3/12] python3 scripts/audit_ecosystem_hygiene.py --json --strict ===
schema_version: 1.1.0 | status: PASS | HIGH=0, MEDIUM=0, LOW=0 | total_findings=0 | secrets_accessed=false | global_charter: 6L/1,062c (~265 tok, html_comment_chars=0)

=== [4/12]–[9/12] AST, Static, Shell, Secret & Actions Security Gates ===
ast-grep scan && ast-grep scan --no-ignore hidden    -> exit 0 | 0 findings across 4 rule files / 6 rule IDs
ruff check . && ruff format --check .                -> All checks passed! (37 files already formatted)
ty check (ty 0.0.112)                                -> All checks passed!
shellcheck scripts/*.sh (shellcheck 0.11.0)          -> exit 0 | 0 findings
gitleaks detect --no-git --redact --source . && git  -> no leaks found (0 secrets)
zizmor --offline (zizmor 1.33.1)                     -> No findings to report. Good job!

=== [10/12]–[12/12] SkillEvaluator Tier 1, Syft SBOM + OSV-Scanner & Zensical Strict Portal ===
skillevaluator tier1 .agents/skills/sota-convergence-audit --no-llm -> exit 0 | 9 of 9 checks passed | Quality A 100.0/100 (100.0 across all 4 dims) | 0 HIGH/CRIT
syft dir:. (1.57.2) + osv-scanner scan source -L (2.7.1)            -> CycloneDX 1.7 SBOM | No issues found (0 CVEs)
zensical build --clean --strict (0.1.3)                             -> 0 errors | 24 HTML pages generated (index, 404, 9 guides, ADR CATALOG, 12/12 ADRs)
```

---

## 5. Drift-Free Maintenance Commands

```bash
# Run the complete 12-step fail-closed verification harness (or `make check`)
bash scripts/check.sh

# Read-only CI verification (must pass 17/17 and exit 0)
python3 scripts/verify_manifest.py --verify

# Re-seal after authorized ADR or upstream pin updates (embeds 12 ADR hashes + root seal + verifies 17/17)
make seal
```
