"""Portable contract tests for the zero-wrapper AGY Practice Plugin Pack."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = REPO_ROOT / "plugins" / "agy-sota-practice"

SYNC_PAIRS = (
    (
        ".agents/scripts/pre_tool_fail_closed.py",
        "plugins/agy-sota-practice/scripts/pre_tool_fail_closed.py",
    ),
    (
        ".agents/scripts/cross_session_hooks.py",
        "plugins/agy-sota-practice/scripts/cross_session_hooks.py",
    ),
    (
        ".agents/schemas/handoff_packet.schema.json",
        "plugins/agy-sota-practice/templates/handoff_packet.schema.json",
    ),
    (
        ".agents/templates/permissions.baseline.json",
        "plugins/agy-sota-practice/templates/permissions.baseline.json",
    ),
    (
        ".agents/templates/sidecar.scheduled.json",
        "plugins/agy-sota-practice/templates/sidecar.scheduled.json",
    ),
    (
        ".agents/templates/sidecar.relay.json",
        "plugins/agy-sota-practice/templates/sidecar.relay.json",
    ),
    (
        "workflows/workflow.json",
        "plugins/agy-sota-practice/workflows/workflow.json",
    ),
    (
        "workflows/sota_convergence_audit.py",
        "plugins/agy-sota-practice/workflows/sota_convergence_audit.py",
    ),
)


class TestAgyPracticePluginPack(unittest.TestCase):
    """Verify plugin manifest, 8-file byte parity, fail-closed hook, and live agy validate."""

    def test_plugin_manifest_opt_in_hooks_and_byte_parity(self) -> None:
        meta = json.loads((PLUGIN_ROOT / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["$schema"], "https://antigravity.google/schemas/v1/plugin.json")
        self.assertEqual(meta["name"], "agy-sota-practice")
        self.assertEqual(meta["version"], "3.2.0")
        self.assertTrue((PLUGIN_ROOT / meta["logo"]).is_file())

        hooks = json.loads((PLUGIN_ROOT / "hooks.json").read_text(encoding="utf-8"))
        self.assertEqual(len(hooks), 2)
        for group_name, group_cfg in hooks.items():
            self.assertFalse(
                group_cfg.get("enabled"),
                msg=f"Hook group {group_name} must ship disabled by default",
            )

        for src_rel, dst_rel in SYNC_PAIRS:
            src_sha = hashlib.sha256((REPO_ROOT / src_rel).read_bytes()).hexdigest()
            dst_sha = hashlib.sha256((REPO_ROOT / dst_rel).read_bytes()).hexdigest()
            self.assertEqual(src_sha, dst_sha, msg=f"Parity drift: {src_rel} != {dst_rel}")

        for script_name in ("pre_tool_fail_closed.py", "cross_session_hooks.py"):
            sp = PLUGIN_ROOT / "scripts" / script_name
            self.assertTrue(os.access(sp, os.X_OK), msg=f"{sp} must be executable (0755)")

    def test_packaged_pre_tool_fail_closed_behavior(self) -> None:
        hook_script = PLUGIN_ROOT / "scripts" / "pre_tool_fail_closed.py"

        # Malformed JSON -> exit 0 + deny
        r_bad = subprocess.run(
            [sys.executable, str(hook_script)],
            input="{malformed-json",
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(r_bad.returncode, 0)
        self.assertEqual(json.loads(r_bad.stdout)["decision"], "deny")

        # Benign workspace git status -> exit 0 + allow
        r_ok = subprocess.run(
            [sys.executable, str(hook_script)],
            input=json.dumps(
                {
                    "toolCall": {"name": "run_command", "args": {"CommandLine": "git status"}},
                    "workspacePaths": ["/tmp/ws"],
                }
            ),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(r_ok.returncode, 0)
        self.assertEqual(json.loads(r_ok.stdout)["decision"], "allow")

        # Protected .env read -> exit 0 + deny
        r_env = subprocess.run(
            [sys.executable, str(hook_script)],
            input=json.dumps(
                {
                    "toolCall": {"name": "read_file", "args": {"Path": "/tmp/ws/.env"}},
                    "workspacePaths": ["/tmp/ws"],
                }
            ),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(r_env.returncode, 0)
        self.assertEqual(json.loads(r_env.stdout)["decision"], "deny")

    @unittest.skipUnless(shutil.which("agy"), "agy CLI not installed on runner")
    def test_live_agy_plugin_validate_strict_zero_findings(self) -> None:
        proc = subprocess.run(
            ["agy", "plugin", "validate", "--strict", "--json", str(PLUGIN_ROOT)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["name"], "agy-sota-practice")
        self.assertEqual(payload["findings"], [])
        self.assertEqual(
            payload["components"],
            {
                "agents": 2,
                "hooks": 2,
                "mcpServers": 0,
                "rules": 2,
                "sidecars": 0,
                "skills": 3,
            },
        )


if __name__ == "__main__":
    unittest.main()
