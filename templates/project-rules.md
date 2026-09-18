## Agent Project Memory

本节只规定协作与记忆流程，不取代个人偏好和本工程更具体的约定。安装框架不授权训练、发布、删除产物或扩大任务范围。

### 接手与事实

- 延续项目先读 `project_memory/00_project_brief.md`、`01_current_focus.md`；涉及实现或入口定位再读 `02_repo_map.md`。一次性小任务只读相关上下文。
- knowledge 先看索引和相关条目；archive 只作历史参考，不默认加载。不要把全部 skills 当作知识正文读取。
- 用户最新确认决定目标和授权；代码、配置、日志与产物说明实际状态。记录日期较新不等于事实更可靠；明确区分目标、实现、观察、推断与待确认事项。
- 运行状态附观察时间、主机和 run 身份；接手时重查，不据旧记忆重复启动或删除产物。保留未提交和未跟踪改动，单个 commit 不一定代表运行代码。

### 任务路由

原生 skills 位于 `.agents/skills/<name>/SKILL.md`；Claude Code 的 `.claude/skills/` 是安装器生成的适配副本。只加载适用流程，审查或修改 skill 本身不触发其业务动作。

- 初次填写记忆：`initialize-memory`；接手未完成工作：`start-new-session`。
- 普通“更新 memory”或已授权工作的稳定变化：`close-session`，局部替换旧状态及相关索引；没有稳定变化不写。
- 明确要求整理、压缩、周期维护或已授权的相应框架升级：`rebalance-memory`。普通回填不扩大成全局重排。
- research profile 才安装：`plan-experiment`、`review-experiment`、`run-experiment`、`diagnose-training`、`run-minimal-train`、`modify-backbone`、`add-literature`；分别负责实验设计、审查记录、执行恢复、异常诊断、最小验证、模型链路修改与文献综合。未安装时不假定它们可用。

### 记忆职责

`project_memory/` 仅保存记忆；不放 skills、安装状态或执行脚本。
三个热文件只保存稳定概览、当前工作集和高价值入口；更新优先替换当前真相，不追加会话流水账。
`knowledge/` 路由：架构→`10_architecture_patterns.md`；决策→`11_decisions.md`；实验→`12_experiment_ledger.md`；运行→`13_runbook.md`；问题→`14_open_issues.md`；术语→`15_glossary.md`；文献→`16_literature_synthesis.md`。
同一事实指定一个主要位置；其他文件保留短摘要和引用。唯一历史证据先保存再压缩，不把未采纳建议写成决策；自动 memory 仅作召回辅助。

### 执行与验证

任务已授权时在原对象、预算和停止条件内继续，不逐步重复确认；规划、诊断和审查本身不授权实施或重跑。
验证按影响选择已有检查和最小真实入口，通过后停止；不因固定流程重复完整训练。明确区分实现完成、运行通过、效果改善和机制证据。
有实验时，数据 split、metric、评价协议视为受保护资产；必要修改说明原因、影响和单独验证方法。历史结论保留适用条件，不外推到改变后的设定。
