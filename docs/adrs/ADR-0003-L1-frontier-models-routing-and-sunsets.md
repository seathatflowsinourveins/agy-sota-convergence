---
id: ADR-0003
layer: L1
status: accepted
date: 2026-11-26
decision-makers: SOTA Convergence Swarm (Verified 2026-11-26)
consulted: [sota-ecosystem, cross-session, changelogs, best-practices]
informed: [verifier, coordinator]
---

# ADR-0003: Frontier Models, Thinking Effort Routing, Local Runtimes & Sunset Enforcement (`L1`)

## Context and Problem Statement

Layer `L1` governs foundation model selection, reasoning-effort budgeting, dual-model planning/execution routing, on-device/local inference fallback, and active sunset enforcement across all Google Antigravity (AGY) surfaces and programmatic pipelines.

As of November 26, 2026, two urgent operational risks demand an explicit, enforceable decision:

1. **Imminent Model Removals (`2026-11-30`):** Per live `https://antigravity.google/docs/models.md`, four hosted model families are scheduled for permanent removal in four days (`Gemini 4 Argon`, `Gemini 3.8 Flash`, `GPT-OSS-120b`, and `Claude Sonnet/Opus 4.6`). Any unpinned default or hardcoded legacy slug in CLI scripts, `settings.json` `"orchestrator"` configs, CI workflows, or SDK pipelines will suffer hard outages on November 30, 2026.
2. **Quota & Latency Burn from Static Single-Model Pinning:** Running maximum-reasoning models (`Extra` / `xhigh` or flagship long-horizon models) for every routine edit, formatting pass, or high-fan-out subagent check wastes 5-hour/weekly quota windows and degrades interactive latency, while conversely relying on ad-hoc custom LLM proxy routers duplicates AGY's native `Orchestrator` and effort-tier controls and risks violating consumer OAuth Terms of Service.

How should `L1` standardize model selection, multi-tier reasoning routing, local/offline execution, and deterministic sunset hygiene with zero custom router self-invention?

## Decision Drivers

- **Zero Outage Across the `2026-11-30` Model Sunset:** Eliminate all active dependencies on retiring slugs (`Gemini 4 Argon`, `Gemini 3.8 Flash`, `GPT-OSS-120b`, `Claude 4.6`) and block re-introduction via CI/manifest regex gates.
- **Cost, Latency & Context-Window Optimization:** Pair frontier planning depth (up to 512K context on Gemini 4 Neon, deep long-horizon reasoning on Gemini 4 Carbon) with fast execution (`Gemini 4 Hydrogen`) and explicit thinking effort budgets (`low`, `medium`, `high`, `xhigh`).
- **Native-First Routing & Zero Custom Proxy Glue:** Adopt AGY's built-in `Orchestrator` and SDK `ModelTarget` / `LiteRTAgentConfig` / `LocalOpenAIAgentConfig` rather than writing bespoke prompt-routing middleware.
- **Compliance & Billing Boundary Integrity:** Respect plan entitlements (Free/Plus vs. Paid Pro/Ultra vs. Gemini Enterprise / GCP Pay As You Go) and never wrap consumer OAuth sessions inside unauthorized third-party routers.
- **Air-Gapped & Reproducible Local Inference:** Support deterministic, keyless on-device execution (LiteRT-LM + Gemma 4 26B A4B or local OpenAI-compatible servers) for privacy-sensitive or offline SDK workloads.

## Considered Options

1. **Option 1 (Chosen): Native AGY Post-Nov-30 Frontier Lineup + Native `Orchestrator` + Explicit Effort Tiers + SDK `LiteRTAgentConfig` / `LocalOpenAIAgentConfig` (with Automated Sunset Gate).**
2. **Option 2 (Rejected): Custom Multi-Provider Proxy / Self-Invented Routing Middleware (e.g., bespoke LiteLLM-style wrapper or custom classifier routing across arbitrary hosted APIs).**
3. **Option 3 (Rejected): Static Single-Model Pinning or Retaining Legacy Pre-Nov-30 Defaults (e.g., pinning unverified defaults or leaving retiring Gemini 3.8 / Argon / Claude 4.6 / GPT-OSS-120b slugs in scripts).**
4. **Option 4 (Rejected): Local-Only Execution Everywhere (dropping hosted frontier models in favor of on-device LiteRT/Ollama exclusively).**

## Decision Outcome

Chosen option: **Option 1 — Native AGY Post-Nov-30 Frontier Lineup + Native `Orchestrator` + Explicit Effort Tiers + SDK Local Runtimes**, because it maximizes reasoning quality per quota unit using zero-glue native AGY primitives while deterministically guaranteeing zero `2026-11-30` sunset breakage and preserving an official offline/local escape hatch in Python SDK pipelines.

Canonical active `L1` model slots (strictly post-Nov-30 compliant):

| Slot / Role | Canonical Active Selection | Effort / Config Default | Plan / Surface Scope |
| :--- | :--- | :--- | :--- |
| **Interactive Paid Default** | `gemini-4-neon` (up to 512K context) | `medium` (default) / `high` / `xhigh` (`Extra`) | Paid Google AI Pro, Ultra, Gemini Enterprise (App, CLI, IDE, Extensions) |
| **Long-Horizon Frontier SWE / Science / Security** | `gemini-4-carbon` | `high` (or `medium`) | Paid Pro, Ultra, Gemini Enterprise |
| **Fast Everyday Executor / Free & SDK Default** | `gemini-4-hydrogen` | `medium` / `high` (`low` for high-fan-out checks, `xhigh` when needed) | All plans (Free, Plus, Pro, Ultra, Enterprise) & SDK `0.1.24` default |
| **Dual-Model Interactive Routing** | Native **`Orchestrator`** (`Gemini 4 Neon` or `Carbon` Planner + `Gemini 4 Hydrogen` Executor) | `high` default (`App v2.35.0` / `CLI v1.5.15+`; Enterprise locked to Carbon High + Hydrogen High) | Paid Pro, Ultra, Gemini Enterprise |
| **Hosted Cross-Model Verifier / Peer** | `claude-opus-5-5` / `claude-sonnet-5-5` (thinking) | `medium` / `high` | Paid Pro (non-trial), Ultra, Enterprise (if enabled on GCP project) |
| **Local / Air-Gapped SDK Runtime** | `LiteRTAgentConfig` (`litert-lm==0.20.0`, e.g., Gemma 4 26B A4B) or `LocalOpenAIAgentConfig` (Ollama/LM Studio/vLLM) | Auto-lightweight presets + KV prefix caching (`SDK 0.1.24`) | Local Python SDK (`google-antigravity==0.1.24`) |
| **Explicitly Banned Active Slots (`2026-11-30` Sunset)** | **None allowed:** `gemini-4-argon`, `gemini-3.8-flash`, `gpt-oss-120b`, `claude-sonnet-4-6`, `claude-opus-4-6` | Hard CI & manifest verification fail (`exit 1`) | All surfaces, scripts, manifests, and CI workflows |

### Consequences

- **Good:** Eliminates `2026-11-30` hard breakage across interactive sessions, headless `agy -p` jobs, and SDK scripts; captures native dual-model cost/latency savings via `Orchestrator` without maintaining routing code; enables cross-model adversarial review (Gemini 4 vs. Claude 5.5) under unified AGY auth; provides first-class offline vision + KV-cached inference via `LiteRTAgentConfig`.
- **Good:** Explicit model pinning in SDK `LocalAgentConfig(model="gemini-4-hydrogen")` immunizes automated pipelines against historical SDK default drift (`3.5 → 3.6 → 3.7 → 3.8 → gemini-4-hydrogen` across `v0.1.0`–`v0.1.24`).
- **Bad:** Paid frontier models (`Gemini 4 Neon`, `Carbon`, `Claude 5.5`) and `Orchestrator` are unavailable on Free/Plus tiers (Free accounts are bounded to `Gemini 4 Hydrogen` post-Nov-30), and Gemini Enterprise restricts `Orchestrator` to Carbon (High) + Hydrogen (High).
- **Bad:** AGY's hosted roster does not include commercial OpenAI GPT/o-series models (only retiring open-weights `GPT-OSS-120b`); workflows requiring commercial OpenAI models must run at `L6` via `openai-agents` or locally via `LocalOpenAIAgentConfig`.
- **Neutral:** Enterprise-only legacy Gemini 3 models (`Gemini 3.7 Flash`, `3.6 Flash`, `3.1 Pro`) remain accessible solely for legacy Enterprise compatibility and are excluded from greenfield active slots.

### Confirmation

Run the following executable fitness checks from the repository root (every command must exit `0`):

```bash
# 1. Confirm live AGY CLI exposes post-Nov-30 Gemini 4 & Claude 5.5 targets
agy models | grep -E "gemini-4-(neon|carbon|hydrogen)|claude-(opus|sonnet)-5-5"

# 2. Enforce zero retiring Nov-30 model slugs across repo customizations & workflows
! rg -i '(gemini[-_ ]?4[-_ ]?argon|gemini[-_ ]?3[._-]8|gpt[-_ ]?oss[-_ ]?120b|claude[-_ ]?(sonnet|opus)?[-_ ]?4[._-]6)' \
  .agents/ .github/ 2>/dev/null

# 3. Verify host non-secret ecosystem hygiene (including zero Nov-30 model refs in user skills/rules)
python3 scripts/audit_ecosystem_hygiene.py --json >/dev/null

# 4. Run sealed 17-gate Compounding Manifest verifier (enforces RETIRING_NOV30_RE across all active slots)
python3 scripts/verify_manifest.py --verify
```

## Pros and Cons of the Options

### Option 1: Native AGY Post-Nov-30 Frontier Lineup + Native `Orchestrator` + SDK Local Runtimes

- **Pro:** Zero custom routing code (passes the 5-Question Zero-Self-Invention Gate cleanly: upstream feature exists natively, 0 wrapper LOC, exact version/model pins, clean install, removes legacy pins).
- **Pro:** Native thinking-effort budgeting (`low`/`medium`/`high`/`xhigh`), mid-turn model switching (`App v2.35.2`), and SDK `RetryConfig` / `Retry-After` handling out of the box.
- **Pro:** Seamless headless billing via `modelProvider: "gemini"` + `GEMINI_API_KEY` or `vertex=True` / GCP Pay As You Go without consumer OAuth ToS risk.
- **Con:** Bounded to AGY's hosted model roster on interactive surfaces unless routing through Enterprise custom LLM gateways or SDK local backends.

### Option 2: Custom Multi-Provider Proxy / Self-Invented Routing Middleware

- **Pro:** Arbitrary third-party commercial model mixing behind one self-hosted proxy.
- **Con (Disqualifying — Fails Zero-Self-Invention Gate):** Re-invents AGY's native `Orchestrator`, breaks prompt-cache locality and native thinking-level mappings (`ThinkingLevel.EXTRA_HIGH -> xhigh`), adds network latency and credential-handling attack surface, and risks violating consumer AGY Terms of Service if wrapping consumer OAuth sessions.

### Option 3: Static Single-Model Pinning or Unaudited Legacy Defaults

- **Pro:** Trivial one-line config.
- **Con (Disqualifying — Guaranteed Outage & Quota Waste):** Any unmigrated `gemini-4-argon`, `gemini-3.8-flash`, `gpt-oss-120b`, or `claude-4-6` pin breaks hard on `2026-11-30`; unpinned SDK scripts silently drift across minor releases (`0.1.8` → `0.1.24`); running a single max-effort frontier model for every step burns quota unnecessarily.

### Option 4: Local-Only Execution Everywhere (`LiteRT` / Ollama)

- **Pro:** Zero API spend and complete offline data locality.
- **Con (Disqualifying):** Even 26B on-device checkpoints (requiring `>=24 GB` VRAM/unified memory for Gemma 4 26B A4B) trail frontier 512K-context Gemini 4 Neon/Carbon and Claude 5.5 on complex multi-file architecture and long-horizon verification tasks.

## Clean Upstream Installation & Adapter Boundary

Aligned 1:1 with [`../clean-install-registry.md`](../clean-install-registry.md) (`L1`) and [`../../pyproject.toml`](../../pyproject.toml):

- **Hosted Frontier Models & `Orchestrator`:** Zero separate installation; authenticated through Antigravity App (`2.35.2`) or `agy` CLI (`1.5.18`). Select via `/model`, `--model gemini-4-neon-high`, or `--effort low|medium|high|xhigh`. For headless CI using API billing, set `"modelProvider": "gemini"` in `~/.gemini/antigravity-cli/settings.json` with host env `GEMINI_API_KEY` (never commit keys).
- **On-Device Local Models (Python SDK + LiteRT):**
  ```bash
  uv add google-antigravity==0.1.24
  uv add --group local-ml litert-lm==0.20.0
  uv run python -c "import litert_lm; from google.antigravity import LiteRTAgentConfig; print('ok')"
  ```
- **External Local OpenAI-Compatible Endpoints (Ollama / LM Studio / vLLM):**
  ```bash
  uv add google-antigravity==0.1.24
  uv run python -c "from google.antigravity import LocalOpenAIAgentConfig; print('ok')"
  ```
- **Thin Adapter Boundary:** Applications pass only declarative configuration (`model`, `thinking_level`, `LiteRTAgentConfig`, or `LocalOpenAIAgentConfig`). Custom HTTP retry loops, manual OpenAPI-to-OpenAI tool-schema rewriters, or custom classifier routers are explicitly forbidden because `google-antigravity==0.1.24` already provides JSON Schema normalization, `Retry-After` handling, vision translation, and KV prefix caching natively.

## More Information

- Live AGY Models & `2026-11-30` Sunset Notice: `https://antigravity.google/docs/models.md`
- Live AGY Plans & Quota Rules: `https://antigravity.google/docs/plans.md`
- Live AGY SDK Local Models (`LiteRTAgentConfig`, `LocalOpenAIAgentConfig`): `https://antigravity.google/docs/sdk/local-models.md`
- Live AGY Changelog (Gemini 4 launches & SDK `0.1.24`): `https://antigravity.google/docs/changelog.md`
- PyPI `google-antigravity==0.1.24`: `https://pypi.org/project/google-antigravity/0.1.24/`
- PyPI `litert-lm==0.20.0`: `https://pypi.org/project/litert-lm/0.20.0/`
- Repository Cross-References: [`../clean-install-registry.md`](../clean-install-registry.md), [`../convergence-stack.md`](../convergence-stack.md), [`../manifest-guide.md`](../manifest-guide.md).
