#!/usr/bin/env python3
"""Stdlib-only 17-gate sealer and verifier for the SOTA Convergence & Compounding Manifest.

Usage:
    python3 scripts/verify_manifest.py --seal
    python3 scripts/verify_manifest.py --verify
    python3 scripts/verify_manifest.py --verify --manifest <path> --schema <path> [--repo-root <dir>]

Zero third-party dependencies (Python 3 stdlib only). Exits 0 on full 17/17 pass,
and 1 on any schema, semantic, ADR MADR-4, ADR SHA-256 parity, clean-install coverage,
saturation proof, repo hygiene/anti-bloat ratchet, upstream registry/map parity,
repo scaffolding/portal integrity, security, sunset, placeholder, or root SHA-256 failure.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO_ROOT / "manifest" / "compounding_manifest.v2.json"
DEFAULT_SCHEMA = REPO_ROOT / "manifest" / "compounding_manifest.v2.schema.json"

EXPECTED_LAYERS = [f"L{i}" for i in range(11)]
EXPECTED_FLYWHEEL_STAGES = [
    "capture",
    "distill",
    "deduplicate",
    "evaluate_gate",
    "promote_escalate",
    "consolidate_memory",
    "prune_gc_ratchet",
]
EXPECTED_ROUTE_IDS = [
    "conversation_service",
    "sidecars_agentapi",
    "swarm_board",
    "dynamic_workflows",
    "subagents",
    "lifecycle_hooks",
    "remote_ssh_acp",
    "orca_heterogeneous",
    "a2a_v1",
]
EXPECTED_ADR_BIJECTION: list[tuple[str, str]] = [
    ("ADR-0001", "META"),
    ("ADR-0002", "L0"),
    ("ADR-0003", "L1"),
    ("ADR-0004", "L2"),
    ("ADR-0005", "L3"),
    ("ADR-0006", "L4"),
    ("ADR-0007", "L5"),
    ("ADR-0008", "L6"),
    ("ADR-0009", "L7"),
    ("ADR-0010", "L8"),
    ("ADR-0011", "L9"),
    ("ADR-0012", "L10"),
]
REQUIRED_FRONTMATTER_KEYS = [
    "id",
    "layer",
    "status",
    "date",
    "decision-makers",
    "consulted",
    "informed",
]
REQUIRED_MADR4_HEADINGS = [
    "## Context and Problem Statement",
    "## Decision Drivers",
    "## Considered Options",
    "## Decision Outcome",
    "### Consequences",
    "### Confirmation",
    "## Pros and Cons of the Options",
    "## Clean Upstream Installation & Adapter Boundary",
    "## More Information",
]
VALID_RULE_TRIGGERS = {"always_on", "glob", "model_decision", "manual"}

AGENTS_MD_MAX_LINES = 45
AGENTS_MD_MAX_CHARS = 1600
SKILL_DESC_MAX_CHARS = 1024
RULE_FILE_MAX_BYTES = 24000

RETIRING_NOV30_RE = re.compile(
    r"(?i)(gemini[-_ ]?4[-_ ]?argon|gemini[-_ ]?3[._-]8|gpt[-_ ]?oss[-_ ]?120b|claude[-_ ]?(?:sonnet|opus)?[-_ ]?4[._-]6)"
)
PLACEHOLDER_RE = re.compile(r"(?i)\b(TBD|TODO|FIXME|XXX|PLACEHOLDER|latest)\b")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
HTTPS_RE = re.compile(r"^https://[^\s]+$")
UPSTREAM_ROW_RE = re.compile(
    r"^\|\s*\*\*(L(?:10|[0-9]))\*\*\s*\|\s*`([a-z0-9_]+)`\s*\|\s*"
    r"\[[^\]]+\]\((https://[^)\s]+)\)\s*\|\s*([^|]+?)\s*\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|$"
)
VALID_ADR_IDS = {aid for aid, _ in EXPECTED_ADR_BIJECTION}
RUNTIME_PY_DIRS = ("scripts", "workflows", ".agents/scripts")
REQUIRED_REPO_SCAFFOLDING_FILES = (
    "LICENSE",
    "SECURITY.md",
    ".gitleaks.toml",
    ".gitignore",
    "orca.yaml",
    "Makefile",
    "scripts/check.sh",
    "UPSTREAM.md",
    "upstream-map.toml",
    "zensical.toml",
    "docs/adrs/CATALOG.md",
)


def compute_canonical_digest(manifest: dict[str, Any]) -> tuple[str, int]:
    """Compute SHA-256 over canonical UTF-8 JSON excluding `integrity.sha256`."""
    payload = copy.deepcopy(manifest)
    integrity = payload.get("integrity")
    if not isinstance(integrity, dict):
        raise ValueError("Manifest missing object at root key 'integrity'")
    integrity.pop("sha256", None)
    canonical_bytes = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical_bytes).hexdigest(), len(canonical_bytes)


def compute_file_sha256(path: Path) -> str:
    """Compute hex SHA-256 digest of exact file bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def infer_repo_root(manifest_path: Path, explicit_root: Path | None) -> Path:
    """Resolve repository root cleanly for both real repo and isolated temp copies."""
    if explicit_root is not None:
        return explicit_root.resolve()
    resolved_manifest = manifest_path.resolve()
    if resolved_manifest.parent.name == "manifest":
        return resolved_manifest.parent.parent
    return resolved_manifest.parent


def resolve_safe_repo_path(repo_root: Path, rel_file: str) -> Path | None:
    """Resolve a repo-relative path inside `repo_root`, blocking traversal outside root."""
    if not rel_file or rel_file.startswith("/") or ".." in Path(rel_file).parts:
        return None
    root_resolved = repo_root.resolve()
    candidate = (root_resolved / rel_file).resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError:
        return None
    return candidate


def parse_yaml_frontmatter(markdown_text: str) -> tuple[dict[str, Any] | None, str]:
    """Parse standard YAML frontmatter (scalars, inline lists, block lists) using stdlib."""
    lines = markdown_text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "missing opening '---' YAML frontmatter delimiter"
    end_idx: int | None = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return None, "missing closing '---' YAML frontmatter delimiter"

    fm: dict[str, Any] = {}
    current_list_key: str | None = None
    for raw_line in lines[1:end_idx]:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and current_list_key is not None:
            item = stripped[2:].strip().strip('"').strip("'")
            if item:
                fm[current_list_key].append(item)
            continue
        if ":" not in raw_line:
            return None, f"unparseable frontmatter line: {raw_line!r}"
        key, val = raw_line.split(":", 1)
        key = key.strip()
        val = val.strip()
        if not val:
            fm[key] = []
            current_list_key = key
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            items = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
            fm[key] = items
            current_list_key = None
        else:
            fm[key] = val.strip('"').strip("'")
            current_list_key = None
    return fm, ""


def _resolve_ref(ref: str, root_schema: dict[str, Any]) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"Unsupported external $ref: {ref}")
    node: Any = root_schema
    for part in ref[2:].split("/"):
        node = node[part]
    if not isinstance(node, dict):
        raise ValueError(f"$ref did not resolve to object: {ref}")
    return node


def _check_type(value: Any, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "null":
        return value is None
    return False


def validate_against_schema(
    instance: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any],
    path: str = "$",
) -> list[str]:
    """Recursive Draft 2020-12 JSON Schema subset validator (stdlib-only)."""
    errors: list[str] = []
    if "$ref" in schema:
        resolved = _resolve_ref(schema["$ref"], root_schema)
        errors.extend(validate_against_schema(instance, resolved, root_schema, path))
        return errors

    expected_type = schema.get("type")
    if isinstance(expected_type, str) and not _check_type(instance, expected_type):
        errors.append(f"{path}: expected type '{expected_type}', got {type(instance).__name__}")
        return errors

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}, got {instance!r}")

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value {instance!r} not in enum {schema['enum']!r}")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(
                f"{path}: string length {len(instance)} < minLength {schema['minLength']}"
            )
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(
                f"{path}: string {instance!r} does not match pattern {schema['pattern']!r}"
            )

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: value {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: value {instance} > maximum {schema['maximum']}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: array length {len(instance)} < minItems {schema['minItems']}")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: array length {len(instance)} > maxItems {schema['maxItems']}")
        if schema.get("uniqueItems"):
            seen: list[str] = []
            for idx, item in enumerate(instance):
                key = json.dumps(item, sort_keys=True, ensure_ascii=False)
                if key in seen:
                    errors.append(f"{path}[{idx}]: duplicate item violates uniqueItems")
                seen.append(key)
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for idx, item in enumerate(instance):
                errors.extend(
                    validate_against_schema(item, item_schema, root_schema, f"{path}[{idx}]")
                )

    if isinstance(instance, dict):
        props = schema.get("properties", {})
        for req_key in schema.get("required", []):
            if req_key not in instance:
                errors.append(f"{path}: missing required property '{req_key}'")
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in props:
                    errors.append(f"{path}: unexpected additional property '{key}'")
        for key, val in instance.items():
            if key in props:
                errors.extend(
                    validate_against_schema(val, props[key], root_schema, f"{path}.{key}")
                )

    return errors


def _walk_strings(node: Any, path: str = "$") -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if isinstance(node, str):
        out.append((path, node))
    elif isinstance(node, list):
        for idx, item in enumerate(node):
            out.extend(_walk_strings(item, f"{path}[{idx}]"))
    elif isinstance(node, dict):
        for k, v in node.items():
            out.extend(_walk_strings(v, f"{path}.{k}"))
    return out


def check_adr_governance(
    manifest: dict[str, Any],
    repo_root: Path,
) -> tuple[tuple[str, bool, str], tuple[str, bool, str]]:
    """Gates [11] adr_12_bounded_bijection_and_madr4 and [12] adr_files_sha256_parity."""
    adr_gov = manifest.get("adr_governance", {})
    adrs = adr_gov.get("adrs", [])

    madr_errors: list[str] = []
    hash_errors: list[str] = []
    verified_hashes = 0

    if not isinstance(adrs, list) or len(adrs) != 12:
        count_str = str(len(adrs)) if isinstance(adrs, list) else type(adrs).__name__
        madr_errors.append(f"expected exactly 12 ADRs, got {count_str}")
        hash_errors.append("cannot verify 12/12 ADR SHA-256 parity without 12 ADR entries")
        return (
            ("adr_12_bounded_bijection_and_madr4", False, "; ".join(madr_errors)),
            ("adr_files_sha256_parity", False, "; ".join(hash_errors)),
        )

    observed_pairs = [(str(a.get("id")), str(a.get("layer"))) for a in adrs if isinstance(a, dict)]
    if observed_pairs != EXPECTED_ADR_BIJECTION:
        madr_errors.append(
            f"bijection mismatch: observed={observed_pairs} expected={EXPECTED_ADR_BIJECTION}"
        )

    if adr_gov.get("standard") != "MADR 4.0.0":
        madr_errors.append(f"adr_governance.standard={adr_gov.get('standard')!r} != 'MADR 4.0.0'")
    if adr_gov.get("adr_directory") != "docs/adrs":
        madr_errors.append(
            f"adr_governance.adr_directory={adr_gov.get('adr_directory')!r} != 'docs/adrs'"
        )
    if adr_gov.get("bounded_max_count") != 12:
        madr_errors.append(
            f"adr_governance.bounded_max_count={adr_gov.get('bounded_max_count')!r} != 12"
        )
    if adr_gov.get("required_frontmatter_keys") != REQUIRED_FRONTMATTER_KEYS:
        madr_errors.append(
            "adr_governance.required_frontmatter_keys does not match canonical 7 MADR keys"
        )
    if adr_gov.get("required_madr4_headings") != REQUIRED_MADR4_HEADINGS:
        madr_errors.append(
            "adr_governance.required_madr4_headings does not match canonical 9 MADR 4.0 headings"
        )

    for entry in adrs:
        if not isinstance(entry, dict):
            madr_errors.append("non-object ADR entry")
            hash_errors.append("non-object ADR entry")
            continue
        aid = str(entry.get("id", ""))
        layer = str(entry.get("layer", ""))
        rel_file = str(entry.get("file", ""))
        expected_date = str(entry.get("date", ""))
        recorded_sha = str(entry.get("sha256", ""))

        adr_path = resolve_safe_repo_path(repo_root, rel_file)
        if adr_path is None or not adr_path.is_file():
            madr_errors.append(f"{aid}: missing or unsafe file path {rel_file!r} under {repo_root}")
            hash_errors.append(f"{aid}: file missing ({rel_file!r})")
            continue

        live_sha = compute_file_sha256(adr_path)
        if not SHA256_RE.match(recorded_sha) or live_sha != recorded_sha:
            hash_errors.append(
                f"{aid} ({rel_file}): recorded={recorded_sha!r} != live={live_sha!r}"
            )
        else:
            verified_hashes += 1

        text = adr_path.read_text(encoding="utf-8")
        fm, fm_err = parse_yaml_frontmatter(text)
        if fm is None:
            madr_errors.append(f"{aid}: {fm_err}")
            continue

        for req_k in REQUIRED_FRONTMATTER_KEYS:
            val = fm.get(req_k)
            if val is None or (isinstance(val, (str, list)) and len(val) == 0):
                madr_errors.append(f"{aid}: missing/empty frontmatter key '{req_k}'")

        if fm.get("id") != aid:
            madr_errors.append(f"{aid}: frontmatter id={fm.get('id')!r} != {aid!r}")
        if fm.get("layer") != layer:
            madr_errors.append(f"{aid}: frontmatter layer={fm.get('layer')!r} != {layer!r}")
        if fm.get("status") != "accepted":
            madr_errors.append(f"{aid}: frontmatter status={fm.get('status')!r} != 'accepted'")
        if fm.get("date") != expected_date:
            madr_errors.append(f"{aid}: frontmatter date={fm.get('date')!r} != {expected_date!r}")

        stripped_lines = [ln.strip() for ln in text.splitlines()]
        h1_prefix = f"# {aid}:"
        if not any(ln.startswith(h1_prefix) for ln in stripped_lines):
            madr_errors.append(f"{aid}: missing H1 starting with {h1_prefix!r}")

        last_pos = -1
        for heading in REQUIRED_MADR4_HEADINGS:
            try:
                pos = stripped_lines.index(heading)
            except ValueError:
                madr_errors.append(f"{aid}: missing required MADR 4.0 heading {heading!r}")
                continue
            if pos < last_pos:
                madr_errors.append(f"{aid}: MADR 4.0 heading out of order: {heading!r}")
            last_pos = pos

    madr_ok = len(madr_errors) == 0
    hash_ok = len(hash_errors) == 0 and verified_hashes == 12
    return (
        (
            "adr_12_bounded_bijection_and_madr4",
            madr_ok,
            "12/12 bounded MADR 4.0.0 ADRs (ADR-0001 META + ADR-0002..0012 <-> L0..L10), "
            "frontmatter & 9 headings verified"
            if madr_ok
            else "; ".join(madr_errors),
        ),
        (
            "adr_files_sha256_parity",
            hash_ok,
            "12/12 ADR markdown files verified byte-for-byte SHA-256 parity"
            if hash_ok
            else "; ".join(hash_errors),
        ),
    )


def check_repo_hygiene_ratchet(repo_root: Path) -> tuple[str, bool, str]:
    """Gate [15] repo_hygiene_and_anti_bloat_ratchet."""
    errors: list[str] = []

    # 1. AGENTS.md <= 45 lines and <= 1,600 chars
    agents_md = repo_root / "AGENTS.md"
    agents_lines = 0
    agents_chars = 0
    if not agents_md.is_file():
        errors.append("AGENTS.md missing at repo root")
    else:
        agents_text = agents_md.read_text(encoding="utf-8")
        agents_lines = len(agents_text.splitlines())
        agents_chars = len(agents_text)
        if agents_lines > AGENTS_MD_MAX_LINES:
            errors.append(f"AGENTS.md has {agents_lines} lines > {AGENTS_MD_MAX_LINES}")
        if agents_chars > AGENTS_MD_MAX_CHARS:
            errors.append(f"AGENTS.md has {agents_chars} chars > {AGENTS_MD_MAX_CHARS}")

    # 2. Every .agents/skills/*/SKILL.md has valid frontmatter, name==folder, description <= 1,024 chars
    skills_dir = repo_root / ".agents" / "skills"
    skill_files = sorted(skills_dir.glob("*/SKILL.md")) if skills_dir.is_dir() else []
    if not skill_files:
        errors.append("no .agents/skills/*/SKILL.md found")
    for sf in skill_files:
        fm, fm_err = parse_yaml_frontmatter(sf.read_text(encoding="utf-8"))
        if fm is None:
            errors.append(f"{sf.relative_to(repo_root)}: {fm_err}")
            continue
        name = fm.get("name")
        desc = fm.get("description")
        if name != sf.parent.name:
            errors.append(
                f"{sf.relative_to(repo_root)}: frontmatter name={name!r} != dir {sf.parent.name!r}"
            )
        if not isinstance(desc, str) or not desc.strip():
            errors.append(f"{sf.relative_to(repo_root)}: missing/empty description")
        elif len(desc) > SKILL_DESC_MAX_CHARS:
            errors.append(
                f"{sf.relative_to(repo_root)}: description length {len(desc)} > {SKILL_DESC_MAX_CHARS}"
            )

    # 3. Every .agents/rules/*.md has snake_case trigger: and size <= 24,000 bytes
    rules_dir = repo_root / ".agents" / "rules"
    rule_files = sorted(rules_dir.glob("*.md")) if rules_dir.is_dir() else []
    if not rule_files:
        errors.append("no .agents/rules/*.md found")
    for rf in rule_files:
        size_bytes = rf.stat().st_size
        if size_bytes > RULE_FILE_MAX_BYTES:
            errors.append(
                f"{rf.relative_to(repo_root)}: size {size_bytes}B > {RULE_FILE_MAX_BYTES}B"
            )
        fm, fm_err = parse_yaml_frontmatter(rf.read_text(encoding="utf-8"))
        if fm is None:
            errors.append(f"{rf.relative_to(repo_root)}: {fm_err}")
            continue
        trigger = fm.get("trigger")
        if not isinstance(trigger, str) or trigger not in VALID_RULE_TRIGGERS:
            errors.append(
                f"{rf.relative_to(repo_root)}: invalid/non-snake_case trigger={trigger!r} "
                f"(expected one of {sorted(VALID_RULE_TRIGGERS)})"
            )

    # 4. .agents/hooks.json parses cleanly as JSON object
    hooks_json = repo_root / ".agents" / "hooks.json"
    if not hooks_json.is_file():
        errors.append(".agents/hooks.json missing")
    else:
        try:
            hooks_obj = json.loads(hooks_json.read_text(encoding="utf-8"))
            if not isinstance(hooks_obj, dict) or not hooks_obj:
                errors.append(".agents/hooks.json must be a non-empty JSON object")
        except json.JSONDecodeError as exc:
            errors.append(f".agents/hooks.json invalid JSON: {exc}")

    # 5. Zero unexpanded tilde deny rules in any .agents/**/*.json file
    agents_dir = repo_root / ".agents"
    if agents_dir.is_dir():
        for jf in sorted(agents_dir.rglob("*.json")):
            raw_text = jf.read_text(encoding="utf-8")
            if "(~/" in raw_text:
                errors.append(f"{jf.relative_to(repo_root)}: contains unexpanded tilde rule '(~/'")

    ok = len(errors) == 0
    return (
        "repo_hygiene_and_anti_bloat_ratchet",
        ok,
        f"AGENTS.md ({agents_lines}L/{agents_chars}c), {len(skill_files)} skill(s) <=1024c, "
        f"{len(rule_files)} rule(s) snake_case <=24KB, .agents/hooks.json valid, 0 tilde deny rules"
        if ok
        else "; ".join(errors),
    )


def _collect_nav_targets(node: Any) -> list[str]:
    targets: list[str] = []
    if isinstance(node, str):
        targets.append(node)
    elif isinstance(node, list):
        for item in node:
            targets.extend(_collect_nav_targets(item))
    elif isinstance(node, dict):
        for val in node.values():
            targets.extend(_collect_nav_targets(val))
    return targets


def check_upstream_registry_and_map_parity(
    manifest: dict[str, Any],
    repo_root: Path,
) -> tuple[str, bool, str]:
    """Gate [16] upstream_registry_and_map_parity."""
    errors: list[str] = []

    reg_entries = manifest.get("clean_install_registry", {}).get("entries", [])
    manifest_layers_by_id: dict[str, str] = {}
    if isinstance(reg_entries, list):
        for entry in reg_entries:
            if isinstance(entry, dict) and entry.get("id"):
                manifest_layers_by_id[str(entry["id"])] = str(entry.get("layer", ""))

    # 1. UPSTREAM.md 1:1 parity with manifest clean_install_registry (63/63 winners)
    upstream_md = repo_root / "UPSTREAM.md"
    upstream_layers_by_id: dict[str, str] = {}
    if not upstream_md.is_file():
        errors.append("UPSTREAM.md missing at repo root")
    else:
        for lineno, raw_line in enumerate(
            upstream_md.read_text(encoding="utf-8").splitlines(), start=1
        ):
            stripped = raw_line.strip()
            if not stripped.startswith("| **L"):
                continue
            match = UPSTREAM_ROW_RE.match(stripped)
            if not match:
                errors.append(f"UPSTREAM.md:{lineno}: malformed layer table row")
                continue
            layer, winner_id, url, spdx, pinned_version, role = match.groups()
            if winner_id in upstream_layers_by_id:
                errors.append(f"UPSTREAM.md:{lineno}: duplicate winner id {winner_id!r}")
                continue
            if not HTTPS_RE.match(url):
                errors.append(f"UPSTREAM.md:{lineno}: invalid HTTPS URL {url!r}")
            if not spdx.strip():
                errors.append(f"UPSTREAM.md:{lineno}: empty SPDX license for {winner_id!r}")
            if not pinned_version.strip() or PLACEHOLDER_RE.search(pinned_version):
                errors.append(
                    f"UPSTREAM.md:{lineno}: unpinned/placeholder version {pinned_version!r}"
                )
            if not role.strip():
                errors.append(f"UPSTREAM.md:{lineno}: empty role for {winner_id!r}")
            upstream_layers_by_id[winner_id] = layer

        missing_in_upstream = sorted(set(manifest_layers_by_id) - set(upstream_layers_by_id))
        extra_in_upstream = sorted(set(upstream_layers_by_id) - set(manifest_layers_by_id))
        if missing_in_upstream:
            errors.append(f"UPSTREAM.md missing manifest winner IDs: {missing_in_upstream}")
        if extra_in_upstream:
            errors.append(f"UPSTREAM.md contains undocumented winner IDs: {extra_in_upstream}")
        for wid, expected_layer in manifest_layers_by_id.items():
            obs_layer = upstream_layers_by_id.get(wid)
            if obs_layer is not None and obs_layer != expected_layer:
                errors.append(
                    f"UPSTREAM.md layer mismatch for {wid!r}: {obs_layer!r} != {expected_layer!r}"
                )

    # 2. upstream-map.toml 1:1 bijection with all runtime .py files under scripts/, workflows/, .agents/scripts/
    discovered_py: set[str] = set()
    for rel_dir in RUNTIME_PY_DIRS:
        target_dir = repo_root / rel_dir
        if target_dir.is_dir():
            for py_file in sorted(target_dir.rglob("*.py")):
                if py_file.name == "__init__.py":
                    continue
                discovered_py.add(py_file.relative_to(repo_root).as_posix())

    upstream_map_path = repo_root / "upstream-map.toml"
    mapped_py: list[str] = []
    if not upstream_map_path.is_file():
        errors.append("upstream-map.toml missing at repo root")
    else:
        try:
            map_data = tomllib.loads(upstream_map_path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"upstream-map.toml invalid TOML: {exc}")
            map_data = {}
        adapters = map_data.get("adapters")
        if not isinstance(adapters, list) or not adapters:
            errors.append("upstream-map.toml missing non-empty [[adapters]] table array")
        else:
            seen_paths: set[str] = set()
            for idx, entry in enumerate(adapters):
                if not isinstance(entry, dict):
                    errors.append(f"upstream-map.toml adapters[{idx}]: not a table")
                    continue
                rel_path = str(entry.get("path", "")).strip()
                layer = str(entry.get("layer", "")).strip()
                adr = str(entry.get("adr", "")).strip()
                winners = entry.get("upstream_winners")
                contract = str(entry.get("upstream_contract", "")).strip()
                boundary = str(entry.get("adapter_boundary", "")).strip()
                non_dup = str(entry.get("non_duplication_proof", "")).strip()
                verify_cmd = str(entry.get("verification_command", "")).strip()

                resolved = resolve_safe_repo_path(repo_root, rel_path)
                if resolved is None or not resolved.is_file():
                    errors.append(
                        f"upstream-map.toml adapters[{idx}]: missing/unsafe path {rel_path!r}"
                    )
                elif rel_path in seen_paths:
                    errors.append(f"upstream-map.toml adapters[{idx}]: duplicate path {rel_path!r}")
                else:
                    seen_paths.add(rel_path)
                    mapped_py.append(rel_path)

                if layer not in EXPECTED_LAYERS:
                    errors.append(f"upstream-map.toml ({rel_path}): invalid layer {layer!r}")
                if adr not in VALID_ADR_IDS:
                    errors.append(f"upstream-map.toml ({rel_path}): invalid adr {adr!r}")
                if not isinstance(winners, list) or not winners:
                    errors.append(f"upstream-map.toml ({rel_path}): missing/empty upstream_winners")
                else:
                    for wid in winners:
                        if not isinstance(wid, str) or wid not in manifest_layers_by_id:
                            errors.append(
                                f"upstream-map.toml ({rel_path}): unknown upstream winner {wid!r}"
                            )
                if not HTTPS_RE.match(contract):
                    errors.append(
                        f"upstream-map.toml ({rel_path}): invalid upstream_contract {contract!r}"
                    )
                if not boundary or not non_dup or not verify_cmd:
                    errors.append(
                        f"upstream-map.toml ({rel_path}): missing adapter_boundary, "
                        "non_duplication_proof, or verification_command"
                    )

            unmapped_py = sorted(discovered_py - seen_paths)
            extra_mapped = sorted(seen_paths - discovered_py)
            if unmapped_py:
                errors.append(f"runtime .py files missing from upstream-map.toml: {unmapped_py}")
            if extra_mapped:
                errors.append(f"upstream-map.toml paths outside runtime .py set: {extra_mapped}")

    ok = len(errors) == 0
    return (
        "upstream_registry_and_map_parity",
        ok,
        f"UPSTREAM.md {len(upstream_layers_by_id)}/{len(manifest_layers_by_id)} manifest winners "
        f"(SPDX + HTTPS verified); upstream-map.toml {len(mapped_py)}/{len(discovered_py)} "
        "runtime .py adapters exact 1:1 bijection"
        if ok
        else "; ".join(errors),
    )


def check_repo_scaffolding_and_portal_integrity(repo_root: Path) -> tuple[str, bool, str]:
    """Gate [17] repo_scaffolding_and_portal_integrity."""
    errors: list[str] = []

    for rel_file in REQUIRED_REPO_SCAFFOLDING_FILES:
        resolved = resolve_safe_repo_path(repo_root, rel_file)
        if resolved is None or not resolved.is_file():
            errors.append(f"missing required repo scaffolding file {rel_file!r}")

    check_sh = repo_root / "scripts" / "check.sh"
    if check_sh.is_file() and not os.access(check_sh, os.X_OK):
        errors.append("scripts/check.sh is not executable (+x required)")

    gitleaks_toml = repo_root / ".gitleaks.toml"
    if gitleaks_toml.is_file():
        try:
            tomllib.loads(gitleaks_toml.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            errors.append(f".gitleaks.toml invalid TOML: {exc}")

    orca_yaml = repo_root / "orca.yaml"
    if orca_yaml.is_file():
        orca_text = orca_yaml.read_text(encoding="utf-8")
        if not orca_text.strip():
            errors.append("orca.yaml is empty")
        if re.search(r"(?m)^\s*defaultTabs\s*:", orca_text):
            errors.append("orca.yaml must not declare forbidden 'defaultTabs:' key")

    nav_targets: list[str] = []
    zensical_toml = repo_root / "zensical.toml"
    if zensical_toml.is_file():
        try:
            zdata = tomllib.loads(zensical_toml.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"zensical.toml invalid TOML: {exc}")
            zdata = {}
        project = zdata.get("project", {})
        if not isinstance(project, dict):
            errors.append("zensical.toml missing [project] table")
        else:
            docs_dir = str(project.get("docs_dir", "docs")).strip()
            nav = project.get("nav")
            if not isinstance(nav, list) or not nav:
                errors.append("zensical.toml missing non-empty project.nav list")
            else:
                nav_targets = _collect_nav_targets(nav)
                if not nav_targets:
                    errors.append("zensical.toml project.nav resolved 0 document paths")
                for target in nav_targets:
                    doc_rel = f"{docs_dir}/{target}"
                    doc_path = resolve_safe_repo_path(repo_root, doc_rel)
                    if doc_path is None or not doc_path.is_file():
                        errors.append(f"zensical.toml nav target missing on disk: {doc_rel!r}")

    ok = len(errors) == 0
    return (
        "repo_scaffolding_and_portal_integrity",
        ok,
        f"{len(REQUIRED_REPO_SCAFFOLDING_FILES)}/{len(REQUIRED_REPO_SCAFFOLDING_FILES)} "
        "repo scaffolding files present, scripts/check.sh executable, .gitleaks.toml valid, "
        f"orca.yaml clean (no defaultTabs), zensical.toml {len(nav_targets)}/{len(nav_targets)} "
        "nav docs verified"
        if ok
        else "; ".join(errors),
    )


def check_semantic_and_saturation_invariants(
    manifest: dict[str, Any],
    repo_root: Path,
) -> list[tuple[str, bool, str]]:
    """Run all semantic, cryptographic ADR, clean-install, saturation, and repo hygiene checks."""
    checks: list[tuple[str, bool, str]] = []

    # [3] Disjoint L0-L10 layer ownership (0 overlaps)
    layers = manifest.get("layers", [])
    layer_ids = [layer.get("id") for layer in layers if isinstance(layer, dict)]
    layer_names = [layer.get("name") for layer in layers if isinstance(layer, dict)]
    ownership_map: dict[str, str] = {}
    overlaps: list[str] = []
    for layer in layers:
        if not isinstance(layer, dict):
            continue
        lid = str(layer.get("id"))
        for cap in layer.get("owns_exclusively", []):
            if cap in ownership_map:
                overlaps.append(f"'{cap}' claimed by {ownership_map[cap]} and {lid}")
            else:
                ownership_map[cap] = lid
    layers_ok = (
        layer_ids == EXPECTED_LAYERS
        and len(set(layer_names)) == len(EXPECTED_LAYERS)
        and not overlaps
    )
    checks.append(
        (
            "disjoint_L0_L10_layers",
            layers_ok,
            f"11 unique layers L0-L10, {len(ownership_map)} exclusive domains, 0 overlaps"
            if layers_ok
            else f"ids={layer_ids}, overlaps={overlaps}",
        )
    )

    # [4] Zero retiring Nov 30, 2026 models in active slots (all roots except deprecations_and_sunsets)
    retiring_hits: list[str] = []
    for root_key, section in manifest.items():
        if root_key == "deprecations_and_sunsets":
            continue
        for path, text in _walk_strings(section, f"$.{root_key}"):
            match = RETIRING_NOV30_RE.search(text)
            if match:
                retiring_hits.append(f"{path} matched {match.group(0)!r}")
    checks.append(
        (
            "zero_retiring_nov30_models_active",
            len(retiring_hits) == 0,
            "0 retiring Nov 30, 2026 models in active slots (dot/hyphen/underscore normalized)"
            if not retiring_hits
            else "; ".join(retiring_hits),
        )
    )

    # [5] Zero unpinned placeholders (TBD/TODO/FIXME/XXX/PLACEHOLDER/latest) anywhere
    placeholder_hits: list[str] = []
    for path, text in _walk_strings(manifest, "$"):
        match = PLACEHOLDER_RE.search(text)
        if match:
            placeholder_hits.append(f"{path} matched {match.group(0)!r}")
    checks.append(
        (
            "zero_unpinned_placeholders",
            len(placeholder_hits) == 0,
            "0 TBD/TODO/FIXME/XXX/PLACEHOLDER/latest tokens across entire manifest"
            if not placeholder_hits
            else "; ".join(placeholder_hits),
        )
    )

    # [6] All 9 cross-session routing mechanisms present uniquely
    routes = manifest.get("cross_session_routing", {}).get("routes", [])
    route_ids = [r.get("id") for r in routes if isinstance(r, dict)]
    routes_ok = sorted(route_ids) == sorted(EXPECTED_ROUTE_IDS) and len(route_ids) == len(
        EXPECTED_ROUTE_IDS
    )
    checks.append(
        (
            "cross_session_9_routes_complete",
            routes_ok,
            f"All {len(EXPECTED_ROUTE_IDS)} canonical cross-session routes present uniquely"
            if routes_ok
            else f"Found route_ids={route_ids}",
        )
    )

    # [7] Exact 7 compounding flywheel stages in order 1..7 + hard anti-bloat ratchets
    flywheel = manifest.get("compounding_flywheel", {})
    stages = flywheel.get("stages", [])
    stage_ids = [s.get("id") for s in stages if isinstance(s, dict)]
    stage_orders = [s.get("stage_order") for s in stages if isinstance(s, dict)]
    ratchets = flywheel.get("anti_bloat_ratchets", {})
    promo = flywheel.get("promotion_criteria", {})
    mcp_eager = ratchets.get("mcp_eager_max_tools")
    flywheel_ok = (
        stage_ids == EXPECTED_FLYWHEEL_STAGES
        and stage_orders == [1, 2, 3, 4, 5, 6, 7]
        and ratchets.get("rule_file_max_bytes") == 24000
        and ratchets.get("rules_aggregate_budget_tokens") == 20000
        and isinstance(mcp_eager, int)
        and mcp_eager <= 3
        and ratchets.get("delete_to_add_policy") is True
        and ratchets.get("temporal_invalidation_required") is True
        and promo.get("skillevaluator_tier1_min_score", 0) >= 70
        and promo.get("skillevaluator_tier1_max_high_or_critical") == 0
        and promo.get("skillevaluator_tier3_min_per_dimension", 0) >= 0.50
        and promo.get("skillevaluator_tier3_min_skill_lift", 0) >= 0.05
    )
    checks.append(
        (
            "compounding_7_stages_and_ratchets",
            flywheel_ok,
            "7 stages (1..7), promotion gates (T1>=70/0 HIGH+CRIT, T3>=0.50/lift>=0.05), "
            "ratchets (24KB/20k/<=3 eager/delete-to-add)"
            if flywheel_ok
            else f"stage_ids={stage_ids}, orders={stage_orders}",
        )
    )

    # [8] Security invariants (zero AGY Linux bubblewrap, resolved absolute deny paths, fail-closed)
    sec = manifest.get("security_invariants", {})
    linux_prim = str(sec.get("os_sandbox_primitives", {}).get("linux", ""))
    l0_local = " ".join(layers[0].get("canonical_upstream_local", [])) if layers else ""
    deny_rules = sec.get("standing_deny_rules_baseline", [])
    deny_paths_resolved = bool(deny_rules) and all("(~/" not in str(rule) for rule in deny_rules)
    sec_ok = (
        sec.get("os_sandbox_required") is True
        and sec.get("permission_precedence") == "Deny > Ask > Allow"
        and sec.get("hooks_fail_closed_wrapper_mandatory") is True
        and sec.get("host_verified_facts_mandatory") is True
        and sec.get("zero_committed_secrets") is True
        and deny_paths_resolved
        and manifest.get("cross_session_routing", {})
        .get("security_and_idempotency_invariants", {})
        .get("messages_are_input_never_authority")
        is True
        and "bubblewrap" not in linux_prim.lower()
        and "bubblewrap" not in l0_local.lower()
    )
    checks.append(
        (
            "security_and_sandbox_invariants",
            sec_ok,
            "OS sandbox required (Linux namespaces/macOS Seatbelt/Win AppContainer), "
            "Deny>Ask>Allow, resolved deny paths, fail-closed hooks, host-verified facts, zero secrets"
            if sec_ok
            else "One or more mandatory security invariants failed",
        )
    )

    # [9] AGY surface alignment (5 products, 7 extensions, `agy acp`, non-enterprise standalone IDE)
    surf = manifest.get("surfaces", {})
    exts = surf.get("antigravity_extensions", {}).get("integrations", [])
    ext_ids = {e.get("id") for e in exts if isinstance(e, dict)}
    expected_ext_ids = {
        "vscode",
        "visual_studio",
        "jetbrains",
        "zed",
        "xcode",
        "eclipse",
        "android_studio",
    }
    surf_ok = (
        surf.get("official_product_count") == 5
        and surf.get("antigravity_cli", {}).get("acp_subcommand") == "agy acp"
        and surf.get("antigravity_ide", {}).get("enterprise_supported") is False
        and ext_ids == expected_ext_ids
    )
    checks.append(
        (
            "agy_5_surfaces_7_extensions",
            surf_ok,
            "5 AGY products, 7 IDE extensions, `agy acp`, standalone IDE enterprise_supported=false"
            if surf_ok
            else f"ext_ids={sorted(str(x) for x in ext_ids)}",
        )
    )

    # [11] & [12] ADR 12-file bounded bijection, MADR 4.0.0 structure, and byte-for-byte SHA-256 parity
    adr_madr_check, adr_sha_check = check_adr_governance(manifest, repo_root)
    checks.append(adr_madr_check)
    checks.append(adr_sha_check)

    # [13] Clean-install registry coverage across ALL 11 layers L0-L10 with pinned versions & URLs
    reg = manifest.get("clean_install_registry", {})
    reg_entries = reg.get("entries", [])
    reg_errors: list[str] = []
    covered_layers: set[str] = set()
    seen_reg_ids: set[str] = set()
    if not isinstance(reg_entries, list) or not reg_entries:
        reg_errors.append("clean_install_registry.entries is empty")
    else:
        for idx, entry in enumerate(reg_entries):
            if not isinstance(entry, dict):
                reg_errors.append(f"entries[{idx}]: not an object")
                continue
            eid = str(entry.get("id", ""))
            elayer = str(entry.get("layer", ""))
            pver = str(entry.get("pinned_version", ""))
            icmd = str(entry.get("install_command", ""))
            vcmd = str(entry.get("verify_command", ""))
            url = str(entry.get("official_url", ""))
            if not eid or eid in seen_reg_ids:
                reg_errors.append(f"entries[{idx}]: missing or duplicate id {eid!r}")
            else:
                seen_reg_ids.add(eid)
            if elayer in EXPECTED_LAYERS:
                covered_layers.add(elayer)
            else:
                reg_errors.append(f"entries[{idx}] ({eid}): invalid layer {elayer!r}")
            if not pver or PLACEHOLDER_RE.search(pver):
                reg_errors.append(f"entries[{idx}] ({eid}): unpinned/placeholder version {pver!r}")
            if not icmd or PLACEHOLDER_RE.search(icmd):
                reg_errors.append(
                    f"entries[{idx}] ({eid}): missing or unpinned install_command {icmd!r}"
                )
            if not vcmd:
                reg_errors.append(f"entries[{idx}] ({eid}): missing verify_command")
            if not HTTPS_RE.match(url):
                reg_errors.append(f"entries[{idx}] ({eid}): invalid official_url {url!r}")

    missing_layers = [layer_id for layer_id in EXPECTED_LAYERS if layer_id not in covered_layers]
    if missing_layers:
        reg_errors.append(f"missing clean-install coverage for layers: {missing_layers}")
    reg_ok = len(reg_errors) == 0
    checks.append(
        (
            "clean_install_registry_coverage",
            reg_ok,
            f"11/11 layers (L0-L10) covered across {len(seen_reg_ids)} pinned clean-install "
            "upstream entries (0 unpinned/latest)"
            if reg_ok
            else "; ".join(reg_errors),
        )
    )

    # [14] Saturation proof invariants
    sat = manifest.get("saturation_proof", {})
    adr_count_actual = len(manifest.get("adr_governance", {}).get("adrs", []))
    sat_ok = (
        sat.get("saturation_status") == "saturated"
        and sat.get("zero_self_invention_verified") is True
        and sat.get("unresolved_contradictions") == 0
        and sat.get("unverified_claims") == 0
        and sat.get("adr_count") == 12
        and adr_count_actual == 12
        and sat.get("layer_count") == 11
        and len(layers) == 11
        and sat.get("disjoint_overlap_count") == 0
        and len(overlaps) == 0
        and sat.get("clean_install_layers_covered") == 11
        and len(covered_layers) == 11
    )
    checks.append(
        (
            "saturation_proof_invariants",
            sat_ok,
            "saturation_status='saturated', zero_self_invention_verified=true, 0 contradictions, "
            "0 unverified claims, 12/12 ADRs, 11/11 layers, 0 overlaps"
            if sat_ok
            else f"saturation_proof invariant failed: {sat!r}",
        )
    )

    # [15] Repository hygiene & anti-bloat ratchet
    checks.append(check_repo_hygiene_ratchet(repo_root))

    # [16] Upstream registry (UPSTREAM.md) & runtime adapter map (upstream-map.toml) parity
    checks.append(check_upstream_registry_and_map_parity(manifest, repo_root))

    # [17] First-class repo scaffolding & Zensical portal nav integrity
    checks.append(check_repo_scaffolding_and_portal_integrity(repo_root))

    return checks


def run_verify(
    manifest_path: Path,
    schema_path: Path,
    repo_root: Path | None = None,
) -> int:
    effective_root = infer_repo_root(manifest_path, repo_root)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    schema_draft = schema.get("$schema")
    schema_draft_ok = schema_draft == "https://json-schema.org/draft/2020-12/schema"
    schema_errors = validate_against_schema(manifest, schema, schema)
    semantic_checks = check_semantic_and_saturation_invariants(manifest, effective_root)

    expected_digest, payload_bytes = compute_canonical_digest(manifest)
    integrity = manifest.get("integrity", {})
    recorded_digest = integrity.get("sha256", "")
    seal_ok = (
        integrity.get("algorithm") == "sha256"
        and integrity.get("canonicalization") == "json-utf8-sort-keys-compact"
        and integrity.get("payload_scope") == "root_excluding_integrity_sha256"
        and bool(SHA256_RE.match(str(recorded_digest)))
        and recorded_digest == expected_digest
    )

    # Order 17 gates: [01..02] schema, [03..09] v1 semantic, [10] root SHA-256, [11..17] ADR/registry/hygiene/provenance/portal gates
    ordered_results: list[tuple[str, bool, str]] = [
        ("schema_draft_2020_12", schema_draft_ok, str(schema_draft)),
        (
            "schema_validation",
            not schema_errors,
            "0 errors" if not schema_errors else f"{len(schema_errors)} errors",
        ),
    ]
    ordered_results.extend(semantic_checks[:7])
    ordered_results.append(
        (
            "sha256_integrity_seal",
            seal_ok,
            f"verified ({payload_bytes} canonical bytes) sha256={expected_digest}"
            if seal_ok
            else f"mismatch recorded={recorded_digest!r} computed={expected_digest!r}",
        )
    )
    ordered_results.extend(semantic_checks[7:])

    print(f"Manifest  : {manifest_path}")
    print(f"Schema    : {schema_path}")
    print(f"Repo Root : {effective_root}")
    passed_count = 0
    for idx, (name, ok, detail) in enumerate(ordered_results, start=1):
        if ok:
            passed_count += 1
        print(f"[{idx:02d}][{'PASS' if ok else 'FAIL'}] {name}: {detail}")
        if name == "schema_validation" and schema_errors:
            for err in schema_errors:
                print(f"  - SCHEMA ERROR: {err}")

    total_checks = len(ordered_results)
    passed = passed_count == total_checks
    print(f"CHECKS    : {passed_count}/{total_checks} passed")
    print(f"RESULT    : {'VERIFIED PASS' if passed else 'VERIFICATION FAILED'}")
    return 0 if passed else 1


def run_seal(
    manifest_path: Path,
    schema_path: Path,
    repo_root: Path | None = None,
) -> int:
    effective_root = infer_repo_root(manifest_path, repo_root)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    adr_gov = manifest.get("adr_governance")
    if not isinstance(adr_gov, dict) or not isinstance(adr_gov.get("adrs"), list):
        print("SEAL ERROR: manifest missing 'adr_governance.adrs' list", file=sys.stderr)
        return 1
    for entry in adr_gov["adrs"]:
        if not isinstance(entry, dict):
            print("SEAL ERROR: non-object entry in 'adr_governance.adrs'", file=sys.stderr)
            return 1
        rel_file = str(entry.get("file", ""))
        adr_path = resolve_safe_repo_path(effective_root, rel_file)
        if adr_path is None or not adr_path.is_file():
            print(
                f"SEAL ERROR: cannot hash missing/unsafe ADR file {rel_file!r} under {effective_root}",
                file=sys.stderr,
            )
            return 1
        entry["sha256"] = compute_file_sha256(adr_path)

    if not isinstance(manifest.get("integrity"), dict):
        manifest["integrity"] = {}
    manifest["integrity"]["algorithm"] = "sha256"
    manifest["integrity"]["canonicalization"] = "json-utf8-sort-keys-compact"
    manifest["integrity"]["payload_scope"] = "root_excluding_integrity_sha256"

    digest, payload_bytes = compute_canonical_digest(manifest)
    manifest["integrity"]["sha256"] = digest

    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"SEALED: {manifest_path} ({payload_bytes} canonical bytes, 12 ADR SHA-256 embedded) "
        f"sha256={digest}"
    )
    return run_verify(manifest_path, schema_path, effective_root)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Seal and verify the SOTA Convergence & Compounding Manifest (stdlib-only, 17 gates)."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--seal",
        action="store_true",
        help="Embed live 12/12 ADR SHA-256 digests, compute canonical manifest SHA-256 seal, write manifest, and verify all 17 gates.",
    )
    mode.add_argument(
        "--verify",
        action="store_true",
        help="Validate schema, semantic invariants, 12/12 MADR 4.0 ADRs + SHA-256 parity, clean-install coverage, saturation proof, repo hygiene ratchet, upstream provenance map, repo scaffolding/portal integrity, and root SHA-256 seal.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Path to v2 manifest JSON file.",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
        help="Path to Draft 2020-12 JSON Schema file.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root directory containing docs/adrs/, AGENTS.md, and .agents/.",
    )
    args = parser.parse_args()

    if args.seal:
        return run_seal(args.manifest, args.schema, args.repo_root)
    return run_verify(args.manifest, args.schema, args.repo_root)


if __name__ == "__main__":
    sys.exit(main())
