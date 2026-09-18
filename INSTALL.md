# Agent 安装与初始化协议

这是用户要求为某个工程安装 Agent Project Memory 时的操作指南。阅读此文件本身不授权修改其他工程、账号或机器；在用户已给定的安装范围内执行，不反复索要同一授权。

## 1. 确认范围，读取现有约定

确认实际目标工程路径、当前宿主（Codex / Claude Code / DeepSeek Harness / 其他）、需要的 profile。首次默认 research；普通软件工程可使用 core。用户没有授权写用户级配置时省略 `--global-rules`，并说明项目级功能仍然可用。

读取适用的用户与项目指令、Git 状态及已有 memory 热文件。检查现有规则是否有矛盾或已重复覆盖的框架内容；保留定制的语言、依赖、测试和权限要求。下载框架到目标工程之外的独立目录，不覆盖已有 checkout，不把真实项目当作框架仓库。

从 `https://github.com/StarkLuo/agent-project-memory` 下载，读取安装器和模板后执行。用户指定 ref 时使用该 ref；否则记录实际 checkout commit。不要执行 `curl | sh`，不要替用户设置 API keys、放宽权限或安装宿主。

## 2. 预览后安装

使用实际路径，按宿主选择参数。例如：

```bash
python3 /path/to/agent-project-memory/install.py --project /path/to/target --agent codex --global-rules --dry-run
python3 /path/to/agent-project-memory/install.py --project /path/to/target --agent codex --global-rules
```

Claude Code 用 `--agent claude`，官方 DeepSeek Harness 用 `--agent dsh`，同时使用可以重复参数。其他宿主用 `generic`，明确说明尚需将规则和 skills 接入宿主；不能冒称自动发现。

预览无冲突且改动在授权范围内时继续安装，不为每个文件重复提问。遇到定制冲突先读取差异；将项目专属规则保留在受管理区块外，按用户目标合并。不要修改哈希骗过冲突检测，不直接删除原规则。只有存在会改变用户意图的关键选择时提问。

旧框架迁移时，搜索活跃规则、skills 与记忆中的 `project_memory/skills` 引用并改为原生入口；历史归档标明是历史即可。确认旧文件仅为未定制跳转后使用 `--remove-legacy`，报告备份位置。安装器不会判断自然语言引用是否已经过期。

## 3. 填写真实记忆

读取目标工程 `.agents/skills/initialize-memory/SKILL.md` 并遵循它。安装当天重新打开 host 之前，这个技能未必已出现在菜单里，可以直接按文件读取执行，不声称原生发现已经验证。

从实际代码与已有用户描述填写三个热文件；只对关键目标、成功标准、优先级或约束缺口集中提问。空工程或证据缺失时明确“尚无实现/待确认”。已有成熟记忆只局部维护，不重新初始化。不得启动训练、修改业务代码或编造项目背景来填满模板。

## 4. 验收与交付

```bash
python3 /path/to/agent-project-memory/install.py --project /path/to/target --check --strict
```

修改了用户级规则时，加 `--global-rules` 一起检查。核对规则不矛盾、路径真实、状态有依据，以及适配副本与原生 skills 一致。检查结构通过不意味着事实全部验证；未知事项可以明确保留。

交付目标路径、宿主/profile、修改的用户级与工程文件、记忆摘要、尚待确认项、备份和实际检查结果。指导用户在宿主中核对加载来源和技能列表，必要时重新启动会话。不要因安装任务顺手提交、push 或发布目标工程。
