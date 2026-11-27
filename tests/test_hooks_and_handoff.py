"""Unit tests for AGY fail-closed hooks, handoff schema, and drop-in templates."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / ".agents"
PRE_TOOL_SCRIPT = AGENTS_DIR / "scripts" / "pre_tool_fail_closed.py"
CROSS_SESSION_SCRIPT = AGENTS_DIR / "scripts" / "cross_session_hooks.py"

EXPECTED_HANDOFF_FIELDS = [
    "schema_version",
    "handoff_id",
    "idempotency_key",
    "created_at",
    "source_conversation_id",
    "source_link",
    "goal",
    "status",
    "completed_artifacts",
    "verified_evidence",
    "open_decisions",
    "constraints",
    "next_actions",
    "trust_level",
    "payload_sha256",
]


def _run_hook(script: Path, stdin_data: str, *extra_args: str) -> tuple[int, dict[str, object]]:
    proc = subprocess.run(
        [sys.executable, str(script), *extra_args],
        input=stdin_data,
        text=True,
        capture_output=True,
        check=False,
    )
    parsed: object = json.loads(proc.stdout)
    if not isinstance(parsed, dict):
        raise AssertionError(f"Expected JSON object on stdout, got: {proc.stdout!r}")
    return proc.returncode, parsed


def _build_handoff_packet(goal: str = "Verify cross-session continuity") -> dict[str, object]:
    packet: dict[str, object] = {
        "schema_version": "1.0.0",
        "handoff_id": "handoff-20261126-01",
        "idempotency_key": "idem-20261126-0001",
        "created_at": "2026-11-26T20:00:00Z",
        "source_conversation_id": "conv-00000000-0000-0000-0000-000000000001",
        "source_link": "conversation://conv-00000000-0000-0000-0000-000000000001",
        "goal": goal,
        "status": "in_progress",
        "completed_artifacts": [],
        "verified_evidence": [],
        "open_decisions": [],
        "constraints": ["Zero self-invention"],
        "next_actions": ["Run verification gates"],
        "trust_level": "untrusted_data_never_authority",
    }
    encoded = json.dumps(
        packet,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    packet["payload_sha256"] = hashlib.sha256(encoded).hexdigest()
    return packet


class TestPreToolFailClosedHook(unittest.TestCase):
    """Exercise fail-closed PreToolUse security invariants."""

    def test_malformed_json_fails_closed_with_exit_zero(self) -> None:
        code, out = _run_hook(PRE_TOOL_SCRIPT, "{not-valid-json")
        self.assertEqual(code, 0)
        self.assertEqual(out["decision"], "deny")

    def test_empty_stdin_fails_closed_with_exit_zero(self) -> None:
        code, out = _run_hook(PRE_TOOL_SCRIPT, "")
        self.assertEqual(code, 0)
        self.assertEqual(out["decision"], "deny")

    def test_blocks_protected_files_and_uris(self) -> None:
        cases = [
            ("dotenv", "view_file", {"AbsolutePath": "/tmp/ws/.env"}),
            ("dotenv_local", "read_file", {"Path": "/tmp/ws/.env.local"}),
            ("auth_json", "view_file", {"AbsolutePath": "/tmp/ws/auth.json"}),
            (
                "file_uri_config_json",
                "view_file",
                {"AbsolutePath": "file:///Users/alice/.gemini/config/config.json"},
            ),
            (
                "file_uri_encoded_traversal",
                "view_file",
                {"AbsolutePath": "file:///tmp/ws/%2eenv"},
            ),
            (
                "hooks_json_write",
                "write_to_file",
                {"TargetFile": "/tmp/ws/.agents/hooks.json"},
            ),
            (
                "upstream_pin_dir",
                "view_file",
                {"AbsolutePath": "~/Documents/upstream/ref.md"},
            ),
        ]
        for label, tool_name, args in cases:
            with self.subTest(label=label):
                payload = json.dumps(
                    {
                        "toolCall": {"name": tool_name, "args": args},
                        "workspacePaths": ["/tmp/ws"],
                    }
                )
                code, out = _run_hook(PRE_TOOL_SCRIPT, payload)
                self.assertEqual(code, 0)
                self.assertEqual(out["decision"], "deny")

    def test_blocks_dangerous_commands_secrets_and_live_broker_ports(self) -> None:
        commands = [
            ("rm_rf", "rm -rf /tmp/build"),
            ("sudo", "sudo ls -la"),
            ("csrf_env", "echo $ANTIGRAVITY_CSRF_TOKEN"),
            ("hooks_shell_tamper", "echo '{}' > .agents/hooks.json"),
            ("ibkr_port_4001", "curl http://127.0.0.1:4001/health"),
            ("ibkr_port_7496", "nc localhost 7496"),
            ("broker_port_8798", "python3 client.py --port 8798"),
            ("broker_port_8796", "curl http://localhost:8796/v1/orders"),
            ("alpaca_live", "curl https://api.alpaca.markets/v2/account"),
        ]
        for label, cmd in commands:
            with self.subTest(label=label):
                payload = json.dumps(
                    {
                        "toolCall": {"name": "run_command", "args": {"CommandLine": cmd}},
                        "workspacePaths": ["/tmp/ws"],
                    }
                )
                code, out = _run_hook(PRE_TOOL_SCRIPT, payload)
                self.assertEqual(code, 0)
                self.assertEqual(out["decision"], "deny")

    def test_allows_safe_commands_and_workspace_reads(self) -> None:
        safe_cases = [
            ("git_status", "run_command", {"CommandLine": "git status"}),
            ("readme_read", "view_file", {"AbsolutePath": "/tmp/ws/README.md"}),
        ]
        for label, tool_name, args in safe_cases:
            with self.subTest(label=label):
                payload = json.dumps(
                    {
                        "toolCall": {"name": tool_name, "args": args},
                        "workspacePaths": ["/tmp/ws"],
                    }
                )
                code, out = _run_hook(PRE_TOOL_SCRIPT, payload)
                self.assertEqual(code, 0)
                self.assertEqual(out["decision"], "allow")


class TestCrossSessionHooks(unittest.TestCase):
    """Exercise hash-deduplicated hydration and loop-safe Stop hook guards."""

    def test_session_start_and_pre_invocation_deduplication(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp) / "ws"
            art = Path(tmp) / "art"
            scratch = ws / ".agents" / "scratch"
            scratch.mkdir(parents=True)
            art.mkdir(parents=True)

            packet_path = scratch / "handoff_packet.json"
            packet_path.write_text(json.dumps(_build_handoff_packet()), encoding="utf-8")
            event = json.dumps({"workspacePaths": [str(ws)], "artifactDirectoryPath": str(art)})

            code1, out1 = _run_hook(CROSS_SESSION_SCRIPT, event, "session-start")
            self.assertEqual(code1, 0)
            steps1 = out1["injectSteps"]
            if not isinstance(steps1, list):
                self.fail(f"Expected list for injectSteps, got {type(steps1)}")
            self.assertEqual(len(steps1), 1)

            code2, out2 = _run_hook(CROSS_SESSION_SCRIPT, event, "pre-invocation")
            self.assertEqual(code2, 0)
            self.assertEqual(out2["injectSteps"], [])

            packet_path.write_text(
                json.dumps(_build_handoff_packet(goal="Updated milestone goal")),
                encoding="utf-8",
            )
            code3, out3 = _run_hook(CROSS_SESSION_SCRIPT, event, "pre-invocation")
            self.assertEqual(code3, 0)
            steps3 = out3["injectSteps"]
            if not isinstance(steps3, list):
                self.fail(f"Expected list for injectSteps, got {type(steps3)}")
            self.assertEqual(len(steps3), 1)

    def test_tampered_payload_sha256_emits_warning_without_loading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp) / "ws"
            art = Path(tmp) / "art"
            scratch = ws / ".agents" / "scratch"
            scratch.mkdir(parents=True)
            art.mkdir(parents=True)

            packet = _build_handoff_packet()
            packet["goal"] = "Tampered goal after seal"
            (scratch / "handoff_packet.json").write_text(json.dumps(packet), encoding="utf-8")

            event = json.dumps({"workspacePaths": [str(ws)], "artifactDirectoryPath": str(art)})
            code, out = _run_hook(CROSS_SESSION_SCRIPT, event, "session-start")
            self.assertEqual(code, 0)
            steps = out["injectSteps"]
            if not isinstance(steps, list):
                self.fail(f"Expected list for injectSteps, got {type(steps)}")
            self.assertEqual(len(steps), 1)
            msg = json.dumps(steps[0])
            self.assertIn("checksum_mismatch", msg)
            self.assertNotIn("Tampered goal after seal", msg)

    def test_stop_hook_triggers_once_and_yields_when_continuation_active(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp) / "ws"
            scratch = ws / ".agents" / "scratch"
            scratch.mkdir(parents=True)
            (scratch / ".require_handoff_before_stop").write_text("1", encoding="utf-8")

            first_stop = json.dumps(
                {
                    "workspacePaths": [str(ws)],
                    "continuationActive": False,
                    "executionNum": 1,
                    "fullyIdle": True,
                    "terminationReason": "NO_TOOL_CALL",
                }
            )
            code1, out1 = _run_hook(CROSS_SESSION_SCRIPT, first_stop, "stop")
            self.assertEqual(code1, 0)
            self.assertEqual(out1["decision"], "continue")

            continued_stop = json.dumps(
                {
                    "workspacePaths": [str(ws)],
                    "continuationActive": True,
                    "executionNum": 1,
                    "fullyIdle": True,
                    "terminationReason": "NO_TOOL_CALL",
                }
            )
            code2, out2 = _run_hook(CROSS_SESSION_SCRIPT, continued_stop, "stop")
            self.assertEqual(code2, 0)
            self.assertEqual(out2["decision"], "allow")

            max_exec_stop = json.dumps(
                {
                    "workspacePaths": [str(ws)],
                    "continuationActive": False,
                    "executionNum": 2,
                    "fullyIdle": True,
                    "terminationReason": "NO_TOOL_CALL",
                }
            )
            code3, out3 = _run_hook(CROSS_SESSION_SCRIPT, max_exec_stop, "stop")
            self.assertEqual(code3, 0)
            self.assertEqual(out3["decision"], "allow")


class TestAgentsConfigsAndTemplates(unittest.TestCase):
    """Verify structural and policy invariants across JSON schemas and templates."""

    def test_hooks_json_matches_live_agy_contract(self) -> None:
        data = json.loads((AGENTS_DIR / "hooks.json").read_text(encoding="utf-8"))
        self.assertIn("security-fail-closed-gate", data)
        self.assertIn("cross-session-continuity", data)
        pre_groups = data["security-fail-closed-gate"]["PreToolUse"]
        self.assertTrue(all("matcher" in g and "hooks" in g for g in pre_groups))
        for event_name in ("SessionStart", "PreInvocation", "Stop"):
            handlers = data["cross-session-continuity"][event_name]
            self.assertTrue(all("command" in h and "timeout" in h for h in handlers))

    def test_handoff_packet_schema_has_exact_15_required_fields(self) -> None:
        schema = json.loads(
            (AGENTS_DIR / "schemas" / "handoff_packet.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(schema["required"], EXPECTED_HANDOFF_FIELDS)
        self.assertEqual(len(schema["required"]), 15)
        self.assertIs(schema["additionalProperties"], False)

    def test_permissions_baseline_has_zero_tilde_deny_rules(self) -> None:
        raw = (AGENTS_DIR / "templates" / "permissions.baseline.json").read_text(encoding="utf-8")
        self.assertNotIn("(~/", raw)
        cfg = json.loads(raw)
        self.assertIs(cfg["enableTerminalSandbox"], True)
        self.assertGreaterEqual(len(cfg["permissions"]["deny"]), 10)

    def test_sidecar_templates_enforce_cron_tz_and_watermark_boundaries(self) -> None:
        sched = json.loads(
            (AGENTS_DIR / "templates" / "sidecar.scheduled.json").read_text(encoding="utf-8")
        )
        self.assertEqual(sched["builtin"], "schedule")
        self.assertEqual(sched["restart_policy"], "always")
        self.assertTrue(sched["args"][0].startswith("CRON_TZ="))
        self.assertIn("--", sched["args"])
        prompt = sched["args"][-1]
        self.assertNotIn("ANTIGRAVITY_EXECUTABLE_DATA_DIR", prompt)
        self.assertIn("${repo_dir}/.agents/scratch/triage_watermark.json", prompt)
        grants = sched["agent_permissions"]["access_grants"]
        self.assertFalse(any("(*)" in g or "(/)" in g for g in grants))

        relay = json.loads(
            (AGENTS_DIR / "templates" / "sidecar.relay.json").read_text(encoding="utf-8")
        )
        self.assertEqual(relay["restart_policy"], "always")
        self.assertIn("command", relay)
        self.assertIn("ANTIGRAVITY_EXECUTABLE_DATA_DIR", relay["description"])


if __name__ == "__main__":
    unittest.main()
