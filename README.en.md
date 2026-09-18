# Agent Project Memory

[中文文档](README.md) · [Agent installation guide](INSTALL.md) · [MIT](LICENSE)

A lightweight, model-independent workflow for persistent project context: small working-set memory, on-demand native skills, and a safe, dependency-free installer. Designed for Codex, Claude Code, and DeepSeek Harness (DSH).

## Agent-assisted setup

Ask your coding agent, from the target project:

> Download https://github.com/StarkLuo/agent-project-memory into a separate directory outside this project. Read INSTALL.md and install the research profile for this project and my current agent host. I authorize merging the host's user-level instructions, project instructions, and project-local skills; preserve existing custom rules and memory. Review the installation preview, then initialize memory from actual source files and the goals I have provided. Ask only for missing goals or material constraints. Do not stop at placeholder creation, publish my project, or start experiments.

The agent performs semantic initialization; the Python installer only manages files. No model API key is needed by the framework. Host permissions and workspace trust still apply.

## Manual setup

Python 3.10+ is required. No third-party dependencies, network calls, telemetry, or background service.

```bash
git clone https://github.com/StarkLuo/agent-project-memory.git
python3 agent-project-memory/install.py --project /path/to/project --agent codex --global-rules --dry-run
python3 agent-project-memory/install.py --project /path/to/project --agent codex --global-rules
```

Use `--agent claude` or `--agent dsh` for other supported hosts; repeat `--agent` for multiple hosts. Use `--profile core` for the four memory skills only; the default research profile includes seven additional experiment/research skills. On later runs, installed hosts/profile are retained.

Ask the agent to read the installed `.agents/skills/initialize-memory/SKILL.md`, inspect the real project, and fill the three hot files. Templates and skill instructions are Chinese-first; the agent should use the user's preferred language for project memory. Then run:

```bash
python3 agent-project-memory/install.py --project /path/to/project --check --strict
```

## Separation of responsibilities

- User-level instructions: optional, narrowly scoped managed block; existing personal preferences remain intact.
- `AGENTS.md`: project rules and routing. Claude receives a `CLAUDE.md` import plus generated `.claude/skills/` copies.
- `.agents/skills/`: native workflows; DSH and Codex share this location.
- `project_memory/`: memory only. Brief, current focus, repository map, on-demand knowledge, and historical archive.
- `.agents/project-memory/`: installer state and Git-ignored local backups.

The installer never overwrites existing memory. Managed rules and skills detect customization conflicts before writing. Existing bytes outside rule blocks are preserved. Every replacement/deletion is backed up; global-rule backups remain in the host's user directory, not in the project. Writes are atomic per file, not transactional across all files. Inspect backups after an interrupted installation; avoid concurrent installers.

Rerun the installer after reviewing an upstream update, preview first. `--global-rules` must be explicit whenever updating user-level rules. Move local rule additions outside managed blocks; do not alter stored hashes to bypass conflicts. Existing custom rules still need semantic review by an agent/person.

`--remove-legacy` removes only recognized, untouched v2 forwarding stubs after backing them up and checking native destinations. It does not remove old custom skill bodies. Update live references before using it; `project_memory/skills/` is no longer part of the layout.

## Host support and limits

Verified against official documentation/source on 2026-09-18: [Codex instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [Codex skills](https://learn.chatgpt.com/docs/build-skills), [Claude memory](https://code.claude.com/docs/en/memory), [Claude skills](https://code.claude.com/docs/en/skills), [DSH instructions](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/context/agent-instructions/README.md), [DSH filesystem skills](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md).

The framework modifies user-level files, not vendor system prompts. Custom host presets, disabled plugins, same-name skills, nested instructions, and host policy may affect loading. DSH is a developer preview. The `generic` adapter does not assume a global path or automatic discovery. Reload the session and verify native discovery when necessary.

The installer and generated layout are locally checked; this release does not claim live model-session end-to-end verification across all three hosts. Structural checks do not prove memory accuracy or model compliance. Use actual sandbox/approval controls for enforcement.

Memory can contain internal goals, paths, and experiment results. Review it separately before publishing a project. The framework itself has no telemetry; file reads performed by an agent remain subject to that host/model's data policies.
