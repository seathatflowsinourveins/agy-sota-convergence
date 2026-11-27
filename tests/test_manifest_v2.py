"""Stdlib unittest suite for the 17-gate SOTA Convergence Manifest sealer & verifier.

Tests live 17/17 verification on the sealed repository manifest plus 14 isolated
temp-directory adversarial mutations that must all fail closed (exit code 1),
and isolated zero-secret host ecosystem hygiene scorecard validation.
"""

from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_verifier_module() -> Any:
    script_path = REPO_ROOT / "scripts" / "verify_manifest.py"
    spec = importlib.util.spec_from_file_location("verify_manifest", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


vm: Any = _load_verifier_module()


def _run_quiet(fn: Any, *args: Any, **kwargs: Any) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = fn(*args, **kwargs)
    return int(rc), buf.getvalue()


class TestCompoundingManifestV2(unittest.TestCase):
    """Verify live 17/17 pass, 14 isolated adversarial mutation rejections, and scorecard."""

    def _copy_repo_to_temp(self) -> tuple[tempfile.TemporaryDirectory[str], Path, Path, Path]:
        td = tempfile.TemporaryDirectory()
        troot = Path(td.name)
        for rel_file in (
            "AGENTS.md",
            "LICENSE",
            "SECURITY.md",
            ".gitleaks.toml",
            ".gitignore",
            "orca.yaml",
            "Makefile",
            "UPSTREAM.md",
            "upstream-map.toml",
            "zensical.toml",
        ):
            shutil.copy2(REPO_ROOT / rel_file, troot / rel_file)
        ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
        shutil.copytree(REPO_ROOT / ".agents", troot / ".agents", ignore=ignore)
        shutil.copytree(REPO_ROOT / "docs", troot / "docs", ignore=ignore)
        shutil.copytree(REPO_ROOT / "scripts", troot / "scripts", ignore=ignore)
        shutil.copytree(REPO_ROOT / "workflows", troot / "workflows", ignore=ignore)
        (troot / "manifest").mkdir(parents=True, exist_ok=True)
        tmp_manifest = troot / "manifest" / "compounding_manifest.v2.json"
        tmp_schema = troot / "manifest" / "compounding_manifest.v2.schema.json"
        shutil.copy2(vm.DEFAULT_MANIFEST, tmp_manifest)
        shutil.copy2(vm.DEFAULT_SCHEMA, tmp_schema)
        return td, troot, tmp_manifest, tmp_schema

    def test_00_live_manifest_passes_17_of_17_gates(self) -> None:
        rc, out = _run_quiet(vm.run_verify, vm.DEFAULT_MANIFEST, vm.DEFAULT_SCHEMA, REPO_ROOT)
        self.assertEqual(rc, 0, msg=out)
        self.assertIn("CHECKS    : 17/17 passed", out)
        self.assertIn("RESULT    : VERIFIED PASS", out)

    def test_01_tampered_manifest_sha256_fails(self) -> None:
        td, troot, tmp_manifest, tmp_schema = self._copy_repo_to_temp()
        try:
            data = json.loads(tmp_manifest.read_text(encoding="utf-8"))
            data["integrity"]["sha256"] = "0" * 64
            tmp_manifest.write_text(json.dumps(data), encoding="utf-8")
            rc, out = _run_quiet(vm.run_verify, tmp_manifest, tmp_schema, troot)
            self.assertEqual(rc, 1, msg=out)
            self.assertIn("[10][FAIL] sha256_integrity_seal", out)
        finally:
            td.cleanup()

    def test_02_tampered_adr_file_byte_fails(self) -> None:
        td, troot, tmp_manifest, tmp_schema = self._copy_repo_to_temp()
        try:
            data = json.loads(tmp_manifest.read_text(encoding="utf-8"))
            adr0 = troot / data["adr_governance"]["adrs"][0]["file"]
            adr0.write_text(
                adr0.read_text(encoding="utf-8") + "\n<!-- tamper -->\n", encoding="utf-8"
            )
            rc, out = _run_quiet(vm.run_verify, tmp_manifest, tmp_schema, troot)
            self.assertEqual(rc, 1, msg=out)
            self.assertIn("[12][FAIL] adr_files_sha256_parity", out)
        finally:
            td.cleanup()

    def test_03_missing_adr_file_fails(self) -> None:
        td, troot, tmp_manifest, tmp_schema = self._copy_repo_to_temp()
        try:
            data = json.loads(tmp_manifest.read_text(encoding="utf-8"))
            adr0 = troot / data["adr_governance"]["adrs"][0]["file"]
            adr0.unlink()
            rc, out = _run_quiet(vm.run_verify, tmp_manifest, tmp_schema, troot)
            self.assertEqual(rc, 1, msg=out)
            self.assertIn("[11][FAIL] adr_12_bounded_bijection_and_madr4", out)
        finally:
            td.cleanup()

    def test_04_missing_madr4_section_fails_even_after_reseal(self) -> None:
        td, troot, tmp_manifest, tmp_schema = self._copy_repo_to_temp()
        try:
            data = json.loads(tmp_manifest.read_text(encoding="utf-8"))
            adr0 = troot / data["adr_governance"]["adrs"][0]["file"]
            adr0.write_text(
                adr0.read_text(encoding="utf-8").replace("### Confirmation", "### Removed"),
                encoding="utf-8",
            )
            rc, out = _run_quiet(vm.run_seal, tmp_manifest, tmp_schema, troot)
            self.assertEqual(rc, 1, msg=out)
            self.assertIn("[11][FAIL] adr_12_bounded_bijection_and_madr4", out)
        finally:
            td.cleanup()

    def test_05_retiring_nov30_hyphenated_slug_fails(self) -> None:
        td, troot, tmp_manifest, tmp_schema = self._copy_repo_to_temp()
        try:
            data = json.loads(tmp_manifest.read_text(encoding="utf-8"))
            data["surfaces"]["antigravity_sdk"]["default_model"] = "claude-sonnet-4-6"
            tmp_manifest.write_text(json.dumps(data), encoding="utf-8")
            rc, out = _run_quiet(vm.run_seal, tmp_manifest, tmp_schema, troot)
            self.assertEqual(rc, 1, msg=out)
            self.assertIn("[04][FAIL] zero_retiring_nov30_models_active", out)
        finally:
            td.cleanup()

    def test_06_latest_pin_in_clean_install_registry_fails(self) -> None:
        td, troot, tmp_manifest, tmp_schema = self._copy_repo_to_temp()
        try:
            data = json.loads(tmp_manifest.read_text(encoding="utf-8"))
            data["clean_install_registry"]["entries"][1]["pinned_version"] = "latest"
            tmp_manifest.write_text(json.dumps(data), encoding="utf-8")
            rc, out = _run_quiet(vm.run_seal, tmp_manifest, tmp_schema, troot)
            self.assertEqual(rc, 1, msg=out)
            self.assertIn("[05][FAIL] zero_unpinned_placeholders", out)
            self.assertIn("[13][FAIL] clean_install_registry_coverage", out)
        finally:
            td.cleanup()

    def test_07_layer_disjoint_overlap_fails(self) -> None:
        td, troot, tmp_manifest, tmp_schema = self._copy_repo_to_temp()
        try:
            data = json.loads(tmp_manifest.read_text(encoding="utf-8"))
            dup = data["layers"][0]["owns_exclusively"][0]
            data["layers"][1]["owns_exclusively"].append(dup)
            tmp_manifest.write_text(json.dumps(data), encoding="utf-8")
            rc, out = _run_quiet(vm.run_seal, tmp_manifest, tmp_schema, troot)
            self.assertEqual(rc, 1, msg=out)
            self.assertIn("[03][FAIL] disjoint_L0_L10_layers", out)
        finally:
            td.cleanup()

    def test_08_tilde_deny_path_fails(self) -> None:
        td, troot, tmp_manifest, tmp_schema = self._copy_repo_to_temp()
        try:
            data = json.loads(tmp_manifest.read_text(encoding="utf-8"))
            data["security_invariants"]["standing_deny_rules_baseline"].append("read_file(~/.ssh)")
            tmp_manifest.write_text(json.dumps(data), encoding="utf-8")
            rc, out = _run_quiet(vm.run_seal, tmp_manifest, tmp_schema, troot)
            self.assertEqual(rc, 1, msg=out)
            self.assertIn("[08][FAIL] security_and_sandbox_invariants", out)
        finally:
            td.cleanup()

    def test_09_agy_linux_bubblewrap_claim_fails(self) -> None:
        td, troot, tmp_manifest, tmp_schema = self._copy_repo_to_temp()
        try:
            data = json.loads(tmp_manifest.read_text(encoding="utf-8"))
            data["security_invariants"]["os_sandbox_primitives"]["linux"] = "bubblewrap"
            tmp_manifest.write_text(json.dumps(data), encoding="utf-8")
            rc, out = _run_quiet(vm.run_seal, tmp_manifest, tmp_schema, troot)
            self.assertEqual(rc, 1, msg=out)
            self.assertIn("[08][FAIL] security_and_sandbox_invariants", out)
        finally:
            td.cleanup()

    def test_10_unexpected_schema_property_fails(self) -> None:
        td, troot, tmp_manifest, tmp_schema = self._copy_repo_to_temp()
        try:
            data = copy.deepcopy(json.loads(tmp_manifest.read_text(encoding="utf-8")))
            data["undocumented_root_key"] = True
            tmp_manifest.write_text(json.dumps(data), encoding="utf-8")
            rc, out = _run_quiet(vm.run_seal, tmp_manifest, tmp_schema, troot)
            self.assertEqual(rc, 1, msg=out)
            self.assertIn("[02][FAIL] schema_validation", out)
        finally:
            td.cleanup()

    def test_11_bloated_agents_md_fails(self) -> None:
        td, troot, tmp_manifest, tmp_schema = self._copy_repo_to_temp()
        try:
            # Exceed >45 lines
            (troot / "AGENTS.md").write_text(
                "\n".join(f"line {i}" for i in range(50)), encoding="utf-8"
            )
            rc1, out1 = _run_quiet(vm.run_verify, tmp_manifest, tmp_schema, troot)
            self.assertEqual(rc1, 1, msg=out1)
            self.assertIn("[15][FAIL] repo_hygiene_and_anti_bloat_ratchet", out1)

            # Exceed >1,600 chars in <=10 lines
            (troot / "AGENTS.md").write_text("x" * 1650 + "\n", encoding="utf-8")
            rc2, out2 = _run_quiet(vm.run_verify, tmp_manifest, tmp_schema, troot)
            self.assertEqual(rc2, 1, msg=out2)
            self.assertIn("[15][FAIL] repo_hygiene_and_anti_bloat_ratchet", out2)
        finally:
            td.cleanup()

    def test_12_overlong_skill_description_fails(self) -> None:
        td, troot, tmp_manifest, tmp_schema = self._copy_repo_to_temp()
        try:
            skill_md = troot / ".agents" / "skills" / "sota-convergence-audit" / "SKILL.md"
            overlong = "a" * 1050
            skill_md.write_text(
                f"---\nname: sota-convergence-audit\ndescription: {overlong}\n---\n\n# Audit\n",
                encoding="utf-8",
            )
            rc, out = _run_quiet(vm.run_verify, tmp_manifest, tmp_schema, troot)
            self.assertEqual(rc, 1, msg=out)
            self.assertIn("[15][FAIL] repo_hygiene_and_anti_bloat_ratchet", out)
        finally:
            td.cleanup()

    def test_13_ecosystem_hygiene_scorecard_is_zero_secret_and_valid(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            fake_home = Path(td)
            agents_root = fake_home / ".agents"
            gemini_cfg = fake_home / ".gemini" / "config"
            (agents_root / "skills" / "demo-skill").mkdir(parents=True)
            (gemini_cfg / "skills").mkdir(parents=True)
            (fake_home / ".gemini" / "antigravity" / "mcp" / "demo-mcp").mkdir(parents=True)

            charter = agents_root / "AGENTS.md"
            charter.write_text(
                "# Charter\n\n1. Stay concise and fail closed.\n",
                encoding="utf-8",
            )
            (fake_home / ".gemini" / "GEMINI.md").symlink_to(charter)
            (agents_root / "skills" / "demo-skill" / "SKILL.md").write_text(
                "---\nname: demo-skill\ndescription: Use when testing isolated scorecard.\n---\n\n# Demo\n",
                encoding="utf-8",
            )
            (gemini_cfg / "skills" / "demo-skill").symlink_to(agents_root / "skills" / "demo-skill")
            (gemini_cfg / "hooks.json").write_text(
                json.dumps(
                    {
                        "sota-security-policy": {
                            "enabled": True,
                            "PreToolUse": [
                                {
                                    "matcher": "*",
                                    "hooks": [
                                        {
                                            "type": "command",
                                            "command": "python3 guard.py",
                                        }
                                    ],
                                }
                            ],
                        }
                    }
                ),
                encoding="utf-8",
            )
            (fake_home / ".env").write_text("SECRET_TOKEN=must-never-read\n", encoding="utf-8")
            (fake_home / ".gemini" / "antigravity" / "mcp" / "demo-mcp" / "tool_a.json").write_text(
                '{"name":"tool_a","description":"demo"}\n', encoding="utf-8"
            )

            proc = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "audit_ecosystem_hygiene.py"),
                    "--json",
                    "--strict",
                    "--home",
                    str(fake_home),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr or proc.stdout)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["schema_version"], "1.1.0")
            self.assertFalse(payload["security_boundary"]["secrets_accessed"])
            self.assertEqual(payload["summary"]["status"], "PASS")
            self.assertEqual(payload["summary"]["total_findings"], 0)

            sc = payload["context_manifest_scorecard"]
            self.assertEqual(sc["global_charter"]["html_comment_chars"], 0)
            self.assertTrue(sc["global_charter"]["within_45L_1600c"])
            self.assertEqual(sc["global_skills"]["count"], 1)
            self.assertEqual(sc["mcp_cached_servers"], {"demo-mcp": 1})
            self.assertEqual(sc["mcp_total_cached_tools"], 1)
            self.assertGreater(sc["total_startup_context_est_tokens"], 0)
            self.assertNotIn("must-never-read", proc.stdout)

    def test_14_unmapped_runtime_py_fails_gate_16(self) -> None:
        td, troot, tmp_manifest, tmp_schema = self._copy_repo_to_temp()
        try:
            (troot / "scripts" / "rogue_unmapped.py").write_text(
                '"""Unmapped script."""\nprint("rogue")\n', encoding="utf-8"
            )
            rc, out = _run_quiet(vm.run_verify, tmp_manifest, tmp_schema, troot)
            self.assertEqual(rc, 1, msg=out)
            self.assertIn("[16][FAIL] upstream_registry_and_map_parity", out)
        finally:
            td.cleanup()

    def test_15_missing_upstream_winner_and_orca_default_tabs_fail(self) -> None:
        td, troot, tmp_manifest, tmp_schema = self._copy_repo_to_temp()
        try:
            upstream_md = troot / "UPSTREAM.md"
            original_upstream = upstream_md.read_text(encoding="utf-8")
            stripped_lines = [
                ln for ln in original_upstream.splitlines() if "`l10_zensical`" not in ln
            ]
            upstream_md.write_text("\n".join(stripped_lines) + "\n", encoding="utf-8")
            rc1, out1 = _run_quiet(vm.run_verify, tmp_manifest, tmp_schema, troot)
            self.assertEqual(rc1, 1, msg=out1)
            self.assertIn("[16][FAIL] upstream_registry_and_map_parity", out1)

            # Restore UPSTREAM.md and test forbidden defaultTabs key in orca.yaml
            upstream_md.write_text(original_upstream, encoding="utf-8")
            orca_yaml = troot / "orca.yaml"
            orca_yaml.write_text(
                orca_yaml.read_text(encoding="utf-8") + "\ndefaultTabs:\n  - name: invalid\n",
                encoding="utf-8",
            )
            rc2, out2 = _run_quiet(vm.run_verify, tmp_manifest, tmp_schema, troot)
            self.assertEqual(rc2, 1, msg=out2)
            self.assertIn("[17][FAIL] repo_scaffolding_and_portal_integrity", out2)
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
