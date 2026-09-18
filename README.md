# Agent Project Memory

[English](README.en.md) · [Agent 安装流程](INSTALL.md) · [MIT](LICENSE)

让 AI coding agents 在跨会话开发中记住**项目目标、当前状态、关键决策和证据**，而不是反复读取聊天记录。

这是从真实研究工程中提炼的轻量协作框架：可审查的 Markdown 记忆、按任务加载的原生 skills，以及只依赖 Python 标准库的安全安装器。支持 Codex、Claude Code 和 DeepSeek Harness（DSH）；不绑定模型，不运行后台服务，不需要 API key。

## 给 agent 一句话

在**目标工程**中，把下面的话发给 agent：

> 请从 https://github.com/StarkLuo/agent-project-memory 下载框架到目标工程之外，读取 INSTALL.md，按其中流程为当前工程安装 research 配置。我授权合并当前 agent 的用户级规则、工程规则并安装项目级 skills；保留我的所有现有规则与记忆。随后读取真实工程，结合我已说明的目标填写初始 memory；只有关键目标或约束缺失时再问我。先检查安装预览，不要仅创建占位文件就结束，不要发布我的工程或启动实验。

这是一条**给具备文件和 shell 权限的 agent 的工作指令**，不是 GitHub URL 自动执行机制。宿主的权限审批、工作区信任或重载提示仍然适用。

安装器处理文件与冲突；agent 负责理解代码、询问目标、填写事实。直接运行安装命令只生成框架与明确标记的占位记忆，不会调用 LLM 或假装完成语义初始化。

## 手动安装

要求 Python **3.10+**；下载可用 Git 或 GitHub ZIP。安装过程离线、不安装依赖。

```bash
git clone https://github.com/StarkLuo/agent-project-memory.git

# /path/to/project 是已有目标工程，不是刚下载的框架目录。
python3 agent-project-memory/install.py --project /path/to/project --agent codex --global-rules --dry-run
python3 agent-project-memory/install.py --project /path/to/project --agent codex --global-rules
```

Windows 可将 `python3` 换成 `py -3`。路径含空格时加引号。首次默认 research 配置；通用软件工程可加 `--profile core`。重复 `--agent` 可同时适配多种宿主：

```bash
python3 agent-project-memory/install.py --project /path/to/project --agent codex --agent claude --agent dsh --global-rules
```

然后让 agent 读取目标工程的 `.agents/skills/initialize-memory/SKILL.md` 完成初始化，最后检查：

```bash
python3 agent-project-memory/install.py --project /path/to/project --check --strict
```

`--strict` 要求三个热文件不再是初始化占位；未使用的 knowledge 允许保留占位。检查通过只代表结构条件满足，不证明项目事实正确。

## 三层职责

```text
用户级规则                 跨项目约定，保留你的个人设置
目标工程/
├── AGENTS.md              工程规则、记忆入口和任务路由
├── CLAUDE.md              仅 Claude：导入 AGENTS.md
├── .agents/
│   ├── skills/*/SKILL.md   原生任务流程
│   └── project-memory/    安装清单；本地备份被 Git 忽略
├── .claude/skills/         仅 Claude：自动生成的适配副本
└── project_memory/        只保存记忆，不保存 skills 或安装状态
    ├── 00_project_brief.md
    ├── 01_current_focus.md
    ├── 02_repo_map.md
    ├── knowledge/         架构、决策、实验、运行、问题、术语、文献
    └── archive/           历史原文，不默认读取
```

不把全部文件塞进每次上下文。三个热文件保存当前工作集；knowledge 按相关主题查阅；archive 只在追溯历史时读取。

## Skills

| 配置 | Skills | 用途 |
| --- | --- | --- |
| core（4 个） | initialize-memory、start-new-session、close-session、rebalance-memory | 初始化、接手、局部回填、明确授权的整理 |
| research（共 11 个） | core + plan-experiment、review-experiment、run-experiment、diagnose-training、run-minimal-train、modify-backbone、add-literature | 实验设计、执行、证据审查、训练与文献流程 |

research 源自研究工程，但不包含任何具体模型、数据集、私有路径或实验结果。`modify-backbone` 的不变量来自目标工程知识，不把原工程的维度或训练策略外推。

“更新 memory”是局部替换当前状态；“整理/压缩 memory”才进行全局维护。审查流程不意味着启动流程中的实验；已有授权无需逐步重复确认，也不扩展到新对象或新预算。

## 宿主适配与实际边界

| 宿主 | 用户级规则（仅 `--global-rules`） | 工程入口 | 项目 skills |
| --- | --- | --- | --- |
| Codex | `$CODEX_HOME/AGENTS.md`，默认 `~/.codex/AGENTS.md` | `AGENTS.md` | `.agents/skills/` |
| Claude Code | `$CLAUDE_CONFIG_DIR/CLAUDE.md`，默认 `~/.claude/CLAUDE.md` | `CLAUDE.md` 导入 `AGENTS.md` | `.claude/skills/` 适配副本 |
| DeepSeek Harness | `$DSH_HOME/AGENTS.md`，默认 `~/.dsh/AGENTS.md` | `AGENTS.md` | `.agents/skills/` |
| generic | 不猜测全局路径 | `AGENTS.md`，宿主需手动接入 | `.agents/skills/`，宿主需支持或显式读取 |

这里的“全局”是**用户级指令文件**，不是修改厂商 system prompt。正确文件名是 `AGENTS.md`，不是大小写不同的 `AGENTS.MD`。

原生路径依据核对于 2026-09-18：[Codex 规则](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[Codex skills](https://learn.chatgpt.com/docs/build-skills)、[Claude memory](https://code.claude.com/docs/en/memory)、[Claude skills](https://code.claude.com/docs/en/skills)、[DSH 规则源码说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/context/agent-instructions/README.md)、[DSH skills 源码说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md)。DSH 仍处于 developer preview；禁用对应插件的自定义 preset 不会因安装文件而自动启用能力。

安装器总是生成 `.agents/skills/`；Claude 另生成等价副本，不依赖符号链接或 Windows 管理员权限。副本由安装器管理，不应单独修改；本地定制会在升级时报告冲突，检查也会发现两边不一致。已存在的同名用户级 skills、嵌套规则、宿主策略及上下文大小限制仍可能影响实际加载。安装后核对宿主技能列表与规则来源；必要时重开会话。

## 安全合并、升级与恢复

- `--dry-run` 不写文件、目录、安装状态或备份。
- 规则使用带哈希的 managed block（受管理区块）；区块外原文逐字节保留。要长期定制规则，写在区块外。区块内被修改时停止，先由 agent/维护者比较并合并，不强行覆盖。
- skills 使用安装清单中的基准哈希识别定制；定制冲突在写入前停止，未跟踪的同名内容不会被默默接管。
- 已有 `project_memory` 正文不覆盖。没有 `--force` 清空记忆的开关。
- 覆盖或删除前备份原文件。项目备份在 `.agents/project-memory/backups/`；全局备份在对应宿主目录的 `.agent-project-memory-backups/`，**不会复制个人全局规则到项目仓库**。
- 每个文件原子替换，但多个目录/文件并非一个事务。磁盘故障或并发修改可能留下部分写入：根据输出的备份检查并恢复，再重试。不要同时运行多个安装器。
- 拒绝受管理文件或其工程内父目录的符号链接；不改变权限策略、API 配置、模型选择、插件设置或业务代码。

升级：在框架仓库检查并拉取所需版本后，针对工程重新执行相同安装命令，先 `--dry-run`。已安装的 agent/profile 会保留，新增 `--agent` 是增量安装；不通过省略参数卸载宿主，不自动降级 research 为 core。需要更新用户级规则时再次显式带 `--global-rules`。

安装器不理解原有自然语言规则的语义冲突；agent 必须审查现有约定与新增区块，不能把“文件合并成功”当成“规则已经一致”。Codex 的非空 `AGENTS.override.md` 会遮蔽同层 `AGENTS.md`，安装器会提示并停止，交由使用者明确处理。

本机隔离演练可以加 `--user-home /path/to/sandbox-home`；该选项忽略实时宿主 home 环境变量，不修改 `$HOME` 或配置环境变量。

## 旧版迁移

原来的 `project_memory/skills/*.md` 不再需要。先检查当前规则与活跃记忆的引用，再执行：

```bash
python3 agent-project-memory/install.py --project /path/to/project --agent codex --remove-legacy --dry-run
python3 agent-project-memory/install.py --project /path/to/project --agent codex --remove-legacy
```

这只删除已知 v2.0.0 的**未修改跳转文件**，先备份且要求对应原生 skill 已安装；原始长技能正文或定制跳转会阻止迁移。旧 `add-experiment` 的工作由 `review-experiment` 的记录阶段承担。识别出的旧 `.framework.json` 一并移出记忆目录，安装状态改由 `.agents/project-memory/manifest.json` 管理。历史归档中的旧路径可以保留为历史事实，不继续充当当前入口。

## 隐私与限制

框架没有遥测、云同步或自动提交。agent 为填写记忆读取的文件仍会受其宿主/模型的数据政策约束；不要让 agent 读取不必要的密钥或敏感数据。`project_memory` 可能包含内部目标、机器路径和实验结果，公开业务仓库前必须单独审查，必要时加入自己的忽略规则。

本项目验证的是安装器和生成文件；尚不宣称已在三个宿主上完成真实模型会话的端到端验证，也不保证模型永远遵守 Markdown 指令。权限控制应使用宿主实际的 sandbox/approval 配置，不能用此框架替代。

## 维护本框架

正文唯一来源是 `skills/`，记忆占位来源是 `templates/project_memory/`，规则来源是 `templates/*-rules.md`。不要把真实项目记忆或凭据复制进模板。修改安装器后用隔离目录验证预览、重复安装、已有记忆保留、冲突、备份、core/research 与宿主适配，并检查新 skills 的 frontmatter 和安装后链接。

本框架有意保持简单：没有向量库、MCP 服务、自动训练调度或模型 API 封装。只有真实使用暴露了需要，才增加相应机制。
