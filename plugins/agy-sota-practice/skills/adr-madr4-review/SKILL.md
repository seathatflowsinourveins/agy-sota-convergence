---
name: adr-madr4-review
description: Use when authoring or reviewing bounded MADR 4.0.0 ADRs, disjoint layer ownership, or zero-self-invention boundaries. Do not use for routine code formatting or unrelated docs.
metadata:
  author: Antigravity SOTA Convergence Team <sota-convergence@antigravity.local>
  tags: [adr, madr4, architecture, governance, convergence]
---

# Bounded MADR 4.0.0 ADR Review Runbook

## Purpose

Author, review, and verify Architecture Decision Records strictly under the **MADR 4.0.0** specification, a bounded `1..12` record ceiling, strictly disjoint layer ownership (`L0`–`L10`), and the 5-Question Zero-Self-Invention Falsification Gate.

## Prerequisites

- Python `>= 3.12` for deterministic frontmatter, heading-order, and manifest verification.
- Optional `zensical==0.1.3` for strict static portal builds and `codebase-memory-mcp==0.12.1` for agent-native ADR indexing.
- Access to the repository's `docs/adrs/` (or `docs/adr/`) directory and governance manifest.

## Instructions

1. **Verify the bounded `1..12` ADR inventory and required 7-key YAML frontmatter (`id`, `layer`, `status`, `date`, `decision-makers`, `consulted`, `informed`):**
   ```bash
   python3 -c '
   from pathlib import Path
   adrs = sorted(Path("docs/adrs").glob("ADR-*.md"))
   assert 1 <= len(adrs) <= 12, f"Out-of-bounds ADR count: {len(adrs)}"
   print(f"ADR_COUNT_OK: {len(adrs)} bounded records")
   '
   ```
2. **Confirm all 9 ordered MADR 4.0.0 headings exist verbatim in every ADR:**
   - `## Context and Problem Statement`
   - `## Decision Drivers`
   - `## Considered Options` (`>= 3` concrete options with falsification evidence)
   - `## Decision Outcome`
   - `### Consequences`
   - `### Confirmation` (executable repo-relative CLI fitness checks)
   - `## Pros and Cons of the Options`
   - `## Clean Upstream Installation & Adapter Boundary`
   - `## More Information`
3. **Apply the 5-Question Zero-Self-Invention Gate before approving any new code:**
   - Q1 Upstream Existence (`>= 80%` solved by maintained upstream or native AGY primitive -> adopt, never duplicate).
   - Q2 Thin Declarative LOC Ratchet (zero custom loop, daemon, parser, or broker).
   - Q3 Pin & Provenance Clean (exact pinned version, SPDX license, `0` retiring models or `SEP-2577`).
   - Q4 Clean Install Without Fork (`uv`, `mise`, `npm --save-exact`, or official binary).
   - Q5 Delete-to-Add & Fitness Proof (bounded byte/token budgets plus executable CI check).
4. **Re-seal the repository manifest and validate the strict Zensical portal after authorized edits:**
   ```bash
   python3 scripts/verify_manifest.py --seal
   python3 scripts/verify_manifest.py --verify
   zensical build --clean --strict
   ```

## Examples

### Example 1: Re-sealing after revising an existing layer ADR in place

```bash
python3 scripts/verify_manifest.py --seal && python3 scripts/verify_manifest.py --verify
# Expected: 12/12 ADR SHA-256 parity PASS and VERIFIED PASS
```

### Example 2: Checking Zensical navigation parity

```bash
zensical build --clean --strict
# Expected: No issues found (exit 0)
```

## Limitations

- Never spawns `ADR-0013` for core convergence layers; revise or supersede the owning layer ADR in place and rely on Git history for historical decisions.
- Static structure validation does not verify upstream package release availability; verify live PyPI, npm, or GitHub release tags before pinning new versions.
- Requires human or coordinator sign-off before changing accepted architectural boundaries.

## Troubleshooting

| Symptom / Error | Root Cause | Resolution |
| :--- | :--- | :--- |
| `[11][FAIL] adr_12_bounded_bijection_and_madr4` | Missing frontmatter key, wrong heading order, or mismatched H1 prefix `# ADR-00XX:`. | Restore all 7 frontmatter keys and all 9 MADR 4.0.0 headings in exact order. |
| `[12][FAIL] adr_files_sha256_parity` | An ADR file changed without re-sealing the manifest. | Run `python3 scripts/verify_manifest.py --seal` and sync updated hashes in `docs/manifest-guide.md`. |
| `zensical build --strict` warns on a broken link | Relative link inside `docs/adrs/` points to a moved file. | Fix the relative path from `docs/adrs/` (`../guide.md`) and re-run `zensical build --clean --strict`. |
| Duplicate capability claimed across two ADRs | Layer boundary overlap between adjacent `L0`–`L10` layers. | Assign exclusive ownership to one layer and document only the wire contract in the neighbor ADR. |
