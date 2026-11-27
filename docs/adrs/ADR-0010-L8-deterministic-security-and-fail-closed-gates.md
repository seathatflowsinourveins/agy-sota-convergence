---
id: ADR-0010
layer: L8
status: accepted
date: 2026-11-26
decision-makers: SOTA Convergence Swarm (Verified 2026-11-26)
consulted: [sota-ecosystem, cross-session, changelogs, best-practices]
informed: [verifier, coordinator]
---

# ADR-0010: Deterministic Security, Permissions, and Fail-Closed Policy Gates (Layer L8)

## Context and Problem Statement

Autonomous coding agents execute shell commands, read and write repository files, invoke remote MCP tools, and actuate browser sessions across multi-surface Google Antigravity (AGY) workflows (`App v2.35.2`, `agy CLI v1.5.18`, `IDE v2.8.0`, 7 IDE Extensions, and `google-antigravity SDK 0.1.24`). Prompt-level Markdown instructions (`AGENTS.md`, `.agents/rules/*.md`) are probabilistic model guidance and cannot guarantee enforcement against prompt injection, shell metacharacter chaining, secret exfiltration, or credential-bearing browser sessions. Furthermore, Antigravity's native hook runtime fails open when a hook process exits with a non-zero exit code (logging the error and allowing execution to proceed).

How must Layer `L8` enforce least-privilege access, deterministic tool gating, browser actuation isolation, secret hygiene, and enterprise IAM/network perimeters strictly without duplicating `L0` OS/microVM sandboxes or inventing custom policy engines?

## Decision Drivers

- **Zero Probabilistic Security Boundaries:** Security invariants (`Deny > Ask > Allow`, secret path blocking, destructive command refusal) MUST be enforced mechanically outside the LLM context window.
- **Fail-Closed Hook Semantics:** Compensate deterministically for AGY's fail-open non-zero hook exit behavior so malformed JSON, timeouts, or unhandled exceptions block execution rather than silently allowing it.
- **Host-Verified Ground Truth:** Approval dialogs and policy evaluators MUST rely exclusively on host-verified runtime facts (parsed command line, canonical resolved path, Git diff, origin/redirect chain, MIME type), never model-generated summaries.
- **Disjoint Layer Separation (`L8` vs. `L0` / `L9` / `L10`):** `L8` exclusively owns `fine_grained_permission_policy_engine`, `fail_closed_deterministic_lifecycle_hooks`, `browser_actuation_isolation_and_masking`, and `enterprise_iam_vpc_sc_and_secret_hygiene`. Kernel/microVM isolation belongs to `L0`; behavioral red-teaming belongs to `L9`; distributed telemetry and manifest sealing belong to `L10`.
- **Zero-Self-Invention Discipline:** Reuse AGY's native permission engine, hook protocol, built-in isolated browser, enterprise IAM/VPC-SC controls, and pinned upstream static security scanners (`ruff`, `ty`, `ast-grep-cli`, `zizmor`, `gitleaks`, `trivy`, `osv-scanner`, `shellcheck`, `syft`) rather than building custom proxies or custom regex secret engines.

## Considered Options

1. **Option 1 (Adopted): AGY Native Permission Engine (`Deny > Ask > Allow`) + Fail-Closed `PreToolUse` Hook Wrapper + Built-In Isolated Browser + Pinned Upstream Static Security Gates + Enterprise IAM/VPC-SC & CaMeL Separation**
2. **Option 2 (Rejected): Probabilistic Markdown Guardrails Only (`AGENTS.md` / `.agents/rules/*.md` Security Prose)**
3. **Option 3 (Rejected): Custom Proxy / Hand-Rolled RBAC & Secret-Scanning Middleware Wrapping AGY Tools**
4. **Option 4 (Rejected): Fail-Open Shell-Script Hooks + Unisolated Personal Chrome Browser with `Always Allow` JavaScript**

## Decision Outcome

Chosen option: **Option 1 — AGY Native Permission Engine + Fail-Closed `PreToolUse` Hook Wrapper + Built-In Isolated Browser + Pinned Upstream Static Security Gates + Enterprise IAM/VPC-SC & CaMeL Separation**, because it delivers non-probabilistic, defense-in-depth enforcement directly atop AGY's native primitives and industry-standard static scanners while maintaining a strict thin-adapter boundary and zero self-invention.

Specifically, Layer `L8` mandates:
1. **Standing Permission Baseline (`Deny > Ask > Allow`):** Configure explicit `Deny` rules using **resolved absolute paths** (never unexpanded `~/` since Antigravity does not expand `~` in permission or customization manifests): `command(rm -rf)`, `command(sudo)`, `command(regex:curl .*)`, `write_file(.git/)`, `read_file(/Users/<your-user>/.ssh)`, and `read_file(/Users/<your-user>/.aws)`. Rely on AGY's shell metacharacter exact-match defense (preventing prefix-allowlists from authorizing `&&`, `||`, `;`, `|`, backticks, or `$()` chains).
2. **Fail-Closed `PreToolUse` Lifecycle Hook Wrapper:** Every security `PreToolUse` hook MUST execute inside a catch-all exception trap that emits valid JSON `{"decision":"deny","reason":"..."}` and exits with code **`0`** on any violation, malformed stdin, or runtime failure (compensating for AGY failing open on non-zero hook exits). Validate hook decisions against all 6 live `hooks.md` values (`allow`, `deny`, `ask`, `force_ask`, `auto_approve`, `deny_unless_prior_grant`).
3. **Browser Actuation Isolation & Masking:** Default to AGY's **Built-in Isolated Browser** (`App v2.30.0+`: IdP/payment page blocking, cross-origin iframe masking, scrubbed network logs, per-port `localhost` isolation, explicit-only sensitive Google subdomains, prompt-gated file uploads & blob downloads, blocked executable/markup downloads). When Chrome `/browser` is required, keep JavaScript execution policy strictly at `Request Review` or `Disabled`.
4. **Least-Privilege Credentials, Plugin Accounts & Enterprise Perimeter:** Authenticate via OAuth 2.0 PKCE (CIMD/DCR), Google ADC (`AGY_ADC_AUTH=true` / `google_credentials`), or plugin `variables` prompts; never hardcode bearer tokens or read/commit `.env*`, `~/.gemini/config/config.json`, or `mcp_oauth_tokens.json`. Scope MCP servers via `enabledTools` allowlists, pin multi-account CLI invocations with `AGY_ACCOUNT=<account-name>` (inspected via `list_plugin_accounts`), never rely on `_meta.ui.visibility: ["app"]` to hide tools in `agy` CLI, and enforce Gemini Enterprise SSO, BYOID/Workforce Identity Federation, `admin_settings.json` MDM policies, and Google Cloud VPC-SC (`businessaicode.googleapis.com`, `aiplatform.googleapis.com`) + regional PSC endpoints. Apply CaMeL capability separation (`arXiv:2503.18813`) by ingesting untrusted external content inside read-only subagents lacking shell, write, or network tools.
5. **Pinned Static Security & Supply-Chain Gates:** Enforce deterministic CI and pre-commit checks using upstream pinned `ruff`, `ty`, `ast-grep-cli`, `zizmor`, `gitleaks`, `trivy`, `osv-scanner`, `shellcheck`, and `syft` (SBOM generation fed into vulnerability gates).

### Consequences

- **Good:** Eliminates prompt-injection bypass of security controls; closes AGY's fail-open hook trap deterministically; keeps credentials out of LLM context and Git history; maintains strict separation from `L0` OS sandboxing (Linux native kernel namespaces, macOS `sandbox-exec` Seatbelt SBPL, Windows 11 24H2+ AppContainer Process Security Environments).
- **Good:** Every rule graduated from Markdown prose into a `PreToolUse` hook or static scanner triggers **delete-to-add** removal of the redundant prose from `AGENTS.md`, shrinking token overhead.
- **Bad:** Adds minor per-tool-call latency (typically `<50 ms` for a local stdlib Python `PreToolUse` hook) and requires engineers to substitute explicit absolute home paths (no `~/`) in standing `Deny` rules.
- **Neutral:** Enterprise MDM (`admin_settings.json`) and VPC-SC apply to App, CLI, Extensions, and SDK, while standalone Antigravity IDE (`v2.8.0`) remains non-Enterprise (`enterprise_supported: false`).

### Confirmation

Execute the following deterministic fitness functions from the repository root (all commands MUST exit `0`):

```bash
# 1. Fail-closed PreToolUse hook self-test (malformed stdin + forbidden .env must return exit 0 + decision=deny)
printf '{invalid-json' | python3 .agents/scripts/pre_tool_fail_closed.py | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["decision"]=="deny", d'
printf '{"tool_name":"read_file","tool_input":{"path":".env.local"}}' | python3 .agents/scripts/pre_tool_fail_closed.py | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["decision"]=="deny", d'

# 2. Repo hook unit tests, static lint, type, GitHub Actions, and secret gates
python3 -m unittest tests/test_hooks_and_handoff.py -v
ruff check . && ruff format --check .
ty check
zizmor --offline .github/workflows/sota-convergence-gates.yml
gitleaks detect --no-git --redact --source .

# 3. Verify standing deny rules contain zero unexpanded tilde (~/) paths and all 15 manifest gates pass
python3 scripts/verify_manifest.py --verify
```

## Pros and Cons of the Options

### Option 1: AGY Native Permission Engine + Fail-Closed `PreToolUse` Hook Wrapper + Built-In Isolated Browser + Pinned Static Security Gates + Enterprise IAM/VPC-SC & CaMeL Separation

- **Good:** Zero custom policy engine to maintain; directly leverages AGY's host-verified approval facts, shell metacharacter parser, built-in browser masking, and enterprise IAM/VPC-SC.
- **Good:** Passes all 5 Zero-Self-Invention falsification checks: upstream primitives exist natively, the fail-closed hook wrapper stays a thin declarative adapter (`<150` LOC stdlib Python), all scanners are version-pinned, zero upstream forks are required, and prose rules are deleted on escalation.
- **Bad:** Requires maintaining pinned versions across 9 upstream static security CLIs in `mise.toml` and `pyproject.toml`.

### Option 2: Probabilistic Markdown Guardrails Only (`AGENTS.md` / `.agents/rules/*.md`)

- **Good:** Zero setup friction and zero tool-call latency.
- **Bad:** Trivially defeated by indirect prompt injection in repository files, MCP responses, or web pages; ETH Zurich (`arXiv:2602.11988`) also showed verbose context prose inflates token costs by `>20%` without reliable compliance. **Rejected.**

### Option 3: Custom Proxy / Hand-Rolled RBAC & Secret-Scanning Middleware

- **Good:** Full control over bespoke policy syntax.
- **Bad:** Fails the **Zero-Self-Invention falsification gate** on every axis: duplicates AGY's native permission engine, duplicates `gitleaks`/`trivy`/`osv-scanner`/`ast-grep`, introduces maintenance drift on every AGY tool-schema release, and widens the trusted computing base. **Rejected.**

### Option 4: Fail-Open Shell-Script Hooks + Unisolated Personal Chrome with `Always Allow` JavaScript

- **Good:** Quick ad-hoc bash snippets and access to existing logged-in browser tabs.
- **Bad:** Any `jq` parse error or bash crash exits non-zero, causing AGY to fail open and permit blocked commands; unisolated personal Chrome exposes authenticated IdP/banking/cloud cookies to indirect web prompt injection. **Rejected.**

## Clean Upstream Installation & Adapter Boundary

All versions below are verified live against PyPI JSON API and GitHub Releases API on `2026-11-26` (zero global `pip` pollution; zero unpinned `curl | sh` installers):

| Component | Channel | Verified Pin (`2026-11-26`) | Clean Pinned Install Command | Post-Install Verify Command |
| :--- | :--- | :--- | :--- | :--- |
| AGY Permissions, Hooks & Built-In Isolated Browser | Bundled in AGY App / CLI | App `2.35.2` / CLI `1.5.18` | Bundled natively (zero extra install) | `agy --version` |
| `ruff` | PyPI (`uv tool`) | `0.17.6` | `uv tool install ruff==0.17.6` | `ruff --version` |
| `ty` | PyPI (`uv tool`) | `0.0.112` | `uv tool install ty==0.0.112` | `ty --version` |
| `ast-grep-cli` | PyPI (`uv tool`) | `0.51.3` | `uv tool install ast-grep-cli==0.51.3` | `ast-grep --version` |
| `zizmor` | PyPI (`uv tool`) | `1.33.1` | `uv tool install zizmor==1.33.1` | `zizmor --version` |
| `gitleaks` | GitHub Release (`mise`) | `v8.30.1` | `mise use gitleaks@8.30.1` | `gitleaks version` |
| `trivy` | GitHub Release (`mise`) | `v0.76.2` | `mise use trivy@0.76.2` | `trivy --version` |
| `osv-scanner` | GitHub Release (`mise`) | `v2.7.1` | `mise use osv-scanner@2.7.1` | `osv-scanner --version` |
| `shellcheck` | GitHub Release (`mise`) | `v0.11.0` | `mise use shellcheck@0.11.0` | `shellcheck --version` |
| `syft` | GitHub Release (`mise`) | `v1.57.2` | `mise use syft@1.57.2` | `syft version` |

**Thin-Adapter Boundary:** Custom code in `L8` is strictly restricted to declarative JSON permission/hook manifests (`.agents/hooks.json`, `.agents/templates/permissions.baseline.json`, `admin_settings.json`, `ast-grep` YAML rules) and minimal stdlib-only fail-closed `PreToolUse` / `Stop` Python adapters (`.agents/scripts/pre_tool_fail_closed.py`, `<=150` LOC) that map stdin tool payloads to AGY's documented `{"decision":"deny"}` schema. Never re-implement secret regex engines, vulnerability databases, SBOM parsers, or browser sandboxes.

## More Information

- Antigravity Permissions Specification: https://antigravity.google/docs/permissions.md
- Antigravity Lifecycle Hooks Specification: https://antigravity.google/docs/hooks.md
- Antigravity OS Sandbox Specification (`L0` boundary reference): https://antigravity.google/docs/sandbox.md
- Antigravity Browser Security & Isolation: https://antigravity.google/docs/browser.md and https://antigravity.google/docs/ide/browser.md
- Antigravity Enterprise IAM, MDM & VPC-SC: https://antigravity.google/docs/enterprise.md
- CaMeL Capability Separation (`arXiv:2503.18813`): https://arxiv.org/abs/2503.18813
- Upstream Static Security Tools: https://docs.astral.sh/ruff/, https://docs.astral.sh/ty/, https://ast-grep.github.io/, https://docs.zizmor.sh/, https://github.com/gitleaks/gitleaks, https://trivy.dev/, https://google.github.io/osv-scanner/, https://www.shellcheck.net/, https://github.com/anchore/syft
- Repository Cross-References: [Convergence Stack](../convergence-stack.md), [Clean Install Registry](../clean-install-registry.md), [Manifest Guide](../manifest-guide.md)
