---
id: ADR-0011
layer: L9
status: accepted
date: 2026-11-26
decision-makers: SOTA Convergence Swarm (Verified 2026-11-26)
consulted: [sota-ecosystem, cross-session, changelogs, best-practices]
informed: [verifier, coordinator]
---

# ADR-0011: L9 Adversarial Evaluation, Isolated Sandboxed Verification & Trace-to-Skill Optimization

## Context and Problem Statement

In 2025–2026, two empirical crises invalidated informal "vibe-checked" agent evaluations and unverified self-improvement loops. First, **benchmark contamination and reward hacking** undermined legacy evaluations: OpenAI deprecated **SWE-bench Verified** on **February 23, 2026** ([blog](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/)) over training-data leakage and broken test suites, audited **SWE-bench Pro** ([blog](https://openai.com/index/separating-signal-from-noise-coding-evaluations/)), and UC Berkeley's RDI ([blog](https://rdi.berkeley.edu/blog/trustworthy-benchmarks-cont/)) demonstrated frontier agents exploiting unhardened test harnesses via `git log` inspection, stack introspection, and `file://` leaks. Second, **SkillsBench** ([arXiv:2602.12670](https://arxiv.org/abs/2602.12670), Feb 13, 2026) proved that while curated skills lift pass rates by **+16.6 pp** (`33.9% -> 50.5%`), **unverified model self-generated skills average −1.3 pp** (regressing up to −11.3 pp). How should Layer `L9` gate every skill, plugin, prompt, and agent harness change in CI while safely closing the offline trace-to-skill optimization loop?

## Decision Drivers

* Eliminate unverified self-authored skill/rule regressions (`SkillsBench` −1.3 pp trap) via mandatory **A/B Skill Lift** and negative-trigger testing before promotion.
* Defend against **reward hacking** by running all behavioral evaluations inside isolated, ephemeral verifier containers where the evaluated agent cannot read or mutate test oracles or `git log`.
* Automate adversarial security red-teaming (prompt injection, jailbreaks, credential exfiltration, PII leaks) on every harness and skill PR.
* Enable cost-effective offline trace-to-skill and prompt optimization without weight fine-tuning or expensive gradient RL rollouts.
* Strictly uphold **Zero-Self-Invention** (`ADR-0001`) by adopting pinned open-source evaluation, red-teaming, and reflection frameworks rather than building custom eval runners.

## Considered Options

* **Option 1 (Chosen): Four-Pillar Isolated Eval & Trace-Optimization Stack — `skillevaluator` (Tiers 1–3) + `agy plugin validate --strict`, `inspect-ai` + `inspect-harbor` + `harbor` (isolated container verifiers), `promptfoo` (CI red-teaming), and `dspy` + `gepa` (offline trace-driven reflection re-gated by CI).**
* **Option 2: Public Leaderboard Reliance (Legacy SWE-bench Verified) + Manual "Vibe-Check" Spot Testing.**
* **Option 3: Unconstrained Autonomous Self-Editing Loops (Agents Directly Rewriting `SKILL.md` / `AGENTS.md` Using In-Container Self-Grading).**
* **Option 4: Custom In-House Python Evaluation Harness & LLM-Judge Script.**

## Decision Outcome

Chosen option: **"Option 1: Four-Pillar Isolated Eval & Trace-Optimization Stack"**, because it enforces end-to-end adversarial rigor across every artifact in the compounding flywheel (`docs/compounding-flywheel.md` Stage 4):
1. **Skill & Plugin CI Gate (`skillevaluator==1.2.1` + `agy plugin validate --strict`):**
   * **Tier 1 (Static, Security & Rubric):** Quality score `>= 70` with **`0` HIGH/CRITICAL** findings (SkillSpector + Gitleaks); all 9 rubric criteria `>= 7` when LLM-scored.
   * **Tier 2 (Deduplication & Trigger Collision Check):** `skillevaluator similarity-check` blocks semantic overlap across the skill collection before merge.
   * **Tier 3 (Sandboxed A/B Skill Lift via Harbor):** Runs Docker-isolated with-skill vs. baseline trials with `>=1` explicit negative trigger case (`"expected_skill": null`). Promotion requires **all 5 dimensions `>= 0.50`** (*Security, Correctness, Discoverability, Effectiveness, Efficiency*), **`skill_lift >= +0.05`**, and **`publication_status == "pass"`**.
2. **Frontier & Behavioral Isolated-Verifier Evals (`inspect-ai==0.3.292` + `inspect-harbor==1.0.0` + `harbor==0.27.0`):** Executes **Terminal-Bench 2.0**, **SWE-bench Pro Public V2** fresh-sandbox protocols, **OSWorld-Verified**, and custom containerized Harbor tasks under isolated verifier boundaries immune to `git log` / oracle tampering.
3. **CI Security Red-Teaming (`promptfoo@0.126.0`):** Runs automated prompt-injection, data-leakage, policy-bypass, and coding-agent SDK regression suites on every PR.
4. **Offline Trace-to-Skill Reflection (`dspy==3.5.0` + `gepa==0.1.4`):** Consumes failed Harbor/Tier-3 traces offline using **Genetic-Pareto (GEPA)** reflection ([arXiv:2507.19457](https://arxiv.org/abs/2507.19457), up to 35× fewer rollouts than GRPO RL) and ACE-style itemized deltas ([arXiv:2510.04618](https://arxiv.org/abs/2510.04618)); every candidate patch **must re-clear the exact same isolated CI gate** before human merge.

### Consequences

* Good, because every promoted skill is empirically proven to lift agent performance (`>= +0.05`) without triggering false-positive collisions or security vulnerabilities.
* Good, because fresh-sandbox Harbor/Inspect AI verifiers neutralize UC Berkeley RDI reward-hacking vectors (`git log`, stack introspection, verifier monkey-patching).
* Good, because retiring **SWE-bench Verified** eliminates false confidence from contaminated legacy benchmarks.
* Bad, because Tier 3 A/B Harbor runs (`cases × attempts × agents × 2 arms`) consume real LLM API spend and Docker/cloud container minutes, requiring cheap keyless Tier 1 gating on every commit and full Tier 3 / Harbor sweeps on promotion PRs or nightly schedules.
* Neutral, because LLM-judge scores exhibit run-to-run variance across models; comparisons must pin exact agent model, judge model, dataset cases, and `--n-attempts >= 3` (never treating `--max-cases 1` smoke runs as publication evidence).

### Confirmation

Execute repository unit/negative-guard tests, keyless SkillEvaluator Tier 1 gates, and pinned-version smoke checks for the `L9` stack from the repository root:

```bash
# 1. Verify repository adversarial hook & 12-mutation manifest suites pass with 0 failures
python3 -m unittest discover -s tests -v

# 2. Verify SkillEvaluator Tier 1 keyless gate on repo skills + Tier 2 similarity check
skillevaluator --version && \
skillevaluator validate .agents/skills --profile default --tiers 1 -r json,markdown,sarif -o reports && \
skillevaluator similarity-check .agents/skills

# 3. Verify Inspect AI, Harbor, Promptfoo, DSPy & GEPA pinned tooling availability
inspect --version && harbor --version && npx --no-install promptfoo --version && \
uv run python -c 'import inspect_ai, inspect_harbor, dspy, gepa; print("OK: L9 eval/opt stack ready")'
```

## Pros and Cons of the Options

### Option 1: Four-Pillar Isolated Eval & Trace-Optimization Stack (`skillevaluator` + `inspect-ai`/`harbor` + `promptfoo` + `dspy`/`gepa`)

* Good, because each upstream owns a cleanly disjoint evaluation responsibility (skill A/B lift & dedup, frontier containerized benchmarks, security red-teaming, offline trace reflection) with zero functional overlap.
* Good, because it passes all 5 questions of the **Zero-Self-Invention Gate** (`ADR-0001`): adopts pinned `skillevaluator==1.2.1`, `inspect-ai==0.3.292`, `inspect-harbor==1.0.0`, `harbor==0.27.0`, `promptfoo@0.126.0`, `dspy==3.5.0`, and `gepa==0.1.4` via declarative `evals.json` / `promptfooconfig.yaml` / Harbor task specs.
* Bad, because Tier 3 and Harbor cloud suites require explicit provider keys in the host CI environment (never inside `evals/config.yml` `runtime_env`).

### Option 2: Legacy SWE-bench Verified + Manual Vibe-Checks

* Good, because it has zero CI setup cost.
* Bad, because SWE-bench Verified was formally deprecated by OpenAI on Feb 23, 2026 due to contamination and broken tests, and vibe-checking misses silent skill trigger collisions, prompt injections, and multi-turn regressions.

### Option 3: Unconstrained Autonomous Self-Editing with In-Container Self-Grading

* Good, because it appears fully automated on paper.
* Bad, because **SkillsBench** (`arXiv:2602.12670`) proved unverified self-generated skills *degrade* performance (−1.3 pp average, up to −11.3 pp), while **UC Berkeley RDI** showed in-container grading is trivially reward-hacked by frontier coding models.

### Option 4: Custom In-House Python Evaluation & Red-Team Runner

* Good, because output JSON format can be customized freely.
* Bad, because it violates **Q1 (Upstream Existence)**, **Q2 (LOC Ratchet)**, and **Q4 (Clean Install Without Fork)** of `ADR-0001`, re-inventing Docker/cloud container orchestration (`harbor`), multi-agent eval telemetry (`inspect-ai`), skill security scanners (`skillevaluator`), and red-team attack libraries (`promptfoo`).

## Clean Upstream Installation & Adapter Boundary

Every `L9` tool is provisioned from exact pinned official releases (zero unpinned version specs, zero vendored forks; host API keys injected via CI secrets only—never committed to `evals/config.yml`):

| Eval / Optimization Capability | Exact Pinned Version (`2026-11-26`) | Official Clean Install Command | Post-Install Verify Command | Thin-Adapter Boundary |
| :--- | :--- | :--- | :--- | :--- |
| **Skill & Rule CI Gate** *(`skillevaluator`, NVIDIA)* | `1.2.1` (PyPI, `2026-11-25`) | `uv tool install --python 3.13 "skillevaluator[all]==1.2.1"` | `skillevaluator --version && skillevaluator health-check --tier 1` | Declarative `<skill-dir>/evals/EVAL.md`, `evals.json`, and `config.yml` fixtures; zero custom skill grader framework. |
| **Frontier Isolated Evals** *(`inspect-ai`, UK AISI)* | `0.3.292` (PyPI, `2026-11-23`) | `uv add --group eval "inspect-ai==0.3.292"` | `uv run inspect --version` | Declarative task/scorer definitions + Docker/K8s sandbox specs. |
| **Containerized Benchmark & Rollout Harness** *(`harbor` + `inspect-harbor`)* | `harbor==0.27.0` (`2026-11-21`); `inspect-harbor==1.0.0` (`2026-09-23`) | `uv tool install "harbor==0.27.0"` / `uv add --group eval "inspect-harbor==1.0.0"` | `harbor --version` / `uv run python -c "import inspect_harbor; print('ok')"` | Declarative Harbor task directories (`instruction.md`, `Dockerfile`, isolated `tests/`); zero custom container runner. |
| **CI Security Red-Teaming** *(`promptfoo`)* | `0.126.0` (npm) | `npm install --save-dev --save-exact "promptfoo@0.126.0"` | `npx --no-install promptfoo --version` | Declarative `promptfooconfig.yaml` attack & regression assertions; zero custom injection scanner. |
| **Offline Reflective Trace Optimizer** *(`dspy` + `gepa`)* | `dspy==3.5.0` (`2026-11-10`); `gepa==0.1.4` (`2026-07-15`) | `uv add --group eval "dspy==3.5.0" "gepa==0.1.4"` | `uv run python -c "import dspy, gepa; print(dspy.__version__)"` | Thin offline reflection script feeding traces -> candidate diff proposals -> mandatory CI re-gating. |

## More Information

* [UK AISI Inspect AI](https://inspect.aisi.org.uk/) | [Meridian Labs `inspect_harbor`](https://github.com/meridianlabs-ai/inspect_harbor) | [Harbor Framework](https://www.harborframework.com/) | [Terminal-Bench 2.0 (arXiv:2601.11868)](https://arxiv.org/abs/2601.11868)
* [NVIDIA SkillEvaluator (`1.2.1`)](https://github.com/NVIDIA/SkillEvaluator)
* [Promptfoo (`0.126.0`) — Joining OpenAI (Mar 9, 2026)](https://www.promptfoo.dev/blog/promptfoo-joining-openai/)
* [SkillsBench (arXiv:2602.12670, Feb 13, 2026)](https://arxiv.org/abs/2602.12670) | [Scale SWE-bench Pro Public V2](https://labs.scale.com/leaderboard/swe_bench_pro_public_v2) | [OSWorld-Verified (Jul 28, 2025)](https://xlang.ai/blog/osworld-verified)
* [OpenAI — Why We No Longer Evaluate SWE-bench Verified (Feb 23, 2026)](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/) | [UC Berkeley RDI — Trustworthy Benchmarks](https://rdi.berkeley.edu/blog/trustworthy-benchmarks-cont/)
* [DSPy + GEPA (arXiv:2507.19457, Jul 25, 2025)](https://arxiv.org/abs/2507.19457) | [gepa-ai/gepa](https://github.com/gepa-ai/gepa) | [ACE (arXiv:2510.04618, Oct 6, 2025)](https://arxiv.org/abs/2510.04618)
* Repository Guides: [`docs/compounding-flywheel.md`](../compounding-flywheel.md), [`docs/convergence-stack.md`](../convergence-stack.md), [`docs/clean-install-registry.md`](../clean-install-registry.md)
