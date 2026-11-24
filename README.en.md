# Agent Project Memory

[中文文档](README.md) · [Agent installation guide](INSTALL.md) · [MIT](LICENSE)

A lightweight, model-independent workflow for persistent project context: small working-set memory, on-demand native skills, and a safe, dependency-free installer. Designed for Codex, Claude Code, and DeepSeek Harness (DSH).

Quick links: [Setup](#agent-assisted-setup) · [Usage guide](#usage-guide) · [Prompt reference](#prompt-reference) · [Guidance for agents](#guidance-for-agents) · [Detailed Chinese guide](README.md#usage-guide).

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

## Usage guide

The usual rhythm is: **explain the project once → let each new session read the current context and wait → work normally → save a handoff before closing → periodically organize memory**. You do not need to invoke every skill manually or write the memory files yourself.

The prompts below describe intent, not exact-match commands. Skill selection depends on the host loading the rules and the agent interpreting your request; this is not a background automation service. If needed, explicitly ask the agent to read the corresponding `.agents/skills/<name>/SKILL.md`.

### 1. Initialize with a generous project briefing

Installing the framework and populating the first memory are normally one-time steps, not something to repeat for every conversation. Give the agent as much relevant background as you already know, especially when inheriting messy legacy code. You can write a long, informal explanation rather than preparing a form first.

Useful context includes:

- Your goal, success criteria, immediate priority, and what is deliberately out of scope.
- Your understanding of directories, real entry points, module responsibilities, third-party code, obsolete scripts, and experimental copies.
- Commands you actually used, required configuration, input/output locations, and environment assumptions. Distinguish previously working commands from recently verified ones.
- Completed work, unfinished changes, current problems, recent results, and uncommitted or untracked files.
- Earlier approaches and why they were abandoned, including the conditions under which they failed.
- Protected interfaces, datasets, evaluation protocols, environments, running jobs, and resource limits.
- Uncertainties: “I think this is still the entry point” is a useful lead, not a verified implementation fact.

For example, after installation:

```text
Initialize project_memory from this background and the actual repository.
For now, inspect and document only; do not implement changes or run training.

I want to make this legacy data-processing and training project reproducible.
The first priority is to reproduce the existing workflow, not rewrite the model.
I believe scripts/ contains launchers, src/ the implementation, and configs/ the
configuration. There are two historical entry points; please determine which
launchers still use them. Do not delete legacy/ or overwrite outputs/.

I recently changed data loading but have not committed it. I do not know whether
the full training workflow passes. Do not add dependencies or change evaluation.
Investigate missing structure from source; ask me only for missing goals or
material constraints. Mark anything you cannot establish as unconfirmed.
```

For a multi-message briefing, first say: “I will describe this in several messages; wait until I say to initialize.” If you know almost nothing about the repository, let the agent map it read-only, then combine those findings with your goals. Source code can reveal implementation, but not your intended priorities or acceptable costs. Never include unnecessary secrets or credentials in a briefing.

The `initialize-memory` workflow should produce a useful brief, current focus, and repository map; place needed detail in knowledge files; identify sources and uncertainties; and ask a small set of consequential questions. Unused knowledge files can remain placeholders. Run `--check --strict` after the three hot files are populated, but remember that it checks structure, not truth.

A long briefing should become **short hot memory with traceable supporting detail**, not a transcript pasted into the current-focus file or an instruction to load the entire repository every session.

### 2. Start a session by understanding, then waiting

Opening with a context-recovery round before assigning work is a useful default:

> Please understand the current progress and wait for my instructions.

For an explicit boundary:

> Read the project rules and hot memory, and inspect relevant source, configuration, or existing logs as needed. Summarize the goal, completed work, blockers, and uncertainties. This round is read-only: do not change code or memory, start, resume, or stop jobs. Reply with the summary and wait for my next message.

`start-new-session` should read only relevant context, inspect the working tree when needed, and treat recorded run status as a dated observation. A remote job that cannot be checked should remain unverified.

**“Wait for my instructions” is the stopping condition for this turn.** A next step in memory or an earlier authorization does not override your current request to wait. The agent should end the context-recovery turn after summarizing, not autonomously continue the old plan.

Review that summary, correct misunderstandings, and then give the actual task. A new conversation should not reinitialize existing memory.

### 3. Work normally; keep decisions and evidence distinct

Describe what you want to achieve, the permitted scope, and how to judge completion. For example:

> Fix the empty-input failure in data loading without changing interfaces or training policy. Trace the real callers, make the smallest sufficient fix, validate through existing entry points, and record stable changes needed for the next handoff.

For authorized implementation work, `close-session` can record stable changes locally. In the research profile, other workflows apply when relevant:

| Activity | Workflow | Recording boundary |
| --- | --- | --- |
| Research idea generation or refinement | `brainstorm-ideas` | Start from a promising lead and identify meaningful differences, improvements, or a clearer research story; absolute originality is not a prerequisite |
| Method novelty assessment | `check-method-novelty` | Inspect the mechanisms and evidence in the closest papers, separate resemblance from substantive overlap, and state an evidence-bounded claim |
| Literature or route comparison | `add-literature` once reusable conclusions exist | Record authorized topic-level synthesis with sources, disagreements, and limits; reading alone does not trigger writing |
| Experiment analysis | `review-experiment` | Separate run validity, comparison fairness, observed effects, and mechanism evidence; record when authorized |
| Experiment planning | `plan-experiment` | Define hypotheses, invariants, budget, and stopping conditions; a plan is not a completed run |
| Architecture discussion | Relevant knowledge, then `close-session` for authorized stable outcomes | Distinguish adopted design from implemented structure; use `modify-backbone` when actually changing model pathways |
| Running or recovering experiments | `run-experiment` | Stay within authorized jobs and budgets; record identity, observations, and recovery locations |
| Diagnosis or minimal verification | `diagnose-training` / `run-minimal-train` | Diagnosis does not imply permission to fix; a smoke run is not evidence of better quality |

Core does not install the research workflows. Not every architecture discussion needs a model-modification skill.

Automatic skill selection does **not** mean every discussion becomes a memory write. Stable outcomes of authorized work can be preserved; read-only analysis, unadopted suggestions, and incomplete investigations must not become settled decisions. Say “Record these conclusions in memory” when you want discussion results saved, or “Discussion only; do not edit files or memory” when you do not.

To explicitly authorize research recordkeeping for a task:

> When this literature review, experiment analysis, or architecture discussion produces reusable conclusions, update the relevant memory locally. Separate verified facts, decisions I adopted, candidate approaches, and untested hypotheses. Do not save a chat transcript or start new experiments because of this instruction.

### 4. Save a handoff before closing or switching tasks

The short request is enough:

> Record memory so another session or machine can take over.

For a more explicit handoff:

> Locally update memory with this session's stable changes, completed and unfinished work, actual validation coverage, uncommitted changes, blockers, next steps, and evidence locations. Replace directly related stale status, but do not reorganize the whole knowledge base. For ongoing jobs, record only checked status with observation time and run identity; do not restart or stop them. Tell me which files changed and what remains unverified, then finish this turn.

This is `close-session`, not `rebalance-memory`. No stable changes means no write is necessary. Do not replace a useful handoff with a growing transcript.

Before closing, check that the next agent can distinguish implemented-but-unverified work from completed work, proposed commands from validated commands, and paused tasks from finished ones. Runs need host/run identifiers, code and configuration identity, last observation time, and log/checkpoint/result locations. Uncommitted and untracked changes matter: Git HEAD may not reproduce the workspace.

Wait for confirmation that files were actually updated. After an abrupt interruption, the next agent can reconstruct state from existing memory, working-tree changes, and logs rather than wiping and reinitializing memory.

### 5. Handoff does not automatically synchronize anything

| Where you continue | What must be available |
| --- | --- |
| New chat, same directory and machine | Existing project rules, skills, and memory; no reinstall needed |
| Another agent host on the same machine | That host's native adapters, reusing the same project memory |
| Another machine, server, or checkout | Matching code, rules, skills, and memory, plus separately prepared environment, data, checkpoints, and results |

Writing memory does not commit, push, copy files, synchronize a cloud folder, or move a running process. Those require a separate mechanism and authorization. Review sensitive content and ignore rules before committing anything; account for uncommitted and untracked source as well as Markdown.

Reviewed project instructions, `.agents/skills/`, `.agents/project-memory/manifest.json`, and `project_memory/` normally travel with the code; include Claude's project adapters when used. Do not indiscriminately commit backups, personal global rules, credentials, or large run artifacts. Configure user-level rules on the destination machine as needed.

Prefer project-relative paths; label host-specific absolute paths. A memory reference to a checkpoint is not the checkpoint itself. Missing assets should be reported, not silently replaced with a new run.

For a change of topic, say: “Save the unfinished task's recovery point; next session I will work on export. Do not mark the old task complete or resume it automatically.” With parallel sessions, divide file ownership and designate one writer for shared memory and one operator for each job/output directory. This framework does not merge concurrent memory writes.

### 6. Periodically organize memory without erasing history

A weekly check can be convenient, but there is no built-in weekly job. Organize when hot files become unwieldy, status contradicts itself, entries repeat, completed tasks dominate the focus, or the project direction changes.

> Please substantially organize memory. Use rebalance-memory to verify the current goal, entry points, and status before compressing hot files. Move currently unnecessary detail into appropriate knowledge or archive files and repair references. Preserve decision rationale, failure conditions, run identities, and evidence. Do not change business code, delete run artifacts, or start experiments. Report corrections, destinations, hot-file size changes, and unresolved uncertainties.

Reusable architecture, decisions, experiments, and run instructions belong in knowledge; history-only originals belong in archive. Keep current working context and navigation in the hot files. Cold memory is retrievable context, not a recycle bin.

The 2,000 / 4,000 / 5,000 character reminders for brief / focus / repository map are not hard limits or compression targets. Judge success by correct handoff, consistent active status, and traceable evidence—not just shorter text. “Unverified” must not become “disproved,” and “organize memory” never means permission to delete checkpoints, logs, or data.

### 7. Common omissions

- Correct inaccurate memory at its primary location and related indexes using explicit evidence; preserve the time and conditions of historical observations.
- Explain changed goals and which constraints still apply; update the brief, focus, and decisions instead of reinstalling or erasing history.
- If a handoff summary is wrong, check the directory, branch, synchronization, and loaded instructions before rebuilding memory.
- Important handoffs deserve an explicit save request and a list of changed files; a conversational summary is not proof of a file write.
- Missing historical artifacts should be marked unavailable, not reconstructed as invented results or silently rerun.
- Put persistent personal preferences in user rules and project-specific conventions outside the managed project-rule block. Do not edit stored hashes to bypass conflicts.

## Prompt reference

| Intent | Example |
| --- | --- |
| Initialize | Initialize memory from my briefing and the actual repository; ask for material gaps |
| Brief in several messages | Wait until I say to initialize; I have more context to provide |
| Start a session | Understand the current progress, summarize, and wait for my instructions |
| Discuss only | Analyze this without changing code, files, or memory |
| Preserve research conclusions | Record these conclusions with sources and separate facts, hypotheses, candidates, and adopted decisions |
| Close a session | Record memory for handoff; update locally, do not reorganize or synchronize |
| Switch topics | Preserve the unfinished task's recovery point; next we will work on another task |
| Maintain memory | Substantially organize memory, preserving evidence and reporting migration destinations |

## Guidance for agents

Treat this guide as usage guidance, not permission to act outside the user's task. Current requests to wait, read only, or avoid recording override assumptions drawn from older plans.

After setup, explain four actions briefly: give a rich initial briefing, ask a new session to understand and wait, request a handoff save before closing, and periodically request organization. Do not recite the whole manual or require the user to format their background first.

Load applicable skills as needed. Reuse established context and authorization without repeated questions. Report actual writes, evidence, and uncertainties; make no write when there is nothing stable to preserve. For cross-machine handoff, explain code and artifact synchronization separately. Offer the prompt and next step relevant to the user's current situation, not a mandatory ritual for every conversation.

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
