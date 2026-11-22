# E14 证据索引

所有文件来自 2026-11-22 在课程服务器 `/root/241880199/e14/group-repo` 的真实运行。执行提交 `081924dc9acd1560755334b87ffdd4ac05dde64d`（分支 `e13-e14`）；镜像 `course-e11e12:241880199`，`sha256:f0419fb5c1150957284792e1fd8494ed8e57d830a7a530111cb6aed5504b0640`。

证据目录共 996 个文件。为控制体积，已排除各工作目录中的 `.git`、`base-project/`、`target-project/` 源树副本和 `draft-build/project/`；完整产物字节哈希仍记录在各目录的 `result.json.artifacts` 中。

## work/：八次运行

| 目录 | 入口 | 请求 | 结果 |
|---|---|---|---|
| `e14-sample-01/` | E11–E12 `run_e11e12.py` | 固定样例 `e12.json` | `SUCCEEDED`，`job-63e15bc5189042c8bdd738a4f6d6b978`，156 个产物 |
| `e14-real-01/` | E11–E12 | B 真实项目 `add734a → 77b40f` | `SUCCEEDED`，`job-4d73635d0e7a4a6caf57603b1d7a0d70`，155 个产物 |
| `e14-a-01/` | E11–E12 | A 真实项目 `e31c977 → 93ef2b3` | `SUCCEEDED`，`job-785fb612165f4bab94b240bd3c50dcc4`，157 个产物 |
| `e14-compose-sample-01/` | 四服务 `orchestrate.py` | 固定样例 | `SUCCEEDED`，`job-53e62b1c1bd64ed9939e2cad9d96241f`，162 个产物 |
| `e14-compose-real-01/` | 四服务 | B 真实项目 | `SUCCEEDED`，`job-6bfaf72120874bd0b821510923f4a182`，160 个产物 |
| `e14-compose-a-01/` | 四服务 | A 真实项目 | `SUCCEEDED`，`job-aa83d9a7866947eabcadea9790d0ca20`，162 个产物 |
| `e14-fault-timeout-01/` | 四服务 | `build_timeout=0.01` | `FAILED`，`job-df5fdb54ad4a42078c7f03c8f2606a93`，DRAFT `TIMEOUT`，`stages=[]` |
| `e14-fault-retry-01/` | 四服务 | 原固定样例 | `SUCCEEDED`，`job-17961b8a04c844268ad3c4b53803e586`，162 个产物 |

每个成功目录包含：

- `request.json`、`result.json`；
- 五阶段文件 `draft.json`、`full-check.json`、`incremental-check.json`、`repair.json`、`recheck.json`；
- 四服务目录额外含各阶段 HTTP 响应（`*-response.json`）、内层 `incremental/incremental-check.json`、`repair-work/candidate.patch`、`repair-work/validation/validation.json`；
- DRAFT 两轮迭代日志（`draft-build/iter-01/`、`iter-02/`）；
- `logs/`：git clone/checkout 等快照日志。

`e14-fault-timeout-01/` 包含失败结果与 DRAFT HTTP 422 响应，不包含任何成功阶段。

## build/：环境、Compose 与日志

- `e14-image-build.log`、`e14-image-id.txt`：镜像构建与完整 ID。
- `e14-toolchain.txt`：宿主机、Docker/Compose 版本、容器内 gcc/make/git/strace/python 版本。
- `e14-tests.log`：E11–E12 21 项测试 `OK`。
- `e14-e13e14-tests.log`：E13/E14 7 项测试 `OK`。
- `e14-prepare.log`：固定样例生成。
- `e14-sample-console.log`、`e14-real-console.log`、`e14-a-console.log`：E11–E12 三次运行的控制台与退出码。
- `compose-config.yaml`、`compose-up.log`、`compose-wait.log`、`compose-ps.txt`、`compose-ps-after-down.txt`、`compose-down.log`：Compose 配置、启动、健康等待和关闭。
- `compose-services.log`：四角色日志（`role/job_id/trace_id/status/elapsed_ms`，失败含 `error_code`）。
- `compose-sample-console.log`、`compose-real-console.log`、`compose-a-console.log`、`compose-fault-console.log`、`compose-fault-retry-console.log`：四服务五次运行的控制台。
- `compose-scan.txt`：`runtime log scan: text_files=640 hits=0 errors=0`。
- `e14-verify.txt`：对归档证据重新执行五阶段、job/trace、报告 SHA、补丁接受、recheck 无 MISSING 和产物哈希校验，末行 `E14_VERIFY=PASS`。源树副本按归档规则排除，脚本只校验实际归档文件并记录排除数量。
- `fault-container-check.txt`：故障后的容器、镜像和 DRAFT 进程检查。
- `e14-repo-state.txt`：`origin`、`git status`、`HEAD` 和 `v0.9-rc` 标签查询（本地/远端均为空）。该文件是运行时的快照；之后 E13 已通过 PR #14 合并到 `main`（`ecc5d08`），发布标签以最终 Release 为准。

## requests/：请求输入

- `e14-real-request.json`（SHA256 `6be08eae18698c6fcde8ad7fbc42d0c4fdeca2737dbaedf549c957250743b023`）：B 真实项目，外部 A 报告 SHA `3f66b60d...`。
- `e14-a-request.json`（SHA256 `47743854304825e5688a31e6294693a823faf76b24afd51029687b62e9424abb`）：A 真实项目，外部 A 报告 SHA `c574b1d5...`。
- `e14-timeout.json`（SHA256 `0b440c88260cef158bcf84d0b9080201ed606f2ce9499869f56e391e6970bf39`）：固定样例 + `build_timeout=0.01`。

## 未包含/边界

- 未包含课程服务器密码、SSH 密钥或任何真实凭据；`scan_runtime_logs.py` 对五个编排目录和服务日志扫描 0 命中。
- A 组 E14 的已合并 SHA、正式镜像和 CI 证据未提供；本目录只包含 B 侧在 `081924d` 上的运行，以及使用 A 已公开项目提交 `93ef2b3` 的运行。
- `v0.9-rc` 尚未创建：`e14-repo-state.txt` 记录了本地和远端查询均为空。
