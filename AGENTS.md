# AGY SOTA Convergence — Repository Charter

1. **Upstream-Only Thin Layer (`ADR-0001`):** Adopt pinned upstream tools (`docs/clean-install-registry.md`). Zero vendored forks, zero unpinned `latest`/`TBD` pins, zero global `pip install` (use `uv`, `mise`, `npm --save-exact`).
2. **Bounded 12-ADR & Sealed Manifest:** Core architecture is strictly `12` MADR 4.0.0 ADRs (`docs/adrs/ADR-0001` `META` + `ADR-0002`..`ADR-0012` <-> `L0`–`L10`). Any edit to `docs/adrs/*` or `manifest/compounding_manifest.v2.json` requires `python3 scripts/verify_manifest.py --seal` and double `--verify`.
3. **Anti-Bloat & Sunset Ratchets:** Keep `AGENTS.md <=45L / <=1,600c`, rules `<=24,000 B` (snake_case `trigger:`), skill descriptions `<=1,024c`, eager MCP tools `<=3`. Zero `2026-11-30` retiring models; zero MCP `SEP-2577` adoption.
4. **Fail-Closed Security:** Never touch `.env*`, `config.json`, `mcp_config.json`, `mcp_oauth_tokens.json`, `auth.json`, `~/Documents/upstream/`, or broker ports (`:4001`, `:7496`, `:8798`, `:8796`). `PreToolUse` hooks exit `0` with `{"decision":"deny"}` on faults; never use `~/` in AGY deny rules.
5. **Merge Gates (`bash scripts/check.sh`):**
   - `python3 scripts/verify_manifest.py --verify` (`17/17` PASS)
   - `python3 -m unittest discover -s tests -v` (`0` failures)
   - `ruff check . && ruff format --check . && ty check && shellcheck scripts/*.sh` (`0` errors)
   - `gitleaks detect --no-git --source . && zizmor --offline .github/workflows/`
