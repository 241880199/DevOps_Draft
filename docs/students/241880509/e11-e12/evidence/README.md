# E11 证据索引

所有文件来自 2026-11-11 的真实运行。镜像 `course-e11e12:241880509`（`sha256:91c3d7dee370ed2ffaae45006e30e6f138d5249d694737bd631fee9f2d158376`），容器内 Debian 13、gcc 14.2.0、GNU Make 4.4.1、strace 6.13、Python 3.13.14。固定样例由 `run_e11e12.py prepare` 生成：base `948585fd9a7c9261694291b16d8f7c440719eb79`，target `2fe9a507740301fafd379f2f3205de0974bc5cdf`。

## e11-a-01/

| 文件/目录 | 内容 |
|---|---|
| `result.json` | `SUCCEEDED`，`job-e3f19aa81f8540fbaa4aeff0e6639c88`，`trace-c09b50c79156410baccf7b29e71d7bc4`，85 个产物清单 |
| `request.json` | E11-A 实际请求（`mode=e11-a`、base/target、repo/candidate/fixed_report） |
| `baseline-cache.json` | base 的真实 strace 图投影：`main.o←config.h/main.c`、`helper.o←helper.c` |
| `full-check.json` | 全量阶段封装（`schema_version=e11e12-1`、`kind=full-check`、base commit） |
| `incremental-check.json` | 增量阶段封装（target commit） |
| `incremental-report.json` | target 增量结果：MD `config.h`/`extra.h`、RD `unused.h`；`refreshed` 两目标、`reused` 空 |
| `baseline-full/` | base 的 `actual-graph.json`、`findings.json`、`make-db.txt`、`processes.json`、构建日志 |
| `target-full/` | target 的真实全量图、声明图、findings、make-db、processes、构建日志 |

## e11-b-01/

| 文件/目录 | 内容 |
|---|---|
| `result.json` | `SUCCEEDED`，`job-f9f8caa936014d008d65143abe60a505`，`trace-1a5638c3ded341b79b603c98ea9a82e6`，四阶段 `draft/fixed-md/repair/recheck` |
| `request.json` | E11-B 实际请求（`mode=e11-b`） |
| `draft.json` | DRAFT 阶段封装（`kind=draft`、target commit、artifact URI/SHA256） |
| `draft-build/result.json` | 两轮构建：iter-01 `MISSING_MAKE` exit 1；iter-02 exit 0、镜像 `sha256:5a5d7bf3...`；运行输出 `1` |
| `draft-build/iter-01/` | broken Dockerfile、`make: not found` 原始日志 |
| `draft-build/iter-02/` | 候选 Dockerfile、构建日志、`image-inspect.json` |
| `draft-build/verify.log` | 同镜像禁网运行输出 `1` |
| `fixed-md.json` / `fixed-md-input.json` | 固定 MD 输入及其 envelope（commit 与 target 一致） |
| `candidate.patch` | 唯一变化：`main.o: main.c unused.h config.h extra.h` |
| `repair-plan.json` / `repair.json` | 两条 `direct` 编辑与输入报告 artifact 引用 |
| `validation/validation.json` | 五项检查全 true、`accepted=true` |
| `validation/build.log`、`incremental.log`、`recheck.json` | 沙箱构建、修改 `config.h` 后重编译、重检 |
| `recheck.json` | 动态重检仅 RD `unused.h`，无 MISSING |
| `target-Makefile.after-patch` / `sample-Makefile.before-patch` | 写回后与样例源 Makefile 的字节对照 |

## autonomous-a/

| 文件 | 内容 |
|---|---|
| `request-body.json` | C1→C2（只改 `helper.c` 函数体）请求 |
| `request-directive.json` | C2→C3（只改 `config.h` 的 `#define`）请求 |
| `out-body/incremental-report.json` | `refreshed=[]`、`reused=['main.o','helper.o']`，findings 不变 |
| `directive-incremental-report.json` | `refreshed=['main.o','helper.o']`、`reused=[]`，findings 不变 |
| `result-body.json` / `result-directive.json` | 两次 `SUCCEEDED` 的 job_id/trace_id/commit |

## stale-report/

| 文件 | 内容 |
|---|---|
| `fixed-md-stale.json` | 把 `commit` 改为 `0`×40 的固定报告 |
| `request-stale.json` | 以 `mode=e11-b` 消费该报告 |
| `result.json` | `FAILED`、`error.code=STALE_REPORT`、`stages=['draft']`，未进入 repair/recheck |

## api/

| 文件 | 内容 |
|---|---|
| `api-summary.json` | 健康检查、202 受理、同键同 job、冲突 409、越界 400、终态 SUCCEEDED、下载三处 SHA256 一致 |
| `submit.json` / `submit-repeat.json` / `submit-conflict.json` / `submit-outside-data.json` | 四类提交响应 |
| `poll-final.json` | 轮询终态与 `trace_id` |
| `artifacts.json` | 85 个 artifact URI/SHA256 |
| `downloaded-incremental-report.json` | 通过文件接口下载的增量报告 |
| `server-command.json` / `container-id.txt` / `server.log` / `client.log` | 服务启动参数、容器 ID 与两端日志 |

## tests/ 与 environment/

- `tests/e11-contract-tests-20261111.log`：镜像内 15 项测试 `Ran 15 tests ... OK`，退出 0。
- `environment/e11-build-20261111.log`：镜像构建日志，`Successfully tagged course-e11e12:241880509`。
- `environment/dataset.json`、`environment/candidate.Dockerfile`：本轮固定样例的数据清单与 DRAFT 候选（候选基础镜像走镜像站，digest 不变）。
- `environment/e11-b-dockerhub-timeout.log`：首次 E11-B 在 Docker Hub 解析 `python:3.13-slim@sha256:70729...` 超时的原始日志；不计入实验失败，只作为环境适配依据。
- `environment/image-id.txt`：本次镜像完整 ID。
- `summary.json`：E11-A/B 的阶段、commit、job_id、trace_id 和 artifact SHA256 汇总。
