"""Portable contract tests for the host AGY fail-closed security hook shim.

Exercises ~/.agents/hooks/agy-hook-shim.py, ~/.agents/hooks/policy_core.py, and
~/.agents/security-policy.toml dynamically via Path.home() so the suite stays
fully portable and skips cleanly on CI runners without the host shim installed.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from collections.abc import Mapping
from pathlib import Path

HOST_AGENTS_DIR = Path.home() / ".agents"
HOST_HOOKS_DIR = HOST_AGENTS_DIR / "hooks"
HOST_SHIM = HOST_HOOKS_DIR / "agy-hook-shim.py"
HOST_POLICY_CORE = HOST_HOOKS_DIR / "policy_core.py"
HOST_POLICY_TOML = HOST_AGENTS_DIR / "security-policy.toml"
REPO_ROOT = Path(__file__).resolve().parent.parent


def _run_shim(
    shim_path: Path,
    stdin_data: str,
    event: str = "PreToolUse",
    *,
    safe_path: bool = False,
) -> tuple[int, dict[str, object]]:
    env = os.environ.copy()
    if safe_path:
        env["PYTHONSAFEPATH"] = "1"
        env.pop("PYTHONPATH", None)
    cmd = [sys.executable]
    if safe_path:
        cmd.append("-P")
    cmd.extend([str(shim_path), "--event", event])
    proc = subprocess.run(
        cmd,
        input=stdin_data,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    parsed: object = json.loads(proc.stdout)
    if not isinstance(parsed, dict):
        raise AssertionError(f"Expected JSON object on stdout, got: {proc.stdout!r}")
    return proc.returncode, parsed


def _pre_tool_payload(
    tool_name: str,
    tool_args: Mapping[str, object],
    cwd: str | None = None,
) -> str:
    return json.dumps(
        {
            "hookEventName": "PreToolUse",
            "cwd": cwd if cwd is not None else str(REPO_ROOT),
            "toolCall": {"name": tool_name, "args": tool_args},
        }
    )


@unittest.skipUnless(
    HOST_SHIM.is_file() and HOST_POLICY_CORE.is_file() and HOST_POLICY_TOML.is_file(),
    "Host ~/.agents/hooks/agy-hook-shim.py not installed on this runner",
)
class TestHostSecurityShimContract(unittest.TestCase):
    """End-to-end contract tests against the live host AGY security shim."""

    def test_malformed_empty_and_missing_tool_call_fail_closed(self) -> None:
        bad_inputs = [
            ("malformed_json", "{not-valid-json"),
            ("empty_stdin", ""),
            ("whitespace_stdin", "   \n  "),
            ("missing_tool_call", json.dumps({"hookEventName": "PreToolUse"})),
            ("non_dict_tool_call", json.dumps({"toolCall": "invalid"})),
        ]
        for label, raw in bad_inputs:
            with self.subTest(label=label):
                code, out = _run_shim(HOST_SHIM, raw)
                self.assertEqual(code, 0)
                self.assertEqual(out.get("decision"), "deny")

    def test_broken_import_in_isolated_copy_fails_closed_with_exit_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            isolated_shim = Path(tmp) / "agy-hook-shim.py"
            shutil.copy2(HOST_SHIM, isolated_shim)
            payload = _pre_tool_payload("run_command", {"CommandLine": "git status"})
            code, out = _run_shim(isolated_shim, payload, safe_path=True)
            self.assertEqual(code, 0)
            self.assertEqual(out.get("decision"), "deny")
            reason = out.get("reason")
            if not isinstance(reason, str):
                self.fail(f"Expected string reason, got {type(reason)}")
            self.assertIn("fail-closed", reason)

    def test_python_safe_path_still_resolves_sibling_policy_core(self) -> None:
        allow_payload = _pre_tool_payload("run_command", {"CommandLine": "git status"})
        code_ok, out_ok = _run_shim(HOST_SHIM, allow_payload, safe_path=True)
        self.assertEqual(code_ok, 0)
        self.assertEqual(out_ok.get("decision"), "allow")

        deny_payload = _pre_tool_payload(
            "read_file",
            {"Path": str(Path.home() / ".gemini" / "antigravity" / "mcp_oauth_tokens.json")},
        )
        code_deny, out_deny = _run_shim(HOST_SHIM, deny_payload, safe_path=True)
        self.assertEqual(code_deny, 0)
        self.assertEqual(out_deny.get("decision"), "deny")

    def test_blocks_file_uris_percent_encoded_traversal_and_symlinks(self) -> None:
        home = Path.home()
        home_str = str(home)
        uri_and_encoded_cases = [
            (
                "file_uri_oauth_tokens",
                "read_file",
                {"Path": f"file://{home_str}/.gemini/antigravity/mcp_oauth_tokens.json"},
            ),
            (
                "file_uri_localhost_oauth_tokens",
                "read_file",
                {"Path": f"file://localhost{home_str}/.gemini/antigravity/mcp_oauth_tokens.json"},
            ),
            (
                "encoded_traversal_raw_path",
                "read_file",
                {"Path": f"{home_str}/scratch/%2e%2e/.gemini/antigravity/mcp_oauth_tokens.json"},
            ),
            (
                "encoded_traversal_file_uri_config",
                "view_file",
                {"AbsolutePath": f"file://{home_str}/scratch/%2e%2e%2f.gemini/config/config.json"},
            ),
        ]
        for label, tool_name, args in uri_and_encoded_cases:
            with self.subTest(label=label):
                code, out = _run_shim(HOST_SHIM, _pre_tool_payload(tool_name, args))
                self.assertEqual(code, 0)
                self.assertEqual(out.get("decision"), "deny")

        with tempfile.TemporaryDirectory() as tmp:
            oauth_link = Path(tmp) / "benign_name.txt"
            oauth_link.symlink_to(home / ".gemini" / "antigravity" / "mcp_oauth_tokens.json")
            code_a, out_a = _run_shim(
                HOST_SHIM,
                _pre_tool_payload("read_file", {"Path": str(oauth_link)}, cwd=tmp),
            )
            self.assertEqual(code_a, 0)
            self.assertEqual(out_a.get("decision"), "deny")

            upstream_link = Path(tmp) / "upstream_alias.md"
            upstream_link.symlink_to(home / "Documents" / "upstream" / "pinned.md")
            code_b, out_b = _run_shim(
                HOST_SHIM,
                _pre_tool_payload("read_file", {"Path": str(upstream_link)}, cwd=tmp),
            )
            self.assertEqual(code_b, 0)
            self.assertEqual(out_b.get("decision"), "deny")

    def test_blocks_protected_reads_and_immutable_upstream(self) -> None:
        home = Path.home()
        cases = [
            ("read_config_json", "read_file", {"Path": "~/.gemini/config/config.json"}),
            ("read_mcp_config_json", "read_file", {"Path": "~/.gemini/config/mcp_config.json"}),
            (
                "read_plugin_auth_json",
                "read_file",
                {"Path": "~/.gemini/config/plugins/gdocs/auth.json"},
            ),
            (
                "read_upstream_file",
                "read_file",
                {"Path": str(home / "Documents" / "upstream" / "foo.md")},
            ),
            (
                "search_upstream_dir",
                "grep_search",
                {"SearchDirectory": str(home / "Documents" / "upstream")},
            ),
        ]
        for label, tool_name, args in cases:
            with self.subTest(label=label):
                code, out = _run_shim(HOST_SHIM, _pre_tool_payload(tool_name, args))
                self.assertEqual(code, 0)
                self.assertEqual(out.get("decision"), "deny")

    def test_blocks_self_tampering_writes_on_hooks_and_policy(self) -> None:
        cases = [
            ("write_hooks_json", "write_file", {"Path": "~/.gemini/config/hooks.json"}),
            ("edit_mcp_config", "edit_file", {"Path": "~/.gemini/config/mcp_config.json"}),
            ("write_security_policy", "write_file", {"Path": str(HOST_POLICY_TOML)}),
            ("edit_host_shim", "edit_file", {"Path": str(HOST_SHIM)}),
            ("edit_policy_core", "edit_file", {"Path": str(HOST_POLICY_CORE)}),
            ("write_hooks_dir", "write_file", {"Path": str(HOST_HOOKS_DIR)}),
        ]
        for label, tool_name, args in cases:
            with self.subTest(label=label):
                code, out = _run_shim(HOST_SHIM, _pre_tool_payload(tool_name, args))
                self.assertEqual(code, 0)
                self.assertEqual(out.get("decision"), "deny")

    def test_blocks_shell_secret_exfiltration_and_live_broker_ports(self) -> None:
        commands = [
            ("csrf_token_env", "echo $ANTIGRAVITY_CSRF_TOKEN"),
            ("cat_config_json", "cat ~/.gemini/config/config.json"),
            ("cat_mcp_config_json", "cat ~/.gemini/config/mcp_config.json"),
            ("cat_oauth_tokens", "cat ~/.gemini/antigravity/mcp_oauth_tokens.json"),
            ("cat_plugin_auth", "cat ~/.gemini/config/plugins/gdocs/auth.json"),
            ("ls_upstream", "ls ~/Documents/upstream"),
            ("ibkr_port_4001", "curl http://127.0.0.1:4001/health"),
            ("ibkr_port_7496", "curl http://localhost:7496/health"),
            ("broker_port_8798", "curl http://127.0.0.1:8798/status"),
            ("broker_port_8796", "curl http://localhost:8796/status"),
            ("alpaca_live", "curl https://api.alpaca.markets/v2/account"),
        ]
        for label, cmd in commands:
            with self.subTest(label=label):
                code, out = _run_shim(
                    HOST_SHIM,
                    _pre_tool_payload("run_command", {"CommandLine": cmd}),
                )
                self.assertEqual(code, 0)
                self.assertEqual(out.get("decision"), "deny")

    def test_allows_benign_commands_and_workspace_operations(self) -> None:
        benign_commands = [
            "git status",
            "git init",
            "git add .",
            'git commit -m "chore: seal release"',
            "python3 -m unittest discover -s tests -v",
            "python3 scripts/verify_manifest.py --verify",
            "python3 scripts/audit_ecosystem_hygiene.py --json",
            "zensical build --strict",
            "ast-grep scan",
            "ruff check .",
            "ruff format --check .",
            "ty check",
            "gitleaks git .",
            "zizmor --offline .github/workflows/sota-convergence-gates.yml",
        ]
        for cmd in benign_commands:
            with self.subTest(command=cmd):
                code, out = _run_shim(
                    HOST_SHIM,
                    _pre_tool_payload("run_command", {"CommandLine": cmd}),
                )
                self.assertEqual(code, 0)
                self.assertEqual(out.get("decision"), "allow")

        benign_file_ops = [
            ("read_repo_readme", "read_file", {"Path": str(REPO_ROOT / "README.md")}),
            (
                "write_repo_scratch",
                "write_file",
                {"Path": str(REPO_ROOT / "docs" / "example.md"), "Content": "# ok\n"},
            ),
            ("read_host_policy_readonly", "read_file", {"Path": str(HOST_POLICY_TOML)}),
            ("read_host_shim_readonly", "read_file", {"Path": str(HOST_SHIM)}),
        ]
        for label, tool_name, args in benign_file_ops:
            with self.subTest(label=label):
                code, out = _run_shim(HOST_SHIM, _pre_tool_payload(tool_name, args))
                self.assertEqual(code, 0)
                self.assertEqual(out.get("decision"), "allow")

    def test_stop_and_post_tool_use_lifecycle_contracts(self) -> None:
        stop_payload = json.dumps({"hookEventName": "Stop", "continuationActive": True})
        code_stop, out_stop = _run_shim(HOST_SHIM, stop_payload, event="Stop")
        self.assertEqual(code_stop, 0)
        self.assertEqual(out_stop, {"decision": ""})

        post_payload = json.dumps(
            {"hookEventName": "PostToolUse", "toolCall": {"name": "read_file", "args": {}}}
        )
        code_post, out_post = _run_shim(HOST_SHIM, post_payload, event="PostToolUse")
        self.assertEqual(code_post, 0)
        self.assertEqual(out_post, {})

    def test_toml_fallback_parser_matches_stdlib_tomllib(self) -> None:
        spec = importlib.util.spec_from_file_location("host_policy_core", HOST_POLICY_CORE)
        if spec is None or spec.loader is None:
            self.fail(f"Could not load module spec from {HOST_POLICY_CORE}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        raw_text = HOST_POLICY_TOML.read_text(encoding="utf-8")
        expected = tomllib.loads(raw_text)
        fallback = module._parse_toml_fallback(raw_text)
        self.assertEqual(fallback, expected)


if __name__ == "__main__":
    unittest.main()
