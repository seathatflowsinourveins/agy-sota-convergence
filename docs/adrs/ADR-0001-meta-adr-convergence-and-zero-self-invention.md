---
id: ADR-0001
layer: META
status: accepted
date: 2026-11-26
decision-makers: SOTA Convergence Swarm (Verified 2026-11-26)
consulted: [sota-ecosystem, cross-session, changelogs, best-practices]
informed: [verifier, coordinator]
---

# ADR-0001: Bounded 12-ADR MADR 4.0.0 Governance, Zero-Self-Invention Gate & Cryptographic Convergence Manifest

## Context and Problem Statement

AI-native software engineering platforms (such as Google Antigravity spanning App 2.0, CLI, IDE, 7 IDE extensions, and Python SDK) evolve at weekly cadence alongside rapid open-protocol shifts (MCP `2026-07-28`, A2A v1.0, ACP v2 Preview, AAIF Agent Skills). Without a machine-verifiable Architectural Knowledge Management (AKM) system, engineering teams suffer three compounding pathologies: (1) **ADR sprawl and context rot** when hundreds of unindexed or contradictory records accumulate, (2) **custom self-invention drift** when engineers or agents hand-roll duplicate orchestration loops, memory stores, or eval harnesses instead of adopting pinned upstream tools, and (3) **silent specification decay** when prose documentation drifts away from live packages, security gates, and sunset calendars (e.g., `2026-11-30` model removals). How should we govern architectural decisions, layer boundaries, upstream installation pins, and research saturation across all 11 layers (`L0`–`L10`)?

## Decision Drivers

* Enforce a strictly disjoint 11-layer convergence stack (`L0`–`L10`) with **zero functional overlap** and **zero unowned gaps**.
* Prevent ADR sprawl and token bloat (consistent with ETH Zurich `arXiv:2602.11988` minimal-context evidence and AGY's `20,000`-token aggregate rules budget).
* Mechanically enforce the **Upstream-Only, Native-First Thin Layer** doctrine via an unambiguous falsification gate rather than subjective prose guidelines.
* Convert architectural decisions from passive Markdown into **executable Evolutionary Architecture fitness functions** (MADR 4.0 confirmation checks) backed by cryptographic SHA-256 tamper detection.
* Keep ADRs first-class queryable for both human engineers (via static docs-as-code portal) and AI agents (via AST/hybrid-search MCP servers).

## Considered Options

* **Option 1 (Chosen): Bounded 12-ADR MADR 4.0.0 Set (`META` + 1:1 `L0`–`L10` Bijection) + 5-Question Zero-Self-Invention Gate + SHA-256 Sealed Convergence Manifest (`v3.0.0`) + Zensical / `codebase-memory-mcp` / `XERJ` Indexing.**
* **Option 2: Unbounded Per-Feature Nygard ADRs in Git without Manifest Sealing or Automated Fitness Gates.**
* **Option 3: Informal Wiki / Technical Design Docs / Chat Transcripts Only (No Formal ADR Log).**
* **Option 4: Custom Proprietary Governance Service / Database Portal Built In-House.**

## Decision Outcome

Chosen option: **"Option 1: Bounded 12-ADR MADR 4.0.0 Set (`META` + 1:1 `L0`–`L10` Bijection) + 5-Question Zero-Self-Invention Gate + SHA-256 Sealed Convergence Manifest (`v3.0.0`)"**, because it is the only option that pairs standardized MADR 4.0.0 human legibility with deterministic 17-gate cryptographic verification (`scripts/verify_manifest.py`), prevents ADR sprawl by capping core platform records at exactly 12 (`ADR-0001` `META` + `ADR-0002`..`ADR-0012` <-> `L0`..`L10`), and enforces zero-self-invention + zero-sunset drift automatically in CI.

### Consequences

* Good, because every architectural layer (`L0`–`L10`) has **exactly one** authoritative MADR 4.0.0 ADR whose byte-level SHA-256 digest is sealed inside `manifest/compounding_manifest.v2.json`, making silent drift or unauthorized edits fail CI immediately (`exit 1`).
* Good, because the **5-Question Zero-Self-Invention Falsification Gate** (Upstream Existence, Thin Declarative LOC Ratchet, Pin/Provenance, Clean-Install-Without-Fork, Delete-to-Add & Fitness Proof) eliminates subjective debates over custom glue vs. upstream adoption.
* Good, because `Zensical` (`0.1.3`), `codebase-memory-mcp` (`0.12.1` `manage_adr`), and `XERJ` (`v1.0.0-rc.105`) expose the exact same Markdown source files to both human browsers and AI agents without duplicating content.
* Bad, because every legitimate architectural update requires updating the corresponding ADR, syncing pinned versions/hashes, and running `--seal` + double `--verify` before merge.
* Neutral, because historical superseded rationale lives in Git commit history and prior manifest tags rather than multiplying active ADR files past `N = 12`.

### Confirmation

Compliance is verified deterministically via the stdlib-only 17-gate manifest verifier, bounded ADR inventory check, and Zensical portal validation from the repository root:

```bash
# 1. Run all 17 cryptographic, MADR 4.0.0 bijection, ADR SHA-256 parity, clean-install, saturation, hygiene, upstream parity & portal gates (twice)
python3 scripts/verify_manifest.py --verify && python3 scripts/verify_manifest.py --verify

# 2. Verify exact 12-file bounded ADR inventory (docs/adrs/ADR-0001..ADR-0012) and zensical.toml parse
python3 -c '
import pathlib, tomllib
adrs = sorted(p.name for p in pathlib.Path("docs/adrs").glob("ADR-*.md"))
assert len(adrs) == 12, f"Expected 12 ADRs, got {len(adrs)}: {adrs}"
cfg = tomllib.loads(pathlib.Path("zensical.toml").read_text(encoding="utf-8"))
assert "project" in cfg and "nav" in cfg["project"]
print("OK: 12 bounded ADRs & zensical.toml verified")
'

# 3. Verify static portal compiles cleanly when zensical==0.1.3 is provisioned
zensical --version && zensical build --strict
```

## Pros and Cons of the Options

### Option 1: Bounded 12-ADR MADR 4.0.0 Set + Zero-Self-Invention Gate + SHA-256 Sealed Manifest (`v3.0.0`)

* Good, because MADR 4.0.0 ([Sep 17, 2024](https://github.com/adr/madr/releases/tag/4.0.0)) natively supports machine-parseable YAML frontmatter (`status`, `date`, `decision-makers`, `consulted`, `informed`) and executable confirmation sections.
* Good, because capping the core convergence log at `12` records enforces a strict 1:1 bijection with `L0`–`L10`, eliminating multi-ADR ambiguity and context rot.
* Good, because passing the **5-Question Zero-Self-Invention Gate** is auditable: adopts upstream MADR 4.0.0, upstream `zensical==0.1.3`, upstream `codebase-memory-mcp==0.12.1`, and upstream `xerj` `v1.0.0-rc.105` with only a thin stdlib Python SHA-256 sealer/verifier.
* Bad, because cross-cutting changes touching multiple layers require coordinated updates across the affected layer ADRs and a fresh manifest seal.

### Option 2: Unbounded Per-Feature Nygard ADRs without Manifest Sealing

* Good, because individual PR authors can append new ADRs quickly without touching a central manifest.
* Bad, because unbounded ADR growth creates conflicting historical records that degrade agent retrieval precision and fail to catch silent drift against deprecated models (`2026-11-30`) or protocol sunsets (`SEP-2577`).
* Bad, because without executable confirmation gates and SHA-256 parity checks, ADRs decay into write-only shelfware.

### Option 3: Informal Wiki / Design Docs / Chat Logs Only

* Good, because zero upfront template discipline is required.
* Bad, because point-in-time design docs and external wikis live outside Git, go stale immediately after launch, cannot be cryptographically verified in CI, and leave AI agents repeating rejected architectural dead ends across sessions.

### Option 4: Custom In-House Governance Database & ADR Web Portal

* Good, because custom dashboards could offer bespoke workflows.
* Bad, because it fails **Q1 (Upstream Existence)**, **Q2 (LOC Ratchet)**, and **Q4 (Clean Install Without Fork)** of the Zero-Self-Invention Gate—re-inventing static docs publishing (`zensical`), Git-native MADR 4.0 files, and MCP ADR indexing (`codebase-memory-mcp` `manage_adr`).

## Clean Upstream Installation & Adapter Boundary

All governance, publishing, and agent-indexing tooling is installed strictly from pinned official upstream releases (zero vendoring, zero forks, zero global `pip install` pollution):

| Component | Exact Pinned Version (`2026-11-26`) | Official Clean Install Command | Post-Install Verify Command | Thin-Adapter Boundary |
| :--- | :--- | :--- | :--- | :--- |
| **Zensical** *(MADR 4.0 static portal)* | `0.1.3` (PyPI, `2026-11-20`) | `uv tool install "zensical==0.1.3"` | `zensical --version` | Declarative `zensical.toml` pointing at `docs/` and `docs/adrs/`; zero custom SSG plugins. |
| **codebase-memory-mcp** *(`manage_adr` + AST graph)* | `0.12.1` (PyPI / GitHub, `2026-10-16`) | `uv tool install "codebase-memory-mcp==0.12.1"` | `codebase-memory-mcp --version` | Mounted declaratively in `mcp_config.json`; zero custom AST/ADR server code. |
| **XERJ** *(hybrid ADR/docs search MCP)* | `v1.0.0-rc.105` (GitHub release) | `nix run github:xerj-org/xerj/v1.0.0-rc.105 -- --version` *(or download pinned `v1.0.0-rc.105` release tarball from `https://github.com/xerj-org/xerj/releases/tag/v1.0.0-rc.105`; interactive installer: `curl -fsSL https://xerj.org/get \| sh`)* | `xerj --version` | Declarative `xerj autoindex` + MCP config; zero custom search engine code. |
| **Manifest Sealer / Verifier** *(thin declarative fitness gate)* | Stdlib Python 3.12+ (zero third-party deps) | Checked directly into repository (`scripts/verify_manifest.py`) | `python3 scripts/verify_manifest.py --verify` | Thin stdlib SHA-256 + schema/bijection/hygiene validator only; zero duplicated runtime or framework logic. |

## More Information

* [MADR 4.0.0 Official Specification](https://adr.github.io/madr/) & [Release 4.0.0 (Sep 17, 2024)](https://github.com/adr/madr/releases/tag/4.0.0)
* [Michael Nygard — Documenting Architecture Decisions (Nov 15, 2011)](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
* [Thoughtworks Technology Radar — Lightweight ADRs](https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records) & [Fitness Function-Driven Development](https://www.thoughtworks.com/insights/articles/fitness-function-driven-development)
* [Zensical Docs Engine (`0.1.3`)](https://zensical.org/) | [codebase-memory-mcp (`0.12.1`)](https://github.com/DeusData/codebase-memory-mcp) | [XERJ (`v1.0.0-rc.105`)](https://github.com/xerj-org/xerj/releases/tag/v1.0.0-rc.105)
* Repository Guides: [`docs/adr-and-convergence-practice.md`](../adr-and-convergence-practice.md), [`docs/convergence-stack.md`](../convergence-stack.md), [`docs/clean-install-registry.md`](../clean-install-registry.md), [`docs/manifest-guide.md`](../manifest-guide.md)
