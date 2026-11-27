.PHONY: check seal sync-plugin audit docs docs-serve sbom skill-eval clean

check:
	bash scripts/check.sh

seal:
	python3 scripts/verify_manifest.py --seal
	python3 scripts/verify_manifest.py --verify

sync-plugin:
	mkdir -p plugins/agy-sota-practice/scripts plugins/agy-sota-practice/workflows plugins/agy-sota-practice/templates
	cp .agents/scripts/pre_tool_fail_closed.py plugins/agy-sota-practice/scripts/pre_tool_fail_closed.py
	cp .agents/scripts/cross_session_hooks.py plugins/agy-sota-practice/scripts/cross_session_hooks.py
	chmod 0755 plugins/agy-sota-practice/scripts/pre_tool_fail_closed.py plugins/agy-sota-practice/scripts/cross_session_hooks.py
	cp .agents/schemas/handoff_packet.schema.json plugins/agy-sota-practice/templates/handoff_packet.schema.json
	cp .agents/templates/permissions.baseline.json plugins/agy-sota-practice/templates/permissions.baseline.json
	cp .agents/templates/sidecar.scheduled.json plugins/agy-sota-practice/templates/sidecar.scheduled.json
	cp .agents/templates/sidecar.relay.json plugins/agy-sota-practice/templates/sidecar.relay.json
	cp workflows/workflow.json plugins/agy-sota-practice/workflows/workflow.json
	cp workflows/sota_convergence_audit.py plugins/agy-sota-practice/workflows/sota_convergence_audit.py

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
