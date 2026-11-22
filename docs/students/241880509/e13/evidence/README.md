# E13 B 轨道证据索引

所有文件来自 2026-11-22 的真实运行。镜像 `course-e11e12:241880509`（`sha256:91c3d7dee370...`），容器内 Debian 13、gcc 14.2.0、GNU Make 4.4.1、strace 6.13、Python 3.13.14。B 仓库基线 `main` 为 `1394580`（E12 已合并）。

A 组本轮提供代码（`exp7/A组代码/DevOps_BuildChecker`，main `c68a87e`），未单独提供原始结果目录。`c1_fresh/`、`c1prime/` 中的 A 报告由 B 用 A 的 `labs/e11e12/pipeline.py` 在隔离容器运行 A 的 E11-A 入口生成；A 组员独立签收待补。

## c1_fresh/、c1prime/

| 目录 | 内容 |
|---|---|
| `c1_fresh/` | A 对 B 项目 target `77b40f` 的报告（`job-e6ed45e4...`，SHA `3f66b60d...`）、handoff SHA `fa70153d...`、B `job-02f85b97...` 的四阶段结果、补丁、validation、recheck |
| `c1prime/` | A 自有项目 target `93ef2b3` 的报告（`job-84674fd1...`，SHA `c574b1d5...`）、handoff SHA `60c8d752...`、B `job-9d8de9c7...` 的四阶段结果、补丁、validation、recheck |

每项目录含 `a_source/`（A 的 result/full-check/incremental-check/incremental-report/baseline-cache、target-full）、`handoff-fixed-md.json`、`request-e11-b.json`、B 的 `result.json`、`draft.json`、`fixed-md-input.json`、`candidate.patch`、`repair-plan.json`、`repair.json`、`recheck.json`、`validation.json`、`draft-build-result.json`。

`c1_live_handoff/` 保留 E12 种子（A 的 E12 报告、metadata、bundle、旧 B 修复），不作为本轮 C1 判定。

## c2_old_report/、c3_tampered/

- `c2_old_report/`：fresh handoff 的错误 target/旧 commit 请求、B `FAILED/STALE_REPORT` 结果。
- `c3_tampered/`：fresh handoff 追加换行的请求、`ARTIFACT_HASH_MISMATCH` 结果、原/改后 SHA256。

## c4_timeout/、c5_pair/、c5_rollback/

- `c4_timeout/`：`build_timeout=0.01` 请求、控制台、外层 `FAILED/DRAFT_FAILED`、内层 `TIMED_OUT`、容器检查。
- `c5_pair/`：A 项目隔离副本的 `invalid patch`、`validation.json`、前后 Makefile SHA（`accepted=false`、`rollback=true`、`source_unchanged=true`）。
- `c5_rollback/`：E10 B 的 `reject-test`/`reject-patch` 历史参考。

## c6_secret/、c7_isolation/、c8_api/

- `c6_secret/`：假 Key 前后 SHA256、命中/清理扫描、E13 证据 867 文件 0 命中、`secret_scan.py . --history`（606 文件）与 `--image` 镜像扫描（0 命中）。
- `c7_isolation/`：失败任务 `job-26860...`、成功任务 `job-02f85b97...` 结果与隔离核对。
- `c8_api/`：fresh C1 请求的 API 摘要、提交/重复/冲突/越界、轮询终态 `job-3974276f...`、95 个产物清单、`validation.json` 下载、服务端日志与启动命令。

## h1_jsmn/、h2_inih/、h3_tiny_aes/

每项含 `request-e12.json`、`result.json`、`draft.json`、`incremental-report.json`、`candidate.patch`、`repair-plan.json`、`validation.json`、`recheck.json`、`draft-build-result.json`、`draft-iter-01-stderr.log`。三项均 `SUCCEEDED`，补丁只加缺失的 `extra.h`，H2 保留 RD `unused.h`。

## ci_four_services/

E13 门禁 CI 的本地预检（不是 E14 交付）：四容器 `healthy` 后运行 `orchestrate.py`，五阶段 `SUCCEEDED`，`job-2cefa6521a1849aa9cfe51b7ea680382`，162 个产物；`services.log` 为四角色日志，`scan.txt` 为 `text_files=152 hits=0 errors=0`。该预检暴露并修复了 compose 以 root 运行时 Git `dubious ownership` 的问题（在四个服务环境设置 `safe.directory=*`）。

## tests/、environment/

- `tests/e11e12-tests.log`：E12 基线 21 项测试 `OK`。
- `tests/e13-tests.log`：E13 7 项测试 `OK`（课程 handoff 3 + 本人 B 侧 4）。
- `environment/image-id.txt`、`toolchain.txt`：镜像与容器工具链。
- `environment/baseline-result.json`：固定样例五阶段基线 `job-d3d68e73...`。
- `summary.json`：C1/C1′/C2/C3/C4/C5/C7/C8/H1/H2/H3 的 job/trace/commit/校验汇总。
