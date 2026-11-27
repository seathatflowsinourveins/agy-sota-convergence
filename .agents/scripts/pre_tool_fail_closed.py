#!/usr/bin/env python3
"""Fail-closed Antigravity PreToolUse security hook.

Contract (https://antigravity.google/docs/hooks.md):
- Reads camelCase JSON payload on stdin (`toolCall.name`, `toolCall.args`, ...).
- Writes JSON decision on stdout and ALWAYS exits 0 so errors fail CLOSED
  (non-zero hook exits in Antigravity fail open).
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

PROTECTED_BASENAMES: frozenset[str] = frozenset(
    {
        ".env",
        "auth.json",
        ".git-credentials",
        "_netrc",
        ".netrc",
        "mcp_oauth_tokens.json",
        "hooks.json",
        "mcp_config.json",
        "admin_settings.json",
    }
)

PROTECTED_SUFFIXES: tuple[str, ...] = (
    "/.gemini/config/config.json",
    "/.gemini/antigravity/mcp_oauth_tokens.json",
    "/Documents/upstream",
)

PROTECTED_PREFIXES: tuple[str, ...] = (
    os.path.realpath(os.path.expanduser("~/.ssh")),
    os.path.realpath(os.path.expanduser("~/.aws")),
    os.path.realpath(os.path.expanduser("~/.docker")),
    os.path.realpath(os.path.expanduser("~/.kube")),
    os.path.realpath(os.path.expanduser("~/.gemini/config/config.json")),
    os.path.realpath(os.path.expanduser("~/.gemini/antigravity/mcp_oauth_tokens.json")),
    os.path.realpath(os.path.expanduser("~/Documents/upstream")),
)

PATH_ARG_KEYS: tuple[str, ...] = (
    "AbsolutePath",
    "TargetFile",
    "Path",
    "SearchPath",
    "SearchDirectory",
    "DirectoryPath",
)

DANGEROUS_CMD_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("sudo", re.compile(r"(^|[;&|]\s*)sudo(\s|$)")),
    (
        "rm_rf",
        re.compile(r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f\b|\brm\s+-[a-zA-Z]*f[a-zA-Z]*r\b"),
    ),
    (
        "protected_file_ref",
        re.compile(
            r"(^|[\s/'\"=])(\.env(\.[A-Za-z0-9_.-]+)?|auth\.json|"
            r"mcp_oauth_tokens\.json|hooks\.json|mcp_config\.json)(\s|$|['\"])"
        ),
    ),
    (
        "protected_home_path",
        re.compile(
            r"(~|/Users/[^/\s]+|/home/[^/\s]+)/"
            r"(\.ssh|\.aws|\.docker|\.kube|\.gemini/config/config\.json|Documents/upstream)"
        ),
    ),
    ("csrf_token_ref", re.compile(r"ANTIGRAVITY_CSRF_TOKEN")),
    (
        "live_broker_port",
        re.compile(
            r"(?::|\b(?:127\.0\.0\.1|localhost|0\.0\.0\.0)\s+|--?port[=\s]+)"
            r"(?:4001|7496|8798|8796)\b"
        ),
    ),
    ("live_broker_host", re.compile(r"\bapi\.alpaca\.markets\b", re.IGNORECASE)),
)


def emit(decision: str, reason: str = "") -> None:
    """Write a single-line JSON decision payload to stdout."""
    payload: dict[str, str] = {"decision": decision}
    if reason:
        payload["reason"] = reason
    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def _normalize_raw_path(raw_path: str) -> str:
    """Decode file:// URIs (including %2e%2e traversal) into a filesystem path."""
    if raw_path.lower().startswith("file://"):
        parsed = urlparse(raw_path)
        decoded = unquote(parsed.path)
        if parsed.netloc and parsed.netloc not in ("", "localhost"):
            return f"/{parsed.netloc}{decoded}"
        return decoded
    return raw_path


def is_protected_path(raw_path: str, workspace_paths: list[str]) -> str | None:
    """Return a denial reason if raw_path resolves to a protected target, else None."""
    if not raw_path:
        return None
    cleaned = _normalize_raw_path(raw_path)
    expanded = os.path.expanduser(cleaned)
    if not os.path.isabs(expanded) and workspace_paths:
        expanded = os.path.join(workspace_paths[0], expanded)
    resolved = os.path.realpath(expanded)
    normalized_posix = resolved.replace("\\", "/")
    name = Path(resolved).name

    if name in PROTECTED_BASENAMES or name.startswith(".env."):
        return f"Blocked access to protected file '{name}' ({resolved})"
    for suffix in PROTECTED_SUFFIXES:
        if normalized_posix.endswith(suffix) or f"{suffix}/" in normalized_posix:
            return f"Blocked access to protected path pattern '{suffix}'"
    for prefix in PROTECTED_PREFIXES:
        if resolved == prefix or resolved.startswith(prefix + os.sep):
            return f"Blocked access to protected path prefix '{prefix}'"
    return None


def evaluate(event: object) -> tuple[str, str]:
    """Evaluate a parsed PreToolUse JSON event and return (decision, reason)."""
    if not isinstance(event, dict):
        return ("deny", "Malformed PreToolUse payload: root must be a JSON object")

    tool_call = event.get("toolCall")
    if not isinstance(tool_call, dict):
        return ("deny", "Malformed PreToolUse payload: missing toolCall object")

    tool_name = str(tool_call.get("name", ""))
    raw_args = tool_call.get("args")
    args: dict[str, object] = raw_args if isinstance(raw_args, dict) else {}

    raw_workspaces = event.get("workspacePaths")
    workspace_paths: list[str] = (
        [str(p) for p in raw_workspaces if isinstance(p, str)]
        if isinstance(raw_workspaces, list)
        else []
    )

    for key in PATH_ARG_KEYS:
        val = args.get(key)
        if isinstance(val, str):
            hit = is_protected_path(val, workspace_paths)
            if hit is not None:
                return ("deny", hit)

    if tool_name == "run_command":
        cmd = str(args.get("CommandLine", ""))
        for label, pattern in DANGEROUS_CMD_PATTERNS:
            if pattern.search(cmd):
                return ("deny", f"Blocked command matching protected policy '{label}'")

    return ("allow", "")


def main() -> None:
    """Entry point: always exit 0 and fail closed on any runtime error."""
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            emit("deny", "Fail-closed: empty stdin payload")
            return
        event: object = json.loads(raw)
        decision, reason = evaluate(event)
        emit(decision, reason)
    except BaseException as exc:
        emit("deny", f"Fail-closed internal hook exception: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
