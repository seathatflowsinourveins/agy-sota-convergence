#!/usr/bin/env python3
"""Reusable Google Antigravity `/run-workflow` SOTA convergence audit pipeline.

Orchestrates deterministic repository and workstation audit gates inside an
isolated `/run-workflow` script process using Antigravity's native primitives
(`phase`, `log`, `parallel`, `call_tool`, `args`, and `ToolError`) so verbose
tool output stays out of the main conversation context and only a structured
JSON summary is returned.

Args schema is defined in `workflows/workflow.json`:
- `check_host_hygiene` (bool, default True)
- `run_tests` (bool, default True)
- `strict_portal` (bool, default False)
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable, Sequence
from typing import TYPE_CHECKING, Any


class _FallbackToolError(Exception):
    """Fallback exception class when executed outside AGY `/run-workflow`."""

    tool: str = "run_command"
    message: str = ""
    denied: bool = False


if TYPE_CHECKING:
    args: dict[str, Any]

    def phase(name: str) -> None: ...
    def log(*values: object) -> None: ...
    def call_tool(name: str, **kwargs: Any) -> Awaitable[str]: ...
    def parallel[T, R](
        items: Sequence[T],
        fn: Callable[[T], Awaitable[R]],
    ) -> Awaitable[list[R]]: ...

    class ToolError(Exception):
        tool: str
        message: str
        denied: bool


class AuditConfig:
    """Validated runtime toggles parsed from `workflows/workflow.json` args."""

    __slots__ = ("check_host_hygiene", "run_tests", "strict_portal")

    def __init__(
        self,
        check_host_hygiene: bool = True,
        run_tests: bool = True,
        strict_portal: bool = False,
    ) -> None:
        self.check_host_hygiene = check_host_hygiene
        self.run_tests = run_tests
        self.strict_portal = strict_portal

    @classmethod
    def from_args(cls, raw_args: dict[str, Any]) -> AuditConfig:
        """Build an `AuditConfig` from the injected `/run-workflow` `args` dict."""
        return cls(
            check_host_hygiene=bool(raw_args.get("check_host_hygiene", True)),
            run_tests=bool(raw_args.get("run_tests", True)),
            strict_portal=bool(raw_args.get("strict_portal", False)),
        )


class GateSpec:
    """Single deterministic shell check executed via `call_tool('run_command', ...)`."""

    __slots__ = ("gate_id", "summary", "command", "wait_ms")

    def __init__(
        self,
        gate_id: str,
        summary: str,
        command: str,
        wait_ms: int = 10_000,
    ) -> None:
        self.gate_id = gate_id
        self.summary = summary
        self.command = command
        self.wait_ms = wait_ms


def _resolve_runtime() -> tuple[
    Callable[[str], None],
    Callable[..., None],
    Callable[..., Awaitable[str]],
    Callable[[Sequence[Any], Callable[[Any], Awaitable[Any]]], Awaitable[list[Any]]],
    dict[str, Any],
    type[Exception],
]:
    """Resolve injected `/run-workflow` runtime globals cleanly without fail-open fallbacks."""
    ns = globals()
    injected_call_tool = ns.get("call_tool")
    injected_parallel = ns.get("parallel")
    if not callable(injected_call_tool) or not callable(injected_parallel):
        raise RuntimeError(
            "workflows/sota_convergence_audit.py must be executed via Antigravity "
            "`/run-workflow` (missing injected `call_tool` / `parallel` runtime primitives)."
        )

    def _default_phase(name: str) -> None:
        print(f"[phase] {name}")

    def _default_log(*values: object) -> None:
        print(*values)

    phase_fn: Callable[[str], None] = ns.get("phase", _default_phase)
    log_fn: Callable[..., None] = ns.get("log", _default_log)
    raw_args = ns.get("args")
    args_dict: dict[str, Any] = raw_args if isinstance(raw_args, dict) else {}
    tool_error_cls = ns.get("ToolError", _FallbackToolError)
    if not (isinstance(tool_error_cls, type) and issubclass(tool_error_cls, Exception)):
        tool_error_cls = _FallbackToolError

    return phase_fn, log_fn, injected_call_tool, injected_parallel, args_dict, tool_error_cls


def build_core_gates() -> list[GateSpec]:
    """Return the always-on deterministic verification gates."""
    return [
        GateSpec(
            gate_id="manifest_verify",
            summary="Verify sealed compounding manifest (18 gates)",
            command="python3 scripts/verify_manifest.py --verify",
        ),
        GateSpec(
            gate_id="ast_grep_scan",
            summary="Run ast-grep structural ban rules (including .agents/ and .github/)",
            command="ast-grep scan --no-ignore hidden",
        ),
        GateSpec(
            gate_id="ruff_and_ty",
            summary="Run ruff lint, format check, and ty typecheck",
            command="ruff check . && ruff format --check . && ty check",
        ),
    ]


def build_optional_gates(config: AuditConfig) -> list[GateSpec]:
    """Return optional gates enabled by `workflows/workflow.json` arguments."""
    gates: list[GateSpec] = []
    if config.check_host_hygiene:
        gates.append(
            GateSpec(
                gate_id="host_ecosystem_hygiene",
                summary="Audit read-only local AGY ecosystem hygiene",
                command="python3 scripts/audit_ecosystem_hygiene.py --json --strict",
            )
        )
    if config.run_tests:
        gates.append(
            GateSpec(
                gate_id="unit_and_contract_tests",
                summary="Run stdlib unit, mutation, and hook contract tests",
                command="python3 -m unittest discover -s tests -v",
            )
        )
    if config.strict_portal:
        gates.append(
            GateSpec(
                gate_id="zensical_strict_portal",
                summary="Build static MADR 4.0.0 ADR portal strictly",
                command="zensical build --strict",
            )
        )
    return gates


def _tail_excerpt(text: str, max_lines: int = 8) -> str:
    """Keep summary excerpts concise to protect the main conversation context."""
    lines = [line for line in text.strip().splitlines() if line.strip()]
    if len(lines) <= max_lines:
        return "\n".join(lines)
    return "\n".join(lines[-max_lines:])


async def _run_gate(
    spec: GateSpec,
    call_tool_fn: Callable[..., Awaitable[str]],
    tool_error_cls: type[Exception],
) -> dict[str, Any]:
    """Execute one gate via `call_tool('run_command', ...)` and classify outcome."""
    try:
        output = await call_tool_fn(
            "run_command",
            CommandLine=spec.command,
            WaitMsBeforeAsync=spec.wait_ms,
            toolSummary=spec.summary,
        )
        return {
            "gate_id": spec.gate_id,
            "command": spec.command,
            "status": "PASS",
            "denied": False,
            "excerpt": _tail_excerpt(output),
        }
    except tool_error_cls as exc:
        denied = bool(getattr(exc, "denied", False))
        message = str(getattr(exc, "message", "") or exc)
        return {
            "gate_id": spec.gate_id,
            "command": spec.command,
            "status": "DENIED" if denied else "FAIL",
            "denied": denied,
            "excerpt": _tail_excerpt(message),
        }


async def run_audit(config_override: AuditConfig | None = None) -> dict[str, Any]:
    """Run the phased `/run-workflow` convergence audit and return structured JSON data."""
    phase_fn, log_fn, call_tool_fn, parallel_fn, raw_args, tool_error_cls = _resolve_runtime()
    config = config_override if config_override is not None else AuditConfig.from_args(raw_args)

    phase_fn("Core Repository Gates")
    core_specs = build_core_gates()
    core_results: list[dict[str, Any]] = await parallel_fn(
        core_specs,
        lambda spec: _run_gate(spec, call_tool_fn, tool_error_cls),
    )
    for item in core_results:
        log_fn(f"[{item['status']}] {item['gate_id']}: {item['command']}")

    optional_specs = build_optional_gates(config)
    optional_results: list[dict[str, Any]] = []
    if optional_specs:
        phase_fn("Configured Extended Gates")
        optional_results = await parallel_fn(
            optional_specs,
            lambda spec: _run_gate(spec, call_tool_fn, tool_error_cls),
        )
        for item in optional_results:
            log_fn(f"[{item['status']}] {item['gate_id']}: {item['command']}")

    phase_fn("Aggregate Summary")
    all_results = core_results + optional_results
    passed = sum(1 for item in all_results if item["status"] == "PASS")
    failed = sum(1 for item in all_results if item["status"] == "FAIL")
    denied = sum(1 for item in all_results if item["status"] == "DENIED")

    report: dict[str, Any] = {
        "workflow": "sota-convergence-audit",
        "config": {
            "check_host_hygiene": config.check_host_hygiene,
            "run_tests": config.run_tests,
            "strict_portal": config.strict_portal,
        },
        "summary": {
            "overall_status": "PASS" if failed == 0 and denied == 0 else "FAIL",
            "total": len(all_results),
            "passed": passed,
            "failed": failed,
            "denied": denied,
        },
        "gates": all_results,
    }
    log_fn(
        f"Audit {report['summary']['overall_status']}: "
        f"{passed}/{len(all_results)} passed, {failed} failed, {denied} denied."
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return report


def _entrypoint() -> None:
    """Execute `run_audit()` cleanly when invoked inside AGY `/run-workflow`."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(run_audit())
    else:
        loop.create_task(run_audit())


if __name__ == "__main__":
    _entrypoint()
