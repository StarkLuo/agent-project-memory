#!/usr/bin/env python3
"""Install repository-local agent skills and memory. Python 3.10+, stdlib only.

No network, model API, subprocess, dependency installation, or business-code execution.
Existing memory is never overwritten. Rule edits use checked managed blocks.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import unquote

VERSION = "1.0.0"
SOURCE = Path(__file__).resolve().parent
STATE = ".agents/project-memory/manifest.json"
LEGACY_STATE = "project_memory/.framework.json"
CORE = {"initialize-memory", "start-new-session", "close-session", "rebalance-memory"}
HOT_LIMITS = {"00_project_brief.md": 2000, "01_current_focus.md": 4000, "02_repo_map.md": 5000}
IGNORE_BODY = "/.agents/project-memory/backups/\n/.project_memory_backups/\n"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_path(base: Path, relative: str) -> Path:
    rel = Path(relative)
    if not relative or rel.is_absolute() or ".." in rel.parts:
        raise ValueError(f"Unsafe relative path: {relative}")
    target = base / rel
    for node in (target, *target.parents):
        if node == base:
            break
        if node.is_symlink():
            raise ValueError(f"Refusing symlink target/ancestor: {node}")
        if node != target and node.exists() and not node.is_dir():
            raise ValueError(f"Not a directory: {node}")
    if target.exists() and not target.is_file():
        raise ValueError(f"Not a regular file: {target}")
    return target


def read(path: Path) -> bytes | None:
    return path.read_bytes() if path.exists() else None


def read_state(root: Path) -> dict:
    raw = read(safe_path(root, STATE))
    if raw is None:
        return {"schema": 1, "version": VERSION, "agents": [], "profile": "core", "files": {}}
    data = json.loads(raw)
    if not isinstance(data, dict) or data.get("schema") != 1:
        raise ValueError("Unknown installation manifest schema")
    version = data.get("version", "")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Invalid installation version")
    if tuple(map(int, version.split("."))) > tuple(map(int, VERSION.split("."))):
        raise ValueError(f"Refusing downgrade from {version} to {VERSION}")
    if data.get("profile") not in {"core", "research"}:
        raise ValueError("Invalid installation profile")
    if not isinstance(data.get("agents"), list) or any(a not in {"codex", "claude", "dsh", "generic"} for a in data["agents"]):
        raise ValueError("Invalid installation agents")
    files = data.get("files")
    if not isinstance(files, dict):
        raise ValueError("Invalid installation file map")
    for key, value in files.items():
        if not isinstance(key, str) or not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("Invalid installation hash entry")
        safe_path(root, key)
    return data


def managed_block(current: bytes | None, body: bytes, kind: str, comment: str = "html") -> bytes:
    """Preserve all bytes outside one verified block, including CRLF and user text."""
    text = (current or b"").decode("utf-8")
    payload = body.decode("utf-8").rstrip("\n") + "\n"
    lead, tail = ("<!-- ", " -->") if comment == "html" else ("# ", "")
    start_prefix = f"{lead}agent-project-memory:begin {kind} "
    end = f"{lead}agent-project-memory:end {kind}{tail}"
    start = f"{start_prefix}v{VERSION} sha256={sha(payload.encode())}{tail}\n"
    new = start + payload + end
    if f"{lead}agent-project-memory:begin {kind}" not in text and f"{lead}agent-project-memory:end {kind}" not in text:
        separator = "" if not text else ("\n" if text.endswith("\n") else "\n\n")
        return (text + separator + new + "\n").encode("utf-8")
    if text.count(start_prefix) != 1 or text.count(end) != 1:
        raise ValueError(f"Duplicate or incomplete {kind} managed markers")
    begin = text.index(start_prefix)
    header_end = text.find("\n", begin)
    finish = text.index(end)
    if header_end < 0 or finish < header_end:
        raise ValueError(f"Malformed {kind} managed block")
    header = text[begin:header_end]
    match = re.fullmatch(re.escape(start_prefix) + r"v(\d+\.\d+\.\d+) sha256=([0-9a-f]{64})" + re.escape(tail), header)
    if not match:
        raise ValueError(f"Invalid {kind} managed header")
    if tuple(map(int, match[1].split("."))) > tuple(map(int, VERSION.split("."))):
        raise ValueError(f"Refusing {kind} managed-block downgrade")
    old_body = text[header_end + 1:finish]
    if sha(old_body.encode()) != match[2]:
        raise ValueError(f"Locally edited {kind} block: move custom additions outside the markers, then reconcile the block")
    return (text[:begin] + new + text[finish + len(end):]).encode("utf-8")


@dataclass
class Change:
    base: Path
    relative: str
    before: bytes | None
    after: bytes | None
    scope: str = "project"

    @property
    def path(self) -> Path:
        return safe_path(self.base, self.relative)


def legacy_stub(name: str) -> bytes:
    if name == "add-experiment":
        return ("# add-experiment（兼容入口）\n\n"
                "实验记录已合并到 [review-experiment](../../.agents/skills/review-experiment/SKILL.md) 的“记录阶段”。沿用已完成的有效审查，仅核对新增证据；保持各 run 身份与原始观察可追溯。记录权限与边界以正式流程为准。\n").encode()
    return (f"# {name}（兼容入口）\n\n"
            f"正式流程位于 [{name}](../../.agents/skills/{name}/SKILL.md)。使用时读取该文件；本文件只保留旧路径兼容，不另行定义步骤或授权。\n").encode()


def global_root(agent: str, args: argparse.Namespace) -> Path:
    defaults = {"codex": ("CODEX_HOME", ".codex"), "claude": ("CLAUDE_CONFIG_DIR", ".claude"), "dsh": ("DSH_HOME", ".dsh")}
    variable, folder = defaults[agent]
    # --user-home is an explicit sandbox for previews/checks; don't inherit live profile env paths.
    if args.user_home:
        return Path(args.user_home).expanduser().resolve() / folder
    return Path(os.environ.get(variable) or (Path.home() / folder)).expanduser().resolve()


def build_plan(root: Path, args: argparse.Namespace, state: dict) -> tuple[list[Change], dict, list[str]]:
    agents = sorted(set(state["agents"]) | set(args.agent or ([] if state["agents"] else ["codex"])))
    profile = args.profile or (state["profile"] if read(safe_path(root, STATE)) else "research")
    if state["profile"] == "research" and profile == "core":
        raise ValueError("Profile downgrade requires manual review; installer does not delete research skills")
    changes: list[Change] = []
    notices: list[str] = []
    bases = dict(state["files"])
    legacy_raw = read(safe_path(root, LEGACY_STATE))
    legacy = {}
    if legacy_raw is not None:
        legacy = json.loads(legacy_raw)
        if not isinstance(legacy, dict) or legacy.get("schema") != 1 or legacy.get("version") != "2.0.0" or not isinstance(legacy.get("managed_sha256"), dict):
            raise ValueError("Unrecognized legacy manifest; migrate it manually")
    legacy_bases = legacy.get("managed_sha256", {})
    if any(not isinstance(k, str) or not isinstance(v, str) or not re.fullmatch(r"[0-9a-f]{64}", v) for k, v in legacy_bases.items()):
        raise ValueError("Invalid legacy hash map")

    def add(relative: str, content: bytes, mode: str = "managed", kind: str = "", base: Path = root, scope: str = "project") -> None:
        path = safe_path(base, relative)
        current = read(path)
        if mode == "memory" and current is not None:
            return
        if mode == "block":
            content = managed_block(current, content, kind, "hash" if relative == ".gitignore" else "html")
        elif mode == "managed":
            known = {bases.get(relative), legacy_bases.get(relative)}
            if current is not None and current != content and sha(current) not in known:
                raise ValueError(f"Local customization conflict; nothing written: {path}")
            bases[relative] = sha(content)
        if current != content:
            changes.append(Change(base, relative, current, content, scope))

    add("AGENTS.md", (SOURCE / "templates/project-rules.md").read_bytes(), "block", "project")
    if "claude" in agents:
        add("CLAUDE.md", b"@AGENTS.md\n", "block", "claude")
    add(".gitignore", IGNORE_BODY.encode(), "block", "ignore")
    skill_files = sorted((SOURCE / "skills").glob("*/SKILL.md"))
    if not skill_files or not CORE.issubset({p.parent.name for p in skill_files}):
        raise ValueError("Incomplete framework download: missing skills")
    for source in skill_files:
        if profile == "core" and source.parent.name not in CORE:
            continue
        content = source.read_bytes()
        add(f".agents/skills/{source.parent.name}/SKILL.md", content)
        if "claude" in agents:
            add(f".claude/skills/{source.parent.name}/SKILL.md", content)
    memory_files = sorted((SOURCE / "templates/project_memory").rglob("*"))
    if not all((SOURCE / "templates/project_memory" / name).is_file() for name in HOT_LIMITS):
        raise ValueError("Incomplete framework download: missing hot templates")
    for source in memory_files:
        if source.is_file():
            add(source.relative_to(SOURCE / "templates").as_posix(), source.read_bytes(), "memory")
    if args.global_rules:
        for agent in agents:
            if agent == "generic":
                notices.append("generic: no global path guessed; configure the host explicitly")
                continue
            base = global_root(agent, args)
            # Validate missing or existing profile directory through its parent as well.
            safe_path(base.parent, base.name + "/AGENTS.md")
            filename = "CLAUDE.md" if agent == "claude" else "AGENTS.md"
            add(filename, (SOURCE / "templates/global-rules.md").read_bytes(), "block", "global", base, "global")
            if agent == "codex" and (base / "AGENTS.override.md").is_file() and (base / "AGENTS.override.md").stat().st_size:
                raise ValueError(f"{base}/AGENTS.override.md shadows global AGENTS.md; reconcile explicitly")
    if "codex" in agents and (root / "AGENTS.override.md").is_file() and (root / "AGENTS.override.md").stat().st_size:
        raise ValueError("AGENTS.override.md shadows project AGENTS.md; reconcile explicitly")
    old_dir = root / "project_memory/skills"
    if args.remove_legacy and old_dir.exists():
        allowed = {p.parent.name for p in skill_files} | {"add-experiment"}
        for path in sorted(old_dir.iterdir()):
            relative = path.relative_to(root).as_posix()
            safe_path(root, relative)
            current = read(path)
            if path.suffix != ".md" or path.stem not in allowed or current != legacy_stub(path.stem):
                raise ValueError(f"Not an untouched legacy forwarding stub; preserved: {path}")
            canonical = "review-experiment" if path.stem == "add-experiment" else path.stem
            destination = f".agents/skills/{canonical}/SKILL.md"
            if destination not in bases:
                raise ValueError(f"Cannot remove stub before installing its native skill: {path}")
            changes.append(Change(root, relative, current, None))
    elif old_dir.exists():
        notices.append("Legacy skills retained; inspect references, then use --remove-legacy for untouched forwarding stubs")
    if args.remove_legacy and legacy_raw is not None:
        changes.append(Change(root, LEGACY_STATE, legacy_raw, None))
    result = {"schema": 1, "version": VERSION, "agents": agents, "profile": profile, "files": bases}
    content = (json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    current = read(safe_path(root, STATE))
    if current != content:
        changes.append(Change(root, STATE, current, content))
    return changes, result, notices


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    fd, temporary = tempfile.mkstemp(prefix=".apm-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def apply(changes: list[Change]) -> None:
    # Preflight every path before any writes; this detects edits made after planning.
    for item in changes:
        if read(item.path) != item.before:
            raise ValueError(f"File changed during planning; retry after review: {item.path}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-")
    backups: dict[tuple[Path, str], Path] = {}
    for item in changes:
        if item.before is None:
            continue
        group = (item.base, item.scope)
        if group not in backups:
            relative = ".agents/project-memory/backups/probe" if item.scope == "project" else ".agent-project-memory-backups/probe"
            base = safe_path(item.base, relative).parent
            base.mkdir(parents=True, exist_ok=True)
            base.chmod(0o700)
            backups[group] = Path(tempfile.mkdtemp(prefix=stamp, dir=base))
            print(f"BACKUP {backups[group]}")
        backup = backups[group] / item.relative
        atomic_write(backup, item.before)
        backup.chmod(0o600)
    # Per-file atomic replacement, not a cross-filesystem transaction. Backups survive failures.
    for item in changes:
        if read(item.path) != item.before:
            raise ValueError(f"Concurrent edit detected; inspect backups and retry: {item.path}")
        if item.after is None:
            item.path.unlink()
        else:
            atomic_write(item.path, item.after)
    print(f"Applied {len(changes)} file changes. Existing memory was preserved.")


def check(root: Path, args: argparse.Namespace, state: dict) -> int:
    errors: list[str] = []
    notices: list[str] = []
    if read(safe_path(root, STATE)) is None:
        errors.append("Installation manifest is missing")
    for source in (SOURCE / "skills").glob("*/SKILL.md"):
        if state["profile"] == "core" and source.parent.name not in CORE:
            continue
        roots = [".agents/skills"] + ([".claude/skills"] if "claude" in state["agents"] else [])
        for skill_root in roots:
            relative = f"{skill_root}/{source.parent.name}/SKILL.md"
            if relative not in state["files"]:
                errors.append(f"Required skill missing from manifest: {relative}")
    for relative, expected in state["files"].items():
        path = safe_path(root, relative)
        data = read(path)
        if data is None:
            errors.append(f"Missing managed file: {relative}")
            continue
        content = data.decode("utf-8").replace("\r\n", "\n")
        if sha(data) != expected:
            notices.append(f"Locally customized file (preserved by installer): {relative}")
        if path.name == "SKILL.md":
            match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", content, re.S)
            if not match or not re.search(r"^name: " + re.escape(path.parent.name) + r"$", match[1], re.M) or not re.search(r"^description: \S.+$", match[1], re.M):
                errors.append(f"Invalid skill frontmatter: {relative}")
            for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", content):
                link = link.strip("<>").split("#", 1)[0]
                if link and not re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", link) and not (path.parent / unquote(link)).exists():
                    errors.append(f"Broken skill navigation: {relative} -> {link}")
    for source in (SOURCE / "templates/project_memory").rglob("*"):
        if not source.is_file():
            continue
        relative = source.relative_to(SOURCE / "templates").as_posix()
        data = read(safe_path(root, relative))
        if data is None:
            errors.append(f"Missing memory file: {relative}")
            continue
        content = data.decode("utf-8").replace("\r\n", "\n")
        if source.name in HOT_LIMITS and not content.strip():
            errors.append(f"Empty hot memory: {relative}")
        placeholder = bool(re.search(r"^status:\s*init_template\s*$", content, re.M))
        if placeholder:
            target = errors if args.strict and source.name in HOT_LIMITS else notices
            target.append(f"Uninitialized memory: {relative}")
        if source.name in HOT_LIMITS and len(content) > HOT_LIMITS[source.name]:
            notices.append(f"Hot file length: {relative} ({len(content)} characters); review, don't truncate blindly")
    rules = [(root, "AGENTS.md", "project", SOURCE / "templates/project-rules.md")]
    if "claude" in state["agents"]:
        rules.append((root, "CLAUDE.md", "claude", None))
        for source in (root / ".agents/skills").glob("*/SKILL.md"):
            target = root / ".claude/skills" / source.parent.name / "SKILL.md"
            if str(source.relative_to(root)) in state["files"] and read(target) != read(source):
                errors.append(f"Claude adapter differs from canonical skill: {source.parent.name}")
    if args.global_rules:
        for agent in state["agents"]:
            if agent != "generic":
                rules.append((global_root(agent, args), "CLAUDE.md" if agent == "claude" else "AGENTS.md", "global", SOURCE / "templates/global-rules.md"))
    for base, name, kind, template in rules:
        data = read(safe_path(base, name))
        body = template.read_bytes() if template else b"@AGENTS.md\n"
        if data is None or f"agent-project-memory:begin {kind} ".encode() not in data:
            errors.append(f"Missing managed rules: {base / name}")
            continue
        try:
            if managed_block(data, body, kind) != data:
                notices.append(f"Rule update available: {base / name}")
        except ValueError as error:
            errors.append(f"{base / name}: {error}")
    if "codex" in state["agents"]:
        for base in [root] + ([global_root("codex", args)] if args.global_rules else []):
            override = base / "AGENTS.override.md"
            if override.is_file() and override.stat().st_size:
                errors.append(f"AGENTS.md shadowed by: {override}")
    for notice in notices:
        print(f"NOTICE {notice}")
    for error in errors:
        print(f"ERROR {error}")
    print(f"Check: {len(errors)} errors, {len(notices)} notices. Structural checks do not prove factual correctness or host loading.")
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="Existing target project, not the downloaded framework directory")
    parser.add_argument("--agent", action="append", choices=["codex", "claude", "dsh", "generic"], help="Repeat to add hosts; default: codex on first install")
    parser.add_argument("--profile", choices=["core", "research"], help="Default: research initially, then retain installed profile")
    parser.add_argument("--global-rules", action="store_true", help="Also merge a bounded block into each selected host's user rules")
    parser.add_argument("--user-home", help="Explicit isolated user home; ignores live host-home environment variables")
    parser.add_argument("--dry-run", action="store_true", help="Preview paths and diffs; write nothing")
    parser.add_argument("--check", action="store_true", help="Read-only structure and initialization checks")
    parser.add_argument("--strict", action="store_true", help="With --check, fail if any hot file still has init_template status")
    parser.add_argument("--remove-legacy", action="store_true", help="Back up and remove only exact v2 forwarding stubs and recognized old manifest")
    parser.add_argument("--version", action="version", version=VERSION)
    args = parser.parse_args()
    if args.check and (args.dry_run or args.remove_legacy or args.agent or args.profile):
        parser.error("--check reads installed state; do not combine it with install options")
    if args.strict and not args.check:
        parser.error("--strict requires --check")
    root = Path(args.project).expanduser().resolve()
    if not root.is_dir() or root == Path(root.anchor) or root == Path.home():
        raise ValueError("Choose an existing project directory, not a filesystem root or home directory")
    if root == SOURCE:
        raise ValueError("Target is the framework checkout itself; choose the project to initialize")
    state = read_state(root)
    if args.check:
        return check(root, args, state)
    changes, result, notices = build_plan(root, args, state)
    print(f"Project: {root}\nFramework: {VERSION}; agents: {', '.join(result['agents'])}; profile: {result['profile']}")
    for notice in notices:
        print(f"NOTICE {notice}")
    for item in changes:
        action = "DELETE" if item.after is None else "CREATE" if item.before is None else "UPDATE"
        print(f"{action} {item.path}")
        if args.dry_run and item.before is not None and item.after is not None:
            print("".join(difflib.unified_diff(item.before.decode().splitlines(True), item.after.decode().splitlines(True), fromfile=str(item.path), tofile=str(item.path) + " (planned)")), end="")
    if args.dry_run:
        print("DRY-RUN: no files, directories, or backups written.")
        return 0
    apply(changes)
    if args.remove_legacy:
        old_dir = root / "project_memory/skills"
        if old_dir.is_dir() and not old_dir.is_symlink() and not any(old_dir.iterdir()):
            old_dir.rmdir()
    print("Next: ask the agent to read .agents/skills/initialize-memory/SKILL.md and fill only uninitialized memory from verified project facts.")
    print("Review preserved custom rules for semantic conflicts. Reload the host session if new instructions/skills are not visible.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2) from error
