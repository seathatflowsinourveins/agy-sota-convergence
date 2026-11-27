---
trigger: glob
globs: "docs/adrs/**, docs/adr/**, .agents/**, plugins/**, .github/workflows/**, orca.yaml"
---

# Governance, Plugin & Supply-Chain File Guardrails

1. **Bounded MADR 4.0.0 ADRs:** Keep core platform ADRs bounded (`1..12` records) with all 7 YAML frontmatter keys (`id`, `layer`, `status`, `date`, `decision-makers`, `consulted`, `informed`) and all 9 ordered MADR 4.0 headings with executable repo-relative confirmation commands.
2. **Native AGY Plugin Hygiene:** Place plugin hooks strictly at `<plugin-root>/hooks.json` using relative `./scripts/*.py` (`0755`) commands and `"enabled": false` opt-in defaults; omit `hooks/hooks.json`, `commands/`, and always-on `rules/AGENTS.md`. Validate with `agy plugin validate --strict --json`.
3. **GitHub Actions Supply-Chain Controls:** Pin every external `uses:` target to an exact 40-char commit SHA, declare top-level `permissions: {}` with minimal job `permissions: { contents: read }`, include `step-security/harden-runner`, bind `${{ inputs.* }}` via `env:`, and verify `zizmor --offline .github/workflows/` returns `0` findings.
4. **Orca Worktree Safety:** Never declare `defaultTabs:` in `orca.yaml` and never commit secrets, live broker ports, or workstation home paths.
