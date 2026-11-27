#!/usr/bin/env python3
"""Read-only, zero-secret local Google Antigravity (AGY) ecosystem hygiene auditor.

Audits non-secret customization files under ``~/.gemini/`` and ``~/.agents/``:
- Global rule files (``GEMINI.md`` / ``AGENTS.md``) against <=45L, <=1,600c, and 20k-token budgets.
- Modular rules (``~/.gemini/config/rules/*.md``) for snake_case YAML ``trigger:`` and 24 KB caps.
- Skill roots (``~/.gemini/config/skills``, ``~/.gemini/skills``, ``~/.gemini/antigravity-cli/skills``,
  ``~/.agents/skills``) for hard-copied duplicates, hash drift, >1-level nesting, and >1,024-char
  descriptions.
- Hooks structure (``~/.gemini/config/hooks.json``) for valid JSON, ``PreToolUse`` gate presence,
  and stale ``.bak`` leftovers (never prints env/token values).
- Retiring 2026-11-30 model slugs and deprecated legacy patterns across non-secret ``.md`` files.

SECURITY INVARIANT:
Strictly read-only. Never opens ``.env*``, ``config.json``, ``mcp_config.json``,
``settings.json``, ``mcp_oauth_tokens.json``, ``auth.json``, or ``~/Documents/upstream/``.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

FORBIDDEN_FILENAMES: frozenset[str] = frozenset(
    {
        "config.json",
        "mcp_config.json",
        "settings.json",
        "mcp_oauth_tokens.json",
        "auth.json",
    }
)
FORBIDDEN_PATH_PARTS: frozenset[str] = frozenset({"upstream", ".ssh", ".aws"})
VALID_RULE_TRIGGERS: frozenset[str] = frozenset({"always_on", "model_decision", "glob", "manual"})

RETIRING_NOV30_RE = re.compile(
    r"\b(gemini[-_ ]?4[-_ ]?argon|gemini[-_ ]?3[._-]8|gpt[-_ ]?oss[-_ ]?120b|"
    r"claude[-_ ]?(?:sonnet|opus)?[-_ ]?4[._-]6)\b",
    re.IGNORECASE,
)
LEGACY_PATTERN_RE = re.compile(
    r"(jetski|\.agents/workflows|global_workflows|\.agents/settings\.json|"
    r"\bunsandboxed\b|McpSseServer|START_SUBAGENT)",
    re.IGNORECASE,
)
FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", re.DOTALL)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

RULE_FILE_MAX_BYTES = 24_000
RULES_AGGREGATE_MAX_TOKENS = 20_000
GLOBAL_CHARTER_MAX_LINES = 45
GLOBAL_CHARTER_MAX_CHARS = 1_600
SKILL_NAME_MAX_CHARS = 64
SKILL_DESC_MAX_CHARS = 1_024
SKILL_DESC_NEAR_CAP_CHARS = 950


def _is_forbidden_path(path: Path) -> bool:
    name_lower = path.name.lower()
    if name_lower == ".env" or name_lower.startswith(".env."):
        return True
    if name_lower in FORBIDDEN_FILENAMES:
        return True
    return any(part in FORBIDDEN_PATH_PARTS for part in path.parts)


def _safe_read_text(path: Path) -> str:
    if _is_forbidden_path(path):
        raise PermissionError(f"Refused to read forbidden path: {path.name}")
    return path.read_text(encoding="utf-8", errors="replace")


def _safe_sha256_prefix(path: Path) -> str:
    if _is_forbidden_path(path):
        raise PermissionError(f"Refused to hash forbidden path: {path.name}")
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def _parse_frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    if not text.startswith("---"):
        return None, "missing_frontmatter"
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, "unclosed_frontmatter"
    raw = match.group(1)
    fields: dict[str, str] = {}
    name_match = re.search(r"^name:\s*(.+)$", raw, re.MULTILINE)
    if name_match:
        fields["name"] = name_match.group(1).strip().strip("'\"")
    trigger_match = re.search(
        r"^([A-Za-z0-9_-]*trigger[A-Za-z0-9_-]*):\s*(.+)$", raw, re.MULTILINE | re.IGNORECASE
    )
    if trigger_match:
        fields[trigger_match.group(1).strip()] = trigger_match.group(2).strip().strip("'\"")
    desc_match = re.search(
        r"^description:\s*(.*?)(?=\n[A-Za-z0-9_-]+:|\Z)", raw, re.MULTILINE | re.DOTALL
    )
    if desc_match:
        fields["description"] = desc_match.group(1).strip().strip("'\"")
    return fields, "ok"


def audit_global_rules(home: Path) -> tuple[dict[str, Any], list[dict[str, str]]]:
    findings: list[dict[str, str]] = []
    candidates = [
        home / ".gemini" / "GEMINI.md",
        home / ".gemini" / "AGENTS.md",
        home / ".gemini" / "config" / "GEMINI.md",
        home / ".gemini" / "config" / "AGENTS.md",
    ]
    present: list[dict[str, Any]] = []
    total_chars = 0
    for path in candidates:
        if not path.exists() or not path.is_file():
            continue
        text = _safe_read_text(path)
        size_bytes = path.stat().st_size
        line_count = len(text.splitlines())
        char_count = len(text)
        comment_chars = sum(len(m.group(0)) for m in HTML_COMMENT_RE.finditer(text))
        total_chars += char_count
        entry = {
            "path": str(path),
            "is_symlink": path.is_symlink(),
            "resolved": str(path.resolve()),
            "bytes": size_bytes,
            "lines": line_count,
            "chars": char_count,
            "est_tokens": char_count // 4,
            "html_comment_chars": comment_chars,
            "sha256_prefix": _safe_sha256_prefix(path),
        }
        present.append(entry)
        if size_bytes > RULE_FILE_MAX_BYTES:
            findings.append(
                {
                    "severity": "HIGH",
                    "code": "RULE_OVER_24KB",
                    "detail": f"{path.name} is {size_bytes} bytes (cap {RULE_FILE_MAX_BYTES}).",
                }
            )
        if line_count > GLOBAL_CHARTER_MAX_LINES or char_count > GLOBAL_CHARTER_MAX_CHARS:
            findings.append(
                {
                    "severity": "MEDIUM",
                    "code": "GLOBAL_CHARTER_BLOAT",
                    "detail": (
                        f"{path} has {line_count}L/{char_count}c "
                        f"(target <={GLOBAL_CHARTER_MAX_LINES}L, <={GLOBAL_CHARTER_MAX_CHARS}c)."
                    ),
                }
            )
    resolved_set = {item["resolved"] for item in present}
    if len(resolved_set) > 1:
        findings.append(
            {
                "severity": "HIGH",
                "code": "DUPLICATE_GLOBAL_CHARTERS",
                "detail": (
                    f"{len(resolved_set)} distinct global rule files loaded cumulatively: "
                    f"{[item['path'] for item in present]}"
                ),
            }
        )

    modular_rules: list[dict[str, Any]] = []
    rules_dir = home / ".gemini" / "config" / "rules"
    if rules_dir.exists() and rules_dir.is_dir():
        for md_file in sorted(rules_dir.rglob("*.md")):
            rel = md_file.relative_to(rules_dir)
            depth = len(rel.parts) - 1
            text = _safe_read_text(md_file)
            size_bytes = md_file.stat().st_size
            total_chars += len(text)
            fields, status = _parse_frontmatter(text)
            modular_rules.append(
                {"file": str(rel), "bytes": size_bytes, "depth": depth, "status": status}
            )
            if depth >= 1:
                findings.append(
                    {
                        "severity": "MEDIUM",
                        "code": "NESTED_RULE_SKIPPED",
                        "detail": f"~/.gemini/config/rules/{rel} is nested >1 level and silently skipped.",
                    }
                )
            if size_bytes > RULE_FILE_MAX_BYTES:
                findings.append(
                    {
                        "severity": "HIGH",
                        "code": "RULE_OVER_24KB",
                        "detail": f"rules/{rel} is {size_bytes} bytes (cap {RULE_FILE_MAX_BYTES}).",
                    }
                )
            if status != "ok" or fields is None:
                findings.append(
                    {
                        "severity": "HIGH",
                        "code": "RULE_BAD_FRONTMATTER",
                        "detail": f"rules/{rel} frontmatter error ({status}); silently discarded by AGY.",
                    }
                )
            else:
                trigger_val = fields.get("trigger")
                if trigger_val not in VALID_RULE_TRIGGERS:
                    findings.append(
                        {
                            "severity": "HIGH",
                            "code": "RULE_INVALID_TRIGGER",
                            "detail": f"rules/{rel} has invalid/non-snake_case trigger: {trigger_val!r}.",
                        }
                    )

    est_tokens = total_chars // 4
    if est_tokens > RULES_AGGREGATE_MAX_TOKENS:
        findings.append(
            {
                "severity": "HIGH",
                "code": "RULES_BUDGET_EXCEEDED",
                "detail": f"Aggregate rules ~{est_tokens} tokens exceed {RULES_AGGREGATE_MAX_TOKENS}-token budget.",
            }
        )

    return {
        "global_files": present,
        "modular_rules": modular_rules,
        "aggregate_est_tokens": est_tokens,
        "budget_tokens": RULES_AGGREGATE_MAX_TOKENS,
    }, findings


def audit_hooks(home: Path) -> tuple[dict[str, Any], list[dict[str, str]]]:
    findings: list[dict[str, str]] = []
    cfg = home / ".gemini" / "config"
    hooks_path = cfg / "hooks.json"
    bak_path = cfg / "hooks.json.bak"

    result: dict[str, Any] = {
        "exists": hooks_path.exists(),
        "stale_backup_exists": bak_path.exists(),
        "groups": {},
        "has_security_pretool_gate": False,
    }
    if bak_path.exists():
        findings.append(
            {
                "severity": "LOW",
                "code": "STALE_HOOKS_BACKUP",
                "detail": "Stale ~/.gemini/config/hooks.json.bak present on disk.",
            }
        )
    if not hooks_path.exists():
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "MISSING_GLOBAL_HOOKS",
                "detail": "No global ~/.gemini/config/hooks.json configured.",
            }
        )
        return result, findings

    try:
        raw = json.loads(_safe_read_text(hooks_path))
    except json.JSONDecodeError as exc:
        findings.append(
            {
                "severity": "HIGH",
                "code": "HOOKS_JSON_INVALID",
                "detail": f"Invalid JSON in ~/.gemini/config/hooks.json: {exc.msg}.",
            }
        )
        return result, findings

    if isinstance(raw, dict):
        for group_name, group_val in raw.items():
            if not isinstance(group_val, dict):
                continue
            events = sorted(k for k in group_val if k != "enabled")
            result["groups"][group_name] = {
                "enabled": group_val.get("enabled", True),
                "events": events,
            }
            if (
                group_val.get("enabled", True) is not False
                and "PreToolUse" in group_val
                and group_name != "orca-status"
            ):
                result["has_security_pretool_gate"] = True

    if not result["has_security_pretool_gate"]:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "NO_SECURITY_PRETOOL_HOOK",
                "detail": "No dedicated non-telemetry PreToolUse security gate found in hooks.json.",
            }
        )
    return result, findings


def audit_skills_and_scans(home: Path) -> tuple[dict[str, Any], list[dict[str, str]]]:
    findings: list[dict[str, str]] = []
    roots: dict[str, Path] = {
        "config_skills": home / ".gemini" / "config" / "skills",
        "gemini_skills": home / ".gemini" / "skills",
        "cli_skills": home / ".gemini" / "antigravity-cli" / "skills",
        "agents_skills": home / ".agents" / "skills",
    }

    root_counts: dict[str, int] = {}
    by_skill: dict[str, dict[str, tuple[bool, str, str]]] = {}
    nested_skips: list[str] = []
    frontmatter_errors: list[str] = []
    over_1024_desc: list[dict[str, Any]] = []
    near_cap_over_950c: list[dict[str, Any]] = []
    retiring_model_hits: list[dict[str, Any]] = []
    legacy_hits: list[dict[str, Any]] = []
    md_files_scanned = 0

    for label, root in roots.items():
        if not root.exists() or not root.is_dir():
            root_counts[label] = 0
            continue
        direct_count = 0
        for child in sorted(root.iterdir()):
            if not child.is_dir():
                continue
            skill_md = child / "SKILL.md"
            if skill_md.exists():
                direct_count += 1
                by_skill.setdefault(child.name, {})[label] = (
                    child.is_symlink(),
                    str(child.resolve()),
                    _safe_sha256_prefix(skill_md),
                )
            else:
                for nested in child.rglob("SKILL.md"):
                    nested_skips.append(f"{label}/{nested.relative_to(root)}")
        root_counts[label] = direct_count

        for md_file in sorted(root.rglob("*.md")):
            if _is_forbidden_path(md_file):
                continue
            md_files_scanned += 1
            text = _safe_read_text(md_file)
            rel = f"{label}/{md_file.relative_to(root)}"
            for lineno, line in enumerate(text.splitlines(), 1):
                m_model = RETIRING_NOV30_RE.search(line)
                if m_model:
                    retiring_model_hits.append(
                        {"file": rel, "line": lineno, "match": m_model.group(0)}
                    )
                m_legacy = LEGACY_PATTERN_RE.search(line)
                if m_legacy:
                    legacy_hits.append({"file": rel, "line": lineno, "match": m_legacy.group(0)})

    # Inspect canonical skill frontmatter once per unique resolved SKILL.md
    seen_real: set[str] = set()
    total_desc_chars = 0
    for skill_name, locs in sorted(by_skill.items()):
        first_label = next(iter(locs))
        skill_md = roots[first_label] / skill_name / "SKILL.md"
        real_key = str(skill_md.resolve())
        if real_key in seen_real:
            continue
        seen_real.add(real_key)
        text = _safe_read_text(skill_md)
        fields, status = _parse_frontmatter(text)
        if status != "ok" or fields is None:
            frontmatter_errors.append(f"{skill_name}: {status}")
            continue
        fm_name = fields.get("name", "")
        fm_desc = fields.get("description", "")
        total_desc_chars += len(fm_desc)
        if not fm_name or len(fm_name) > SKILL_NAME_MAX_CHARS:
            frontmatter_errors.append(f"{skill_name}: invalid name length ({len(fm_name)})")
        if fm_name and fm_name != skill_name:
            frontmatter_errors.append(f"{skill_name}: folder != frontmatter name ({fm_name})")
        if len(fm_desc) > SKILL_DESC_MAX_CHARS:
            over_1024_desc.append({"skill": skill_name, "desc_chars": len(fm_desc)})
        if len(fm_desc) > SKILL_DESC_NEAR_CAP_CHARS:
            near_cap_over_950c.append(
                {
                    "skill": skill_name,
                    "desc_chars": len(fm_desc),
                    "headroom_1024": SKILL_DESC_MAX_CHARS - len(fm_desc),
                }
            )

    # Also scan global GEMINI.md / AGENTS.md for retiring models and legacy patterns
    for gfile in (home / ".gemini" / "GEMINI.md", home / ".gemini" / "AGENTS.md"):
        if gfile.exists() and gfile.is_file():
            md_files_scanned += 1
            text = _safe_read_text(gfile)
            for lineno, line in enumerate(text.splitlines(), 1):
                m_model = RETIRING_NOV30_RE.search(line)
                if m_model:
                    retiring_model_hits.append(
                        {"file": gfile.name, "line": lineno, "match": m_model.group(0)}
                    )
                m_legacy = LEGACY_PATTERN_RE.search(line)
                if m_legacy:
                    legacy_hits.append(
                        {"file": gfile.name, "line": lineno, "match": m_legacy.group(0)}
                    )

    hard_copied_dups = [
        name
        for name, locs in sorted(by_skill.items())
        if len(locs) > 1 and len({v[1] for v in locs.values()}) > 1
    ]
    divergent_hashes = [
        name
        for name, locs in sorted(by_skill.items())
        if len(locs) > 1 and len({v[2] for v in locs.values()}) > 1
    ]

    if root_counts.get("gemini_skills", 0) > 0 or root_counts.get("cli_skills", 0) > 0:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "CLI_SHADOW_SKILL_ROOT_NONEMPTY",
                "detail": (
                    f"CLI-only override roots non-empty: gemini_skills={root_counts['gemini_skills']}, "
                    f"cli_skills={root_counts['cli_skills']}."
                ),
            }
        )
    if hard_copied_dups:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "HARD_COPIED_SKILL_DUPLICATES",
                "detail": f"{len(hard_copied_dups)} skills are unlinked hard copies across multiple roots.",
            }
        )
    if divergent_hashes:
        findings.append(
            {
                "severity": "HIGH",
                "code": "DIVERGENT_SKILL_CONTENT",
                "detail": f"{len(divergent_hashes)} duplicate skills have divergent SHA-256 content: {divergent_hashes}",
            }
        )
    if over_1024_desc:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "SKILL_DESC_OVER_1024",
                "detail": f"Skills exceeding 1,024-char description cap: {over_1024_desc}",
            }
        )
    if nested_skips:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "NESTED_SKILL_SKIPPED",
                "detail": f"Nested >1-level skills silently skipped: {nested_skips}",
            }
        )
    if frontmatter_errors:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "SKILL_FRONTMATTER_ERROR",
                "detail": f"Skill frontmatter errors: {frontmatter_errors}",
            }
        )
    if retiring_model_hits:
        findings.append(
            {
                "severity": "HIGH",
                "code": "RETIRING_NOV30_MODEL_REF",
                "detail": f"{len(retiring_model_hits)} retiring 2026-11-30 model references found.",
            }
        )
    if legacy_hits:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "LEGACY_PATTERN_REF",
                "detail": f"{len(legacy_hits)} deprecated legacy pattern references found.",
            }
        )

    return {
        "root_counts": root_counts,
        "unique_user_skills": len(by_skill),
        "hard_copied_duplicate_count": len(hard_copied_dups),
        "divergent_hash_count": len(divergent_hashes),
        "nested_skipped_skills": nested_skips,
        "over_1024_descriptions": over_1024_desc,
        "near_cap_over_950c": near_cap_over_950c,
        "upfront_description_chars": total_desc_chars,
        "upfront_description_est_tokens": total_desc_chars // 4,
        "md_files_scanned": md_files_scanned,
        "retiring_nov30_model_hits": retiring_model_hits,
        "legacy_pattern_hits": legacy_hits,
    }, findings


def audit_plugins_and_sidecars(home: Path) -> tuple[dict[str, Any], list[dict[str, str]]]:
    findings: list[dict[str, str]] = []
    cfg = home / ".gemini" / "config"

    plugins: list[dict[str, Any]] = []
    pdir = cfg / "plugins"
    if pdir.exists() and pdir.is_dir():
        for d in sorted(pdir.iterdir()):
            if not d.is_dir():
                continue
            manifest = d / "plugin.json"
            if not manifest.exists():
                manifest = d / ".antigravity-plugin" / "plugin.json"
            version = "missing_manifest"
            if manifest.exists():
                try:
                    data = json.loads(_safe_read_text(manifest))
                    version = str(data.get("version", "unversioned"))
                except json.JSONDecodeError:
                    version = "invalid_json"
            plugins.append({"dir": d.name, "version": version})

    sidecars: list[dict[str, Any]] = []
    sdir = cfg / "sidecars"
    if sdir.exists() and sdir.is_dir():
        for d in sorted(sdir.iterdir()):
            if not d.is_dir():
                continue
            sjson = d / "sidecar.json"
            if not sjson.exists():
                sidecars.append({"id": d.name, "valid": False})
                continue
            try:
                data = json.loads(_safe_read_text(sjson))
                args = data.get("args") if isinstance(data.get("args"), list) else []
                has_cron_tz = bool(
                    args and isinstance(args[0], str) and args[0].startswith("CRON_TZ=")
                )
                perms = data.get("agent_permissions") or {}
                grants = perms.get("access_grants") if isinstance(perms, dict) else []
                grants_mcp_cfg = any("mcp_config.json" in str(g) for g in (grants or []))
                if grants_mcp_cfg:
                    findings.append(
                        {
                            "severity": "LOW",
                            "code": "SIDECAR_GRANTS_MCP_CONFIG",
                            "detail": f"Sidecar '{d.name}' grants unattended read_file on mcp_config.json.",
                        }
                    )
                sidecars.append(
                    {
                        "id": d.name,
                        "builtin": data.get("builtin"),
                        "restart_policy": data.get("restart_policy"),
                        "has_cron_tz": has_cron_tz,
                    }
                )
            except json.JSONDecodeError:
                sidecars.append({"id": d.name, "valid": False})

    return {"plugins": plugins, "sidecars": sidecars}, findings


def audit_mcp_cache(home: Path) -> dict[str, Any]:
    """Count lazy-cached MCP tool schema files under ~/.gemini/antigravity/mcp/ without reading secrets."""
    mcp_dir = home / ".gemini" / "antigravity" / "mcp"
    servers: dict[str, int] = {}
    total_tools = 0
    total_tool_name_chars = 0
    total_instructions_chars = 0
    total_deferred_schema_bytes = 0

    if mcp_dir.exists() and mcp_dir.is_dir():
        for d in sorted(mcp_dir.iterdir()):
            if not d.is_dir() or _is_forbidden_path(d):
                continue
            json_files = [
                f
                for f in sorted(d.iterdir())
                if f.is_file() and f.suffix == ".json" and not _is_forbidden_path(f)
            ]
            servers[d.name] = len(json_files)
            total_tools += len(json_files)
            for jf in json_files:
                total_tool_name_chars += len(jf.stem)
                total_deferred_schema_bytes += jf.stat().st_size
            inst = d / "instructions.md"
            if inst.is_file() and not _is_forbidden_path(inst):
                total_instructions_chars += len(_safe_read_text(inst))

    return {
        "servers": servers,
        "total_cached_tools": total_tools,
        "lazy_index_est_tokens": (total_tool_name_chars + total_instructions_chars) // 4,
        "deferred_schema_est_tokens": total_deferred_schema_bytes // 4,
    }


def _build_context_manifest_scorecard(
    rules_data: dict[str, Any],
    skills_data: dict[str, Any],
    ext_data: dict[str, Any],
    mcp_cache: dict[str, Any],
) -> dict[str, Any]:
    global_files: list[dict[str, Any]] = rules_data["global_files"]
    charter_lines = sum(int(item["lines"]) for item in global_files)
    charter_chars = sum(int(item["chars"]) for item in global_files)
    charter_est_tokens = charter_chars // 4
    charter_comment_chars = sum(int(item.get("html_comment_chars", 0)) for item in global_files)
    within_cap = (
        len(global_files) <= 1
        and charter_lines <= GLOBAL_CHARTER_MAX_LINES
        and charter_chars <= GLOBAL_CHARTER_MAX_CHARS
    )
    est_desc_tokens = int(skills_data["upfront_description_est_tokens"])
    mcp_lazy_tokens = int(mcp_cache["lazy_index_est_tokens"])
    return {
        "global_charter": {
            "lines": charter_lines,
            "chars": charter_chars,
            "est_tokens": charter_est_tokens,
            "html_comment_chars": charter_comment_chars,
            "within_45L_1600c": within_cap,
        },
        "global_skills": {
            "count": int(skills_data["unique_user_skills"]),
            "total_desc_chars": int(skills_data["upfront_description_chars"]),
            "est_desc_tokens": est_desc_tokens,
            "near_cap_over_950c": skills_data["near_cap_over_950c"],
        },
        "plugins_count": len(ext_data["plugins"]),
        "sidecars_count": len(ext_data["sidecars"]),
        "mcp_cached_servers": mcp_cache["servers"],
        "mcp_total_cached_tools": int(mcp_cache["total_cached_tools"]),
        "mcp_lazy_index_est_tokens": mcp_lazy_tokens,
        "mcp_deferred_schema_est_tokens": int(mcp_cache["deferred_schema_est_tokens"]),
        "total_startup_context_est_tokens": charter_est_tokens + est_desc_tokens + mcp_lazy_tokens,
    }


def run_audit(home: Path) -> dict[str, Any]:
    rules_data, f_rules = audit_global_rules(home)
    hooks_data, f_hooks = audit_hooks(home)
    skills_data, f_skills = audit_skills_and_scans(home)
    ext_data, f_ext = audit_plugins_and_sidecars(home)
    mcp_cache = audit_mcp_cache(home)
    scorecard = _build_context_manifest_scorecard(rules_data, skills_data, ext_data, mcp_cache)

    all_findings = f_rules + f_hooks + f_skills + f_ext
    counts = {
        "HIGH": sum(1 for f in all_findings if f["severity"] == "HIGH"),
        "MEDIUM": sum(1 for f in all_findings if f["severity"] == "MEDIUM"),
        "LOW": sum(1 for f in all_findings if f["severity"] == "LOW"),
    }
    return {
        "schema_version": "1.1.0",
        "audited_at_utc": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "security_boundary": {
            "read_only": True,
            "secrets_accessed": False,
            "excluded_files": sorted(FORBIDDEN_FILENAMES) + [".env*", "~/Documents/upstream/"],
        },
        "summary": {
            "total_findings": len(all_findings),
            "severity_counts": counts,
            "status": "PASS" if counts["HIGH"] == 0 else "WARN",
        },
        "context_manifest_scorecard": scorecard,
        "rules": rules_data,
        "hooks": hooks_data,
        "skills": skills_data,
        "plugins": ext_data["plugins"],
        "sidecars": ext_data["sidecars"],
        "findings": all_findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only zero-secret local Google Antigravity ecosystem hygiene auditor."
    )
    parser.add_argument("--json", action="store_true", help="Emit structured JSON output.")
    parser.add_argument(
        "--home",
        type=Path,
        default=Path.home(),
        help="Override home directory (default: current user home).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 if any HIGH-severity finding is detected.",
    )
    args = parser.parse_args(argv)
    report = run_audit(args.home)

    if args.json:
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        s = report["summary"]
        sc = report["context_manifest_scorecard"]
        gc = sc["global_charter"]
        gs = sc["global_skills"]
        print(f"AGY Ecosystem Hygiene Audit ({report['audited_at_utc']}): {s['status']}")
        print(
            f"  Rules: {len(report['rules']['global_files'])} global file(s), "
            f"~{report['rules']['aggregate_est_tokens']} est. tokens "
            f"(budget {report['rules']['budget_tokens']})"
        )
        print(
            f"  Skills: {report['skills']['unique_user_skills']} unique, "
            f"hard_dups={report['skills']['hard_copied_duplicate_count']}, "
            f"nov30_hits={len(report['skills']['retiring_nov30_model_hits'])}, "
            f"legacy_hits={len(report['skills']['legacy_pattern_hits'])}"
        )
        print(
            f"  Hooks: groups={sorted(report['hooks']['groups'].keys())}, "
            f"security_pretool_gate={report['hooks']['has_security_pretool_gate']}"
        )
        print(
            f"  Context Scorecard: charter={gc['lines']}L/{gc['chars']}c "
            f"(~{gc['est_tokens']} tok, html_comments={gc['html_comment_chars']}c, "
            f"within_45L_1600c={gc['within_45L_1600c']}), "
            f"skills={gs['count']} (~{gs['est_desc_tokens']} tok, "
            f"near_cap_over_950c={len(gs['near_cap_over_950c'])}), "
            f"plugins={sc['plugins_count']}, sidecars={sc['sidecars_count']}"
        )
        print(
            f"  MCP Lazy Cache: servers={sc['mcp_cached_servers']} "
            f"(tools={sc['mcp_total_cached_tools']}, lazy=~{sc['mcp_lazy_index_est_tokens']} tok, "
            f"deferred=~{sc['mcp_deferred_schema_est_tokens']} tok), "
            f"total_startup_est_tokens=~{sc['total_startup_context_est_tokens']}"
        )
        print(f"  Findings ({s['total_findings']}): {s['severity_counts']}")
        for finding in report["findings"]:
            print(f"    [{finding['severity']}] {finding['code']}: {finding['detail']}")

    if args.strict and report["summary"]["severity_counts"]["HIGH"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
