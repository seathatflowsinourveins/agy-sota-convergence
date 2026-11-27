## AGY SOTA Convergence Merge Checklist

- [ ] **Upstream-Only & Provenance Parity:** Any new dependency or runtime `.py` adapter passes the 5-Question Zero-Self-Invention Gate (`ADR-0001`), is pinned cleanly in `UPSTREAM.md` + `docs/clean-install-registry.md`, and maps 1:1 in `upstream-map.toml`.
- [ ] **Bounded 12-ADR & Sealed Manifest:** Core ADRs remain strictly bounded at `12` (`ADR-0001`..`ADR-0012`); any ADR or manifest edit was re-sealed with `make seal` and synced in `docs/manifest-guide.md`.
- [ ] **Full 13-Step Verification Gate:** `bash scripts/check.sh` passes `13/13` (`18/18` double `--verify`, `unittest` 0 failures, `ast-grep`, `ruff`, `ty`, `shellcheck`, `gitleaks`, `zizmor --offline .github/workflows/`, `skillevaluator` Grade `A` on `4/4` skills, `syft`->`osv-scanner`, strict `zensical` build, and `agy plugin validate --strict --json`).
- [ ] **GitHub Actions Supply-Chain Hygiene:** All workflow `uses:` references are pinned to 40-char commit SHAs, declare top-level `permissions: {}` + minimal job `permissions`, and run `step-security/harden-runner`.
- [ ] **Fail-Closed Security & Zero Leaks:** Zero secrets, zero live broker ports, zero `2026-11-30` retiring models, zero `~/` deny rules, and zero workstation home paths or temporary artifacts committed.
