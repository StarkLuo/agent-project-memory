---
name: close-session
description: 普通更新 memory，或已授权工作产生需要跨会话保留的稳定变化时，局部回填并替换对应旧状态。没有稳定变化、只讨论建议或只审查文档时不写入。
---

# 局部回填 memory

## 先决定是否写入

只保留会影响下次工作的目标、阻塞、下一步、实现边界、决策或证据。用户尚未采纳的建议不写成既定路线；没有稳定变化就不更新。
先读 [当前焦点](../../../project_memory/01_current_focus.md)，其他文件只查本轮涉及的索引与条目。

## 按事实职责更新

| 内容 | 仓库内落点 |
| --- | --- |
| 稳定目标与成功标准改变 | project_memory/00_project_brief.md |
| 当前任务、阻塞、下一步、运行观察 | project_memory/01_current_focus.md |
| 真实入口与模块职责 | project_memory/02_repo_map.md |
| 架构关系与接口不变量 | project_memory/knowledge/10_architecture_patterns.md |
| 已确认决策、理由、适用范围和替代关系 | project_memory/knowledge/11_decisions.md |
| 审查后的实验事实与有限结论 | project_memory/knowledge/12_experiment_ledger.md |
| 已验证命令、环境前提与恢复方式 | project_memory/knowledge/13_runbook.md |
| 活跃问题、假设、排除项和下一项检查 | project_memory/knowledge/14_open_issues.md |
| 高频新术语 | project_memory/knowledge/15_glossary.md |
| 可复用文献综合 | project_memory/knowledge/16_literature_synthesis.md |

安装 research profile 时，实验落盘采用 `review-experiment` 的记录阶段，文献落盘采用 `add-literature`。core profile 只保留相关证据、适用条件和来源；已经完成的审查不重复执行。

## 局部一致性

- 同一事实指定一个主要记录位置，其余以短摘要和引用导航，避免复制完整配置与指标。
- 更新某项状态时，替换本文件及直接关联索引中的过期表述；保留历史条目的日期、run 身份和原始观察，并标明已完成、后置或被替代。
- 运行观察附观察日期、主机/run 标识和证据路径；未实际重查时保留原观察日期，不能以本次编辑日期冒充验证日期。
- 记录代码身份时包含相关未提交/未跟踪改动或已有源码快照；单个 commit 不一定代表实际运行代码。
- 研究结论注明适用数据、配置和证据边界；证据不足可以记录为待确认，不把猜想升级为事实。
- 中断、取消和失败运行可在既有运行元数据或 focus 留恢复入口，不必强行生成研究结论。

## 完成边界

局部更新可以替换旧状态、去除本轮重复并刷新相关链接；不顺带重排无关历史。
若需要跨主题迁移或整体压缩，报告原因并按已获授权调用 [周期维护](../rebalance-memory/SKILL.md)；已有明确维护授权时不重复询问。
交付时说明更新了哪些当前事实、证据边界和仍未核实的状态。
