#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

echo "=== [1/13] Manifest Verification (18/18 gates, double determinism run) ==="
python3 scripts/verify_manifest.py --verify
python3 scripts/verify_manifest.py --verify

echo "=== [2/13] Stdlib Unittest Suite ==="
python3 -m unittest discover -s tests -v

echo "=== [3/13] Zero-Secret Ecosystem Hygiene Audit ==="
if [[ -n "${CI:-}" && ! -d "${HOME}/.agents" ]]; then
  python3 scripts/audit_ecosystem_hygiene.py --json >/dev/null
  echo "CI environment without \$HOME/.agents: ran non-strict schema check (PASS)"
else
  python3 scripts/audit_ecosystem_hygiene.py --json --strict >/dev/null
  echo "Host ecosystem hygiene audit: PASS (strict)"
fi

echo "=== [4/13] ast-grep Structural Ban Scan ==="
ast-grep scan
ast-grep scan --no-ignore hidden

echo "=== [5/13] Ruff Lint & Format Check ==="
ruff check .
ruff format --check .

echo "=== [6/13] ty Static Type Check ==="
ty check

echo "=== [7/13] ShellCheck Static Analysis ==="
shellcheck scripts/*.sh

echo "=== [8/13] Gitleaks Secret Scan ==="
gitleaks detect --no-git --redact --source .
if git rev-parse --verify HEAD >/dev/null 2>&1; then
  gitleaks git --redact .
fi

echo "=== [9/13] Zizmor GitHub Actions Security Audit ==="
zizmor --offline .github/workflows/

echo "=== [10/13] SkillEvaluator Tier 1 Keyless Gate (4/4 skills) ==="
for skill_dir in \
  .agents/skills/sota-convergence-audit \
  plugins/agy-sota-practice/skills/sota-practice-audit \
  plugins/agy-sota-practice/skills/adr-madr4-review \
  plugins/agy-sota-practice/skills/cross-session-handoff; do
  skillevaluator tier1 "$skill_dir" --no-llm --output-dir "$TMP_DIR/skilleval/$(basename "$skill_dir")"
done

echo "=== [11/13] Syft CycloneDX SBOM -> OSV-Scanner ==="
syft dir:. -o cyclonedx-json="$TMP_DIR/sbom.cdx.json"
osv-scanner scan source -L "$TMP_DIR/sbom.cdx.json"

echo "=== [12/13] Zensical Strict Portal Build ==="
zensical build --clean --strict

echo "=== [13/13] AGY Native Plugin Strict Validation ==="
if command -v agy >/dev/null 2>&1; then
  agy plugin validate --strict --json plugins/agy-sota-practice >/dev/null
  echo "agy plugin validate --strict: PASS (0 errors, 0 warnings)"
elif [[ -z "${CI:-}" ]]; then
  echo "[ERROR] agy binary missing on local workstation" >&2
  exit 1
else
  echo "CI runner without agy CLI: Gate [18] stdlib plugin contract verifier passed"
fi

echo "=== ALL 13 CHECKS PASSED ==="
