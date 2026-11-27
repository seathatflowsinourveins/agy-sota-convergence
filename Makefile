.PHONY: check seal audit docs docs-serve sbom skill-eval clean

check:
	bash scripts/check.sh

seal:
	python3 scripts/verify_manifest.py --seal
	python3 scripts/verify_manifest.py --verify

audit:
	python3 scripts/audit_ecosystem_hygiene.py --json --strict

docs:
	zensical build --clean --strict

docs-serve:
	zensical serve

sbom:
	@tmp_dir=$$(mktemp -d); \
	trap 'rm -rf "$$tmp_dir"' EXIT; \
	syft dir:. -o cyclonedx-json="$$tmp_dir/sbom.cdx.json"; \
	osv-scanner scan source -L "$$tmp_dir/sbom.cdx.json"

skill-eval:
	@tmp_dir=$$(mktemp -d); \
	trap 'rm -rf "$$tmp_dir"' EXIT; \
	skillevaluator tier1 .agents/skills/sota-convergence-audit --no-llm --output-dir "$$tmp_dir"

clean:
	rm -rf site .cache .ruff_cache .pytest_cache reports sbom*.json
