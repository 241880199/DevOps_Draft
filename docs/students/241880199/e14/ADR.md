# ADR-014：四角色服务、受控超时与候选发布门禁

编号：ADR-014
日期：2026-11-22
作者：张苏楠 / 241880199（B03 组，B 轨道）

## 问题

E14 要求在通过 E13 门禁的提交上完成三件事：

- 用四个独立容器分别运行 BuildChecker、EChecker、DRAFT、MDFixer，并证明每个角色都实际处理了本轮请求；
- 对固定样例和配对双方的真实项目分别跑通 `draft → full-check → incremental-check → repair → recheck`；
- 做一次受控故障注入，确认失败不会被伪装成成功，然后恢复时限重试成功，并据此决定 `v0.9-rc` 是否可以发布。

需要决定：服务边界怎么切、镜像和运行参数怎么固定、故障注入用什么方式、以及 E13 门禁合并状态对 RC 的影响。

## 候选方案

1. **四个独立容器 + HTTP 边界**（采用）：沿用课程包 `labs/e13e14/service.py`、`orchestrate.py` 和 `compose.yaml`，每个角色一个容器，编排器通过 `127.0.0.1:18081–18084` 调用 `/v1/run`，阶段数据用容器内 `/course/...` 路径传递。
2. **单容器串行执行四项能力**：沿用旧 `run_e11e12.py`。实现简单，但无法证明四个角色分别处理了请求，也无法分别查看角色日志；不满足 E14 的部署要求。
3. **用 `latest` 或重新拉取的镜像**：部署方便，但无法把证据固定到实际运行的镜像字节；E14 明确禁止浮动的 `latest`。
4. **直接在 E13 分支上打 `v0.9-rc`**：省一次合并，但 E14 要求候选来自“E13 门禁通过且已合并的提交”；决策时 E13 尚未合并（PR #13 为 closed/unmerged，后续由 PR #14 合并为 `ecc5d08`），不能绕过。

## 采用方案与原因

采用方案 1，并加两条纪律：

- **镜像固定**：使用 `course-e11e12:241880199`，记录 `docker inspect` 的完整 ID `sha256:f0419fb5c1150957284792e1fd8494ed8e57d830a7a530111cb6aed5504b0640`；不写 `latest`。
- **故障注入用真实超时**：复制固定样例请求，把 `build_timeout` 改为 `0.01`，在全新 `work/` 目录运行。要求外层 `result.json` 为 `FAILED`、阶段列表为空、DRAFT 返回 `TIMED_OUT`/HTTP 422；随后用原请求在新目录重试并成功。

理由：

- 四个角色独立后，`docker compose logs` 可以按角色核对 `role/job_id/trace_id/status/elapsed_ms`；仅“四个容器 healthy”不再是成功证据。
- 用 0.01 秒超时触发的是 DRAFT 的真实 `TimeoutError`，不是人为写一个失败 JSON；失败路径、退出码和清理行为都可复核。
- 镜像 ID、Compose 配置和请求 JSON 一起存档，证据可以按字节重放。

## 输入输出与边界

| 对象 | 关键字段/路径 |
|---|---|
| Compose 项目 | `e14-241880199`，端口仅绑定 `127.0.0.1:18081–18084` |
| 共享工作目录 | `${E14_ROOT}:/course`，DRAFT 额外挂载 `/var/run/docker.sock` |
| 固定样例请求 | `data/integration-sample/e12.json` |
| B 真实项目请求 | `data/e14-real-request.json`，`add734a → 77b40f` |
| A 真实项目请求 | `data/e14-a-request.json`，`e31c977 → 93ef2b3` |
| 故障请求 | `data/e14-timeout.json`，仅把 `build_timeout` 改为 `0.01` |
| 编排输出 | `work/e14-compose-*/result.json` 及五阶段文件、`incremental-check.json`、补丁、validation |
| 角色日志 | `docker compose -p e14-241880199 logs --no-color` |

约束：当前 profile 仍只支持 `main.c/helper.c`、显式 Make 规则和预期输出 `1`；A 项目的 Dockerfile.broken 与固定样例同构，因此复用固定样例的候选 Dockerfile。

## 验证

- E11–E12 基线：`python3 run_e11e12.py test` → `Ran 21 tests ... OK`。
- 固定样例五阶段（E11–E12 入口）：`job-63e15bc5189042c8bdd738a4f6d6b978`，`trace-d55519162cc4452f992197ddd99d7065`，156 个产物，证据关联检查 PASS。
- B 真实项目（E11–E12 入口）：`job-4d73635d0e7a4a6caf57603b1d7a0d70`，target `77b40f`，155 个产物；来源 A 报告 `job-e6ed45e4...`、SHA `3f66b60d...`。
- A 真实项目（E11–E12 入口）：`job-785fb612165f4bab94b240bd3c50dcc4`，target `93ef2b3`，157 个产物；来源 A 报告 `job-84674fd1...`、SHA `c574b1d5...`。
- 四服务固定样例：`job-53e62b1c1bd64ed9939e2cad9d96241f`，162 个产物。
- 四服务 B 真实项目：`job-6bfaf72120874bd0b821510923f4a182`，160 个产物。
- 四服务 A 真实项目：`job-aa83d9a7866947eabcadea9790d0ca20`，162 个产物。
- 故障注入：`job-df5fdb54ad4a42078c7f03c8f2606a93` → `FAILED`，DRAFT `TIMEOUT`，阶段为空；恢复后重试 `job-17961b8a04c844268ad3c4b53803e586` → `SUCCEEDED`。
- 日志扫描：`scan_runtime_logs.py` 检查 640 个文本文件，`hits=0 errors=0`。

## 后果

- 代价：四个容器各 768 MiB 内存、1 CPU，HTTP 串行调用比单进程慢；DRAFT 需要 Docker socket，必须限制在隔离测试仓库。
- 收益：角色、trace、失败码和产物哈希都可独立核对；故障恢复有可重放证据。
- 已知限制：
  - E13 已通过 PR #14 合并到 `main`（`ecc5d08`，2026-11-22）；E14 证据 PR #15 合并后，本轮决定先保持“候选待发布”，待 A 组材料和人工 review 补齐后再把 `v0.9-rc` 固定在最终验收提交上。
  - A 组 E14 的已合并 SHA、正式镜像 ID/digest 和签收尚待 A 组提供；本报告中的 A 项目运行使用 E13 已公开的 A 项目提交 `93ef2b3` 和 A 代码 `main c68a87e`。本次 `v0.9-rc` 只覆盖 B 仓库（`241880199/DevOps_Draft`）。
  - 四服务只在单台课程服务器、单机 Docker 上验证；跨机 API 联调仍沿用 E12 的 SSH 本地端口转发，不开放公网端口。
