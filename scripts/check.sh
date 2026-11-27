#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

echo "=== [1/12] Manifest Verification (double determinism run) ==="
python3 scripts/verify_manifest.py --verify
python3 scripts/verify_manifest.py --verify

echo "=== [2/12] Stdlib Unittest Suite ==="
python3 -m unittest discover -s tests -v

echo "=== [3/12] Zero-Secret Ecosystem Hygiene Audit ==="
if [[ -n "${CI:-}" && ! -d "${HOME}/.agents" ]]; then
  python3 scripts/audit_ecosystem_hygiene.py --json >/dev/null
  echo "CI environment without \$HOME/.agents: ran non-strict schema check (PASS)"
else
  python3 scripts/audit_ecosystem_hygiene.py --json --strict >/dev/null
  echo "Host ecosystem hygiene audit: PASS (strict)"
fi

echo "=== [4/12] ast-grep Structural Ban Scan ==="
ast-grep scan
ast-grep scan --no-ignore hidden

echo "=== [5/12] Ruff Lint & Format Check ==="
ruff check .
ruff format --check .

echo "=== [6/12] ty Static Type Check ==="
ty check

echo "=== [7/12] ShellCheck Static Analysis ==="
shellcheck scripts/*.sh

echo "=== [8/12] Gitleaks Secret Scan ==="
gitleaks detect --no-git --redact --source .
if git rev-parse --verify HEAD >/dev/null 2>&1; then
  gitleaks git --redact .
fi

echo "=== [9/12] Zizmor GitHub Actions Security Audit ==="
zizmor --offline .github/workflows/sota-convergence-gates.yml

echo "=== [10/12] SkillEvaluator Tier 1 Keyless Gate ==="
skillevaluator tier1 .agents/skills/sota-convergence-audit --no-llm --output-dir "$TMP_DIR/skilleval"

echo "=== [11/12] Syft CycloneDX SBOM -> OSV-Scanner ==="
syft dir:. -o cyclonedx-json="$TMP_DIR/sbom.cdx.json"
osv-scanner scan source -L "$TMP_DIR/sbom.cdx.json"

echo "=== [12/12] Zensical Strict Portal Build ==="
zensical build --clean --strict

echo "=== ALL 12 CHECKS PASSED ==="
