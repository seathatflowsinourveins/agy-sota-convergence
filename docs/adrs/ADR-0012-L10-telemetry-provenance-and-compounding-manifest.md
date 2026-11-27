---
id: ADR-0012
layer: L10
status: accepted
date: 2026-11-26
decision-makers: SOTA Convergence Swarm (Verified 2026-11-26)
consulted: [sota-ecosystem, cross-session, changelogs, best-practices]
informed: [verifier, coordinator]
---

# ADR-0012: Telemetry, Provenance, ADR Governance, and Cryptographic Compounding Manifest (Layer L10)

## Context and Problem Statement

Multi-agent engineering systems silently degrade over weeks unless architectural provenance, token/cost telemetry, deprecation cutoffs, and customization growth are governed mechanically. Empirical 2026 benchmarks show that unpruned context files inflate cost by `>20%` (`arXiv:2602.11988`), naive append-only updates cause context collapse (`arXiv:2510.04618`), unverified self-generated skills regress task success by `-1.3 pp` (`arXiv:2602.12670`), and local documentation silently drifts from live upstream releases (as demonstrated by 4 verified builtin doc drifts and imminent `2026-11-30` model retirements).

How must Layer `L10` standardize distributed agent telemetry, bounded MADR 4.0.0 architectural provenance, sunset/drift auditing, and tamper-evident compounding manifest sealing without duplicating `L8` security scanners or `L9` evaluation suites?

## Decision Drivers

- **Standards-Based Distributed Telemetry:** Emit vendor-neutral OpenTelemetry GenAI semantic spans (`invoke_agent`, `execute_tool`, `invoke_workflow`) with W3C `traceparent` propagation across AGY SDK, MCP `params._meta`, and cloud backends rather than proprietary logging schemas.
- **Two-Level Cryptographic Provenance Seal:** Bind every architectural decision (`docs/adrs/ADR-0001`..`ADR-0012`) and pinned upstream version into a Draft 2020-12 JSON manifest (`manifest/compounding_manifest.v2.json`) sealed with deterministic SHA-256 (`json-utf8-sort-keys-compact`) plus byte-for-byte SHA-256 parity across all 12 ADR markdown files.
- **Bounded Evolvable Governance & Anti-Bloat Ratchets:** Keep the ADR registry strictly bounded (`1 <= N <= 12`, `1` Meta-ADR + `11` layer ADRs bijected 1:1 to `L0`–`L10`), enforce hard customization budgets (`AGENTS.md <= 45` lines and `<= 1,600` chars, `24,000` B per rule file, `20,000` aggregate rule tokens, `<=1,024` char skill descriptions, `<=3` eager MCP tools), and apply a strict **delete-to-add** GC ratchet.
- **Zero-Dependency CI Verifiability:** The manifest sealer/verifier (`scripts/verify_manifest.py`) MUST run using Python 3 stdlib only so any developer laptop, container, or CI runner verifies all 15 gates deterministically without third-party package drift.
- **Disjoint Layer Separation (`L10` vs. `L7` / `L8` / `L9`):** `L10` exclusively owns `otel_genai_distributed_tracing`, `deprecation_and_doc_drift_governance`, and `cryptographic_manifest_sealing_and_gc_ratchets`. Memory storage belongs to `L7`, security/vulnerability enforcement belongs to `L8`, and behavioral evals/optimization belong to `L9`.

## Considered Options

1. **Option 1 (Adopted): OpenTelemetry GenAI Semantic Conventions + AGY Native SDK/CLI Observability + Bounded MADR 4.0.0 (`zensical` Portal) + Stdlib SHA-256 Compounding Manifest v2 (`15` CI Gates)**
2. **Option 2 (Rejected): Unsealed Wiki / Freeform Markdown Architecture Docs + Ad-Hoc JSON Log Files**
3. **Option 3 (Rejected): Proprietary Custom Telemetry SDK & Custom YAML Governance Framework**
4. **Option 4 (Rejected): Unbounded Append-Only ADR Directory Without Manifest Hashing or Delete-to-Add GC Ratchets**

## Decision Outcome

Chosen option: **Option 1 — OpenTelemetry GenAI Semantic Conventions + AGY Native SDK/CLI Observability + Bounded MADR 4.0.0 (`zensical` Portal) + Stdlib SHA-256 Compounding Manifest v2 (`15` CI Gates)**, because it unifies industry-standard tracing, live AGY cost/context telemetry, machine-checked ADR provenance, and tamper-evident anti-bloat governance with zero custom telemetry or portal reinvention.

Specifically, Layer `L10` mandates:
1. **OpenTelemetry GenAI Distributed Tracing:** Enable `google-antigravity` SDK (`0.1.24`, native OTel since `0.1.5`) tracing alongside `opentelemetry-sdk==1.45.2`, `opentelemetry-exporter-otlp==1.45.2`, and `opentelemetry-semantic-conventions==0.66b2`, adhering to `open-telemetry/semantic-conventions-genai` (`invoke_agent`, `execute_tool`, `invoke_workflow`, W3C `traceparent` in MCP `params._meta`). Pair with AGY CLI `/context` token-category grid, `/usage` quota monitor, App Project Customizations token breakdown, and Gemini Enterprise Google Cloud Audit logging.
2. **Bounded MADR 4.0.0 Architectural Provenance (`zensical` Portal):** Maintain exactly 12 accepted MADR 4.0.0 ADRs (`docs/adrs/ADR-0001` `META` + `docs/adrs/ADR-0002`..`ADR-0012` bijected 1:1 to `L0`–`L10`), rendered cleanly via upstream `zensical==0.1.3` (`zensical.toml`) when publishing a static documentation portal. When an architectural choice evolves, supersede or revise the owning layer ADR in-place rather than spawning unbounded duplicate ADRs.
3. **Cryptographically Sealed Compounding Convergence Manifest (`v2.1.0`):** Govern all pinned surfaces, disjoint `L0`–`L10` layers, 9 cross-session routes, 7 flywheel stages, sunset calendars, security invariants, 12/12 ADR file SHA-256 digests, clean-install registry pins, and saturation proof inside `manifest/compounding_manifest.v2.json`, validated against Draft 2020-12 `manifest/compounding_manifest.v2.schema.json` by stdlib-only `scripts/verify_manifest.py` across 15 deterministic gates (`--verify` exit `0` required in CI, including Gate `[15] repo_hygiene_and_anti_bloat_ratchet`).
4. **Sunset Watchlist & Anti-Bloat GC Ratchet:** Run scheduled audits against every `deprecations_and_sunsets.sunsets[].detection_pattern` (including the imminent `2026-11-30` retiring model cohort and the `2027-07-28` MCP `SEP-2577` window), run `scripts/audit_ecosystem_hygiene.py --json` for read-only non-secret host hygiene checks, reconcile local builtin doc drifts against live `https://antigravity.google/llms.txt` `.md` endpoints, and never raise token/byte/rule caps to accommodate bloat.

### Consequences

- **Good:** Single deterministic command (`python3 scripts/verify_manifest.py --verify`) proves schema validity, zero layer overlap, zero unpinned stub tokens, zero retiring model pins in active slots, 12/12 MADR 4.0 structural & SHA-256 integrity, 11/11 clean-install layer coverage, repo hygiene ratchets (`AGENTS.md`, skills, rules, hooks), and tamper-evident manifest root hash.
- **Good:** OpenTelemetry GenAI spans flow cleanly into any OTLP-compatible backend (Cloud Trace, Jaeger, Grafana Tempo, Phoenix, Langfuse OTLP) without vendor lock-in.
- **Bad:** Any authorized edit to an ADR file or upstream pin requires re-running `python3 scripts/verify_manifest.py --seal` and `--verify` before commit/merge; unsealed edits fail CI immediately by design.
- **Neutral:** `opentelemetry-semantic-conventions` remains in beta versioning (`0.66b2` on PyPI) as GenAI agent span conventions stabilize upstream, requiring explicit version pinning rather than unpinned ranges.

### Confirmation

Execute the following deterministic fitness functions from the repository root (all commands MUST exit `0`):

```bash
# 1. Verify all 15 cryptographic, schema, ADR MADR-4, clean-install, saturation, and repo hygiene gates (twice for determinism)
python3 scripts/verify_manifest.py --verify
python3 scripts/verify_manifest.py --verify

# 2. Execute full manifest + 12 adversarial mutation unit test suite
python3 -m unittest tests/test_manifest_v2.py -v

# 3. Run read-only zero-secret host ecosystem hygiene audit
python3 scripts/audit_ecosystem_hygiene.py --json

# 4. Validate Zensical portal TOML syntax (and build strictly when zensical CLI is installed)
python3 -c "import tomllib, pathlib; tomllib.loads(pathlib.Path('zensical.toml').read_text(encoding='utf-8')); print('ZENSICAL_TOML_OK')"
```

## Pros and Cons of the Options

### Option 1: OpenTelemetry GenAI + AGY Native Observability + Bounded MADR 4.0.0 (`zensical`) + Stdlib SHA-256 Manifest v2

- **Good:** Vendor-neutral tracing (`OTLP` + GenAI semconv), zero-dependency cryptographic verification (`Python 3` stdlib), strict MADR 4.0.0 compliance, and mechanical prevention of ADR sprawl, doc drift, and silent bloat.
- **Good:** Passes all 5 Zero-Self-Invention falsification checks: builds strictly on upstream OTel, MADR 4.0.0, Zensical, JSON Schema Draft 2020-12, and AGY SDK/CLI telemetry; `scripts/verify_manifest.py` is a pure declarative governance gate with zero duplicated runtime engine.
- **Bad:** Requires disciplined `--seal` execution whenever an ADR or upstream pin changes.

### Option 2: Unsealed Wiki / Freeform Markdown Architecture Docs + Ad-Hoc JSON Logs

- **Good:** Low upfront authoring effort.
- **Bad:** Architecture docs silently drift from installed versions within days; ad-hoc JSON logs lose trace correlation across subagents and MCP tool boundaries; zero CI enforcement against retiring models or unpinned stub tokens. **Rejected.**

### Option 3: Proprietary Custom Telemetry SDK & Custom YAML Governance Framework

- **Good:** Tailored field names for a single team.
- **Bad:** Fails the **Zero-Self-Invention falsification gate**: duplicates OpenTelemetry GenAI semantic conventions, duplicates JSON Schema Draft 2020-12, and duplicates Zensical/MADR 4.0.0 without improving capability. **Rejected.**

### Option 4: Unbounded Append-Only ADR Directory Without Manifest Hashing or GC Ratchets

- **Good:** Preserves every historical brainstorm file indefinitely.
- **Bad:** Causes ADR sprawl (`N >> 12`), contradicting active guidance, bloated retrieval indexes, and unverified drift between ADR prose and actual pinned dependencies. **Rejected.**

## Clean Upstream Installation & Adapter Boundary

All versions below are verified live against PyPI JSON API and GitHub Releases API on `2026-11-26` (isolated via `uv`; zero global `pip` pollution):

| Component | Channel | Verified Pin (`2026-11-26`) | Clean Pinned Install Command | Post-Install Verify Command |
| :--- | :--- | :--- | :--- | :--- |
| `google-antigravity` (native OTel since `0.1.5`) | PyPI (`uv`) | `0.1.24` | `uv add google-antigravity==0.1.24` | `uv run python -c "import google.antigravity as ag; print(ag.__name__)"` |
| `opentelemetry-sdk` | PyPI (`uv`) | `1.45.2` | `uv add opentelemetry-sdk==1.45.2` | `uv run python -c "import importlib.metadata as m; print(m.version('opentelemetry-sdk'))"` |
| `opentelemetry-exporter-otlp` | PyPI (`uv`) | `1.45.2` | `uv add opentelemetry-exporter-otlp==1.45.2` | `uv run python -c "import importlib.metadata as m; print(m.version('opentelemetry-exporter-otlp'))"` |
| `opentelemetry-semantic-conventions` | PyPI (`uv`) | `0.66b2` | `uv add opentelemetry-semantic-conventions==0.66b2` | `uv run python -c "import importlib.metadata as m; print(m.version('opentelemetry-semantic-conventions'))"` |
| `zensical` (MADR 4.0 ADR docs portal) | PyPI (`uv tool`) | `0.1.3` | `uv tool install zensical==0.1.3` | `zensical --version` |
| `MADR` Specification | GitHub Release (Spec) | `4.0.0` | Spec template (`https://adr.github.io/madr/`) | Enforced by `python3 scripts/verify_manifest.py --verify` |
| `scripts/verify_manifest.py` | Python 3 Stdlib | Python `3.12+` stdlib | Zero external install required | `python3 scripts/verify_manifest.py --verify` |

**Thin-Adapter Boundary:** Custom code in `L10` is strictly limited to declarative JSON Schema (`manifest/compounding_manifest.v2.schema.json`), declarative OTLP exporter configuration (`OTEL_EXPORTER_OTLP_ENDPOINT`), Zensical site config (`zensical.toml`), and the stdlib-only SHA-256 manifest/ADR seal verifier (`scripts/verify_manifest.py`). Never build custom trace collectors, custom span wire formats, or custom static-site generators.

## More Information

- OpenTelemetry GenAI Semantic Conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/ and https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/
- OpenTelemetry GenAI Conventions Repo: https://github.com/open-telemetry/semantic-conventions-genai
- OpenTelemetry Python Packages: https://pypi.org/project/opentelemetry-sdk/, https://pypi.org/project/opentelemetry-exporter-otlp/, https://pypi.org/project/opentelemetry-semantic-conventions/
- Google Antigravity Python SDK (`0.1.24`, native OTel): https://antigravity.google/docs/sdk/overview.md and https://pypi.org/project/google-antigravity/
- Antigravity Changelog & Live Docs Index: https://antigravity.google/docs/changelog.md and https://antigravity.google/llms.txt
- MADR 4.0.0 Specification: https://adr.github.io/madr/ and https://github.com/adr/madr/releases/tag/4.0.0
- Zensical Docs Portal: https://zensical.org/ and https://pypi.org/project/zensical/
- JSON Schema Draft 2020-12: https://json-schema.org/draft/2020-12/schema
- Empirical Anti-Bloat & Compounding Citations: https://arxiv.org/abs/2602.11988, https://arxiv.org/abs/2510.04618, https://arxiv.org/abs/2602.12670, https://every.to/guides/compound-engineering
- Repository Cross-References: [ADR & Convergence Practice](../adr-and-convergence-practice.md), [Compounding Flywheel](../compounding-flywheel.md), [Clean Install Registry](../clean-install-registry.md), [Manifest Guide](../manifest-guide.md)
