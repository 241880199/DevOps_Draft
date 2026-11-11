# ADR-011：E11 轨道内集成接口决策

编号：ADR-011  
日期：2026-11-11  
作者：顾家谭 / 241880509（B03 组，B 轨道）

## 问题

E11 要把 E8–E10 已完成的三个组件接成两条轨道：

- A：BuildChecker 的全量检测（真实 strace 图 + Make 数据库）→ EChecker 的增量检测（GCC `-MM` + 历史缓存）；
- B：DRAFT 的两轮真实构建 → MDFixer 的固定 MD 消费、补丁、沙箱验证和动态重检。

需要决定：组件以什么边界组合、报告如何版本化、缓存如何从全量图过渡到增量扫描、固定 MD 与真实报告的切换点放在哪里，以及失败时在哪一阶段停止。

## 候选方案

1. **进程内组合 + 统一 envelope**（采用）：`pipeline.py` 在同一任务内依次调用现有组件，阶段产物写成带 `schema_version/job_id/trace_id/kind/commit/status/data/artifacts` 的 JSON，下游只从 envelope 读取。
2. 各组件独立服务、通过 HTTP 串行调用：边界清晰，但 E11 的课堂目标是“轨道内集成”，引入四个服务的部署与网络故障面，超出本阶段验证范围。
3. 下游直接 import 上游 Python 对象/中间变量：实现最短，但无法保存阶段产物、无法核对 commit 与哈希，也不能复现“版本不一致停止修复”的契约。
4. A 的增量缓存继续用 GCC `-MM` 生成：与 E8–E10 一致，但没有消费 BuildChecker 的真实 strace 图，不满足 E11-A 的“全量图接入历史缓存”。

## 采用方案与原因

采用方案 1，并在 `pipeline.execute()` 中固定以下顺序：

- **A**：`snapshot(base)` → `full(base)` → 把 `actual-graph.json` 投影到 `main.o/helper.o` 写入 `baseline-cache.json` → `snapshot(target)` → `scan(target, cache)` → `full(target)` → 比较 `(type,target,dependency)` 集合。
- **B**：`snapshot(target)` → `auto_build(target, candidate)` → 校验 `fixed-md` envelope → `patch(target, data)` → 写 `candidate.patch` → `validate(target, patch)` → `full(target)` 重检。

原因：

- 复用 E8–E10 的 `scan/patch/validate` 与 BuildChecker 的 `full_check`，不复制算法，个人贡献集中在集成、契约测试和环境适配。
- 阶段 envelope 使每个中间结果都能单独保存、哈希和比对；`check_envelope()` 在消费前统一校验 `schema_version=e11e12-1`、`commit`、`status` 与 `kind`。
- 基线缓存只投影对象目标，不把 `app` 链接目标混入；A 的全量对照也只比较对象目标，避免把链接边差异误判为增量缺陷。
- B 在 E11 明确使用固定 `fixed-md.json`，E12 再切换为真实 `incremental-check` 报告；切换点由输入来源决定，下游代码不变。

## 输入输出字段

|阶段|kind|关键输入|关键输出|
|---|---|---|---|
|全量|`full-check`|base 项目、`make clean && make app`|`findings[]`、`actual-graph.json`、`declared-graph.json`、`make-db.txt`、`processes.json`|
|增量|`incremental-check`|target 项目、`baseline-cache.json` 的 `actual/key`|`incremental-report.json`（`findings/added/resolved/refreshed/reused`）|
|DRAFT|`draft`|target 项目、候选 Dockerfile、`expected_output`|两轮构建日志、`image_id`、`verification`|
|修复输入|`fixed-md`|固定 MD envelope（commit 必须等于 target）|`data.findings`|
|修复|`repair`|MD `data`、target Makefile|`candidate.patch`、`repair-plan.json`、输入报告 artifact|
|重检|`recheck`|沙箱验证结果、修复后全量图|`validation.json`、`findings[]`、`patched_makefile_sha256`|

所有 artifact 使用 `artifact://<job_id>/<相对路径>`，并同时记录 `sha256` 与 `bytes`；下载端必须重新计算哈希。

## 兼容性与测试

- 保留 E8–E10 的 `labs/e8e10/lab.py` 与 11 项测试不动；E11 新增 `test_student.py` 5 项，覆盖缓存刷新/复用、macro/mixed 补丁落点与 `STALE_REPORT`。
- 原有 `test_contract.py` 10 项继续通过；总计 15 项 `OK`。
- 失败语义：`SCHEMA_MISMATCH`、`STALE_REPORT`、`ARTIFACT_TYPE_MISMATCH`、`ARTIFACT_HASH_MISMATCH`、`DRAFT_FAILED`、`REPAIR_REJECTED`、`OUTPUT_EXISTS` 等均在消费前或对应阶段返回；`STALE_REPORT` 的实测见 `evidence/stale-report/`。
- 已知限制：增量失效键是全局保守键，任一项目内预处理行/recipe/flags/编译器变化都会刷新两个目标；C1→C2 函数体变化复用、C2→C3 头文件指令变化刷新的实测见 `evidence/autonomous-a/`。这是为保持检测正确性而选择的保守策略，不是按目标精确失效。

## 后果

- 代价：A 在 target 上仍要跑一次全量用于对照，B 的 `validate()` 会复制项目并完整构建一次，运行时间高于只跑增量或只跑构建。
- 收益：每个阶段都有可独立复核的封装、commit 和哈希；上游失败或版本不一致时不会进入修复；DRAFT 的实际镜像与 MDFixer 的补丁验证可以分别取证。
- 迁移到 E12 时，只需把 `fixed-md` 阶段替换为 `incremental-check` 的真实 `data`，`repair/recheck` 的消费逻辑与校验保持不变。
