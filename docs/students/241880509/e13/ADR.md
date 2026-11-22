# ADR-013：A→B 当次报告交接与 fixed-md 哈希校验

编号：ADR-013  
日期：2026-11-22  
作者：顾家谭 / 241880509（B03 组，B 轨道）

## 问题

E13 要把 A 组当次 `incremental-check` 报告交给 B 组消费，替代 E11-B 的固定 `fixed-md.json`。需要决定：

- A 的 `incremental-check` envelope 如何转换成 B 的 `fixed-md` 输入；
- 跨进程/跨机器传输后如何证明报告字节未被篡改；
- B 原有 `fixed_report` 请求如何保持兼容；
- 哪些字段保留 A 的来源，哪些由 B 重新绑定。

## 候选方案

1. **handoff 适配器 + fixed-md 信封 + 可选 SHA256**（采用）：`handoff_a_to_b.py` 逐项核验 A 的 result/stage/artifact URI、SHA256、bytes、target commit，生成只含 `data` 和 `source_report` 的 `fixed-md` 信封；B 请求携带 `fixed_report_sha256`，pipeline 在读取前重算。
2. 直接把 A 的 `incremental-check.json` 交给 B 的 `patch()`：少一层转换，但 B 的输入类型契约变成 `incremental-check`，E11-B/E12 的 fixed-md 分支和测试要改，且丢失 A 的 stage 与 artifact 路径校验。
3. 只校验 A 的 `result.json`，不校验 artifact 字节：实现简单，但报告文件在传输/检出时被修改无法发现；E13 C3 明确要求拒绝。
4. 强制所有 fixed-md 请求都带 SHA：安全性更高，但会破坏 E11-B/E12 旧请求和既有测试；E13 只要求新交接链路可校验。

## 采用方案与原因

采用方案 1：

- `handoff_a_to_b.py` 要求 A 的 `result.status=SUCCEEDED`、`target_commit` 等于 `--target-sha`，恰有一个 `incremental-check` stage；stage 的 `schema_version/kind/status/commit/job_id/trace_id/data.commit` 全部一致；stage 引用的每个 artifact 都按 `artifact://<job_id>/<path>` 解析，校验路径不越界、SHA256 和 bytes。
- 输出 envelope 保留 `source_report={job_id,trace_id,uri,sha256}`，B 的 `fixed-md-input.json` 可追溯 A 的原始任务与报告。
- B 的 `pipeline.load_fixed_report()` 在 `fixed_report_sha256` 存在时先做字节哈希校验，再校验 envelope 和 `data.findings`；不提供哈希时保持旧行为。
- 这样 A 的报告格式、B 的修复输入和 E11-B 的固定 MD 契约三者解耦，E12 的 `incremental_report` 路径也不受影响。

## 输入输出字段

|对象|关键字段|
|---|---|
|A `result.json`|`schema_version=e11e12-1`、`status=SUCCEEDED`、`job_id`、`trace_id`、`target_commit`、`stages[incremental-check].artifact`|
|A `incremental-check.json`|`kind=incremental-check`、`commit`、`job_id`、`trace_id`、`data.commit`、`data.findings`、`artifacts[]`|
|handoff `fixed-md.json`|`schema_version`、`kind=fixed-md`、`status`、`commit`、`data`、`source_report`|
|B request|`fixed_report`、`fixed_report_sha256`（可选）、`repo/base/target/candidate`|
|B output|`fixed-md-input.json`（含 `source_report`）、`repair.json.input_report`、`validation.json`、`recheck.json`|

## 兼容性与测试

- 不带 `fixed_report_sha256` 的旧 E11-B 请求仍按原逻辑读取；带哈希时必须 64 位十六进制，否则 `INVALID_REPORT_SHA`。
- 哈希不符返回 `ARTIFACT_HASH_MISMATCH`；envelope 的 commit/status/kind 不符返回 `SCHEMA_MISMATCH`/`STALE_REPORT`/`ARTIFACT_TYPE_MISMATCH`。
- 新增 `labs/e13e14/tests/test_e13_b.py` 4 项：正常加载并保留来源、篡改拒绝、非法 SHA、payload commit 过期；课程 `test_handoff.py` 3 项继续通过。
- E12 的 `incremental_report` 外部报告路径未修改；21 项既有测试仍通过。

## 后果

- 代价：交接多一次磁盘读取和 SHA256 计算；B 的 fixed-md 分支新增可选参数；Windows 检出若发生 CRLF 转换，需要先做字节归一，否则会被哈希校验拒绝（这是预期行为）。
- 收益：A 的报告来源可追溯，传输篡改可检测；E11-B 的固定 MD 请求保持兼容；E12 与 E13 的输入路径互不破坏。
- 已知限制：handoff 只支持 `incremental-check` 单一 stage 和固定 `main.o/helper.o` 投影；A 的 E13 自有项目若只发布 job 摘要而没有原始产物，无法通过校验，需 A 补交。
