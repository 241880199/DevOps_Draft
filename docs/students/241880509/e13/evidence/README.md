# E13 B 轨道证据索引

所有文件来自 2026-11-22 的真实运行。镜像 `course-e11e12:241880509`（`sha256:91c3d7dee370...`），容器内 Debian 13、gcc 14.2.0、GNU Make 4.4.1、strace 6.13、Python 3.13.14。B 仓库基线 `main` 为 `1394580`（E12 已合并）。

## c1_live_handoff/

| 文件 | 内容 |
|---|---|
| `a_source/` | A 的 E12 报告（`result.json`、`incremental-check.json`、`full-check.json`、`incremental-report.json`、`target-full/`；`job-96b0363cee494ae882b706e3afccd337`，target `77b40f`）；副本已做 CRLF→LF 归一，SHA256 与 A 的 `result.json` 记录一致，可直接重跑 handoff |
| `handoff-fixed-md.json` | `handoff_a_to_b.py` 输出，SHA256 `b2c94578...`，含 `source_report` |
| `request-e11-b.json` | B 请求，含 `fixed_report_sha256` |
| `result.json` / `draft.json` / `fixed-md-input.json` | B 四阶段结果、DRAFT 封装、固定 MD 输入（`source_report`） |
| `candidate.patch` / `repair-plan.json` / `repair.json` | `main.o` 增加 `config.h`、`extra.h` 的补丁与修复记录 |
| `validation.json` / `recheck.json` | 五项检查全 true；重检仅 RD `unused.h` |
| `draft-build-result.json` / `draft-iter-01-stderr.log` / `draft-verify.log` | iter-01 `MISSING_MAKE`、iter-02 成功、同镜像运行输出 `1` |
| `Makefile.before-patch` / `Makefile.after-patch` | 补丁前后字节对照 |
| `a-project.json` / `a-project.bundle` / `a-handoff-summary.json` | A 的 E13 项目 metadata、完整提交 bundle 与 job 摘要；A 只给 `job-8e9c093f...` 摘要，未发布 `result.json`/`incremental-check.json` 原始产物，C1′ 因此 BLOCKED |

## c2_old_report/、c3_tampered/

- `c2_old_report/`：handoff 错误 target 日志（`A task belongs to another target commit`）、改 commit 的请求、B `FAILED/STALE_REPORT` 结果。
- `c3_tampered/`：追加换行的请求、`ARTIFACT_HASH_MISMATCH` 结果、原/改后 SHA256。

## c4_timeout/、c5_rollback/

- `c4_timeout/`：`build_timeout=0.01` 请求、控制台、外层 `FAILED/DRAFT_FAILED`、内层 `TIMED_OUT`、容器检查。
- `c5_rollback/`：E10 B 的 `reject-test`/`reject-patch` 验证副本与核对文本（`accepted=false`、`rollback=true`、`source_unchanged=true`）。

## c6_secret/、c7_isolation/、c8_api/

- `c6_secret/`：假 Key 前后 SHA256、命中/清理扫描、E13 证据目录 867 文件扫描（0 命中）、`secret_scan.py . --history`（606 文件）与 `--image` 镜像扫描（0 命中）。
- `c7_isolation/`：失败任务 `job-26860...`、成功任务 `job-63ade...` 结果与隔离核对。
- `c8_api/`：API 摘要、提交/重复/冲突/越界、轮询终态、95 个产物清单、`validation.json` 下载、服务端日志与启动命令。

## h1_jsmn/、h2_inih/、h3_tiny_aes/

每项含 `request-e12.json`、`result.json`、`draft.json`、`incremental-report.json`、`candidate.patch`、`repair-plan.json`、`validation.json`、`recheck.json`、`draft-build-result.json`、`draft-iter-01-stderr.log`。三项均 `SUCCEEDED`，补丁只加缺失的 `extra.h`，H2 保留 RD `unused.h`。

## ci_four_services/

E13 门禁 CI 的本地预检（不是 E14 交付）：四容器 `healthy` 后运行 `orchestrate.py`，五阶段 `SUCCEEDED`，`job-2cefa6521a1849aa9cfe51b7ea680382`，162 个产物；`services.log` 为四角色日志，`scan.txt` 为 `text_files=152 hits=0 errors=0`。该预检暴露并修复了 compose 以 root 运行时 Git `dubious ownership` 的问题（在四个服务环境设置 `safe.directory=*`）。

## tests/、environment/

- `tests/e11e12-tests.log`：E12 基线 21 项测试 `OK`。
- `tests/e13-tests.log`：E13 7 项测试 `OK`（课程 handoff 3 + 本人 B 侧 4）。
- `environment/image-id.txt`、`toolchain.txt`：镜像与容器工具链。
- `environment/baseline-result.json`：固定样例五阶段基线 `job-d3d68e73...`。
- `summary.json`：C1/C2/C3/C4/C7/C8/H1/H2/H3 的 job/trace/commit/校验汇总。
