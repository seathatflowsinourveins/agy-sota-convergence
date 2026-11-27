---
trigger: glob
globs: "docs/adrs/**,manifest/**,.agents/**"
---

# ADR, Manifest & Harness Governance Gates

1. **Bounded 12-ADR MADR 4.0.0 Bijection:** Keep exactly 12 accepted ADRs under `docs/adrs/` (`ADR-0001` `META` + `ADR-0002`..`ADR-0012` mapped 1:1 to `L0`–`L10`). Revise or supersede in place; never spawn `ADR-0013` or duplicate layer records. Every ADR must include all 7 YAML frontmatter keys (`id`, `layer`, `status`, `date`, `decision-makers`, `consulted`, `informed`) and all 9 ordered MADR 4.0 headings with executable repo-relative `### Confirmation` commands.
2. **Mandatory Re-Seal & 18-Gate Verification:** After any edit to `docs/adrs/**`, `manifest/**`, `UPSTREAM.md`, `upstream-map.toml`, `plugins/**`, `AGENTS.md`, or `.agents/**`, run `make sync-plugin` (if `.agents/` or `workflows/` changed) and `python3 scripts/verify_manifest.py --seal` (when ADR or manifest content changed) followed by `python3 scripts/verify_manifest.py --verify` (`18/18` `[PASS]`, `exit 0`) and `python3 -m unittest discover -s tests -v`.
3. **Zero Self-Invention & Anti-Bloat Ratchets:** Pass all 5 Zero-Self-Invention questions before adding code. Keep `AGENTS.md` `<=45` lines and `<=1,600` chars, every `.agents/skills/*/SKILL.md` description `<=1,024` chars, every `.agents/rules/*.md` file `<=24,000` bytes with snake_case `trigger:`, and apply delete-to-add whenever prose escalates to a hook or linter.
4. **Fail-Closed Security & Pin Hygiene:** Security `PreToolUse` hooks must exit `0` with `{"decision":"deny"}` on any fault. Use resolved absolute paths (never `read_file(~/` or `write_file(~/`) in standing deny rules. Never pin retiring `2026-11-30` models, MCP `SEP-2577` deprecated features, or unpinned floating version tags.
