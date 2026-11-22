# AI 使用记录（E14）

工具/模型/日期：Claude Code 编程助手（会话模型标识 `deepseek-flash[1m]`），2026-11-22。

## 输入上下文与问题

输入：

- E14 操作手册（`02_操作手册/02_E14候选发布.md`、`00_公共准备.md`）和候选发布模板；
- 远端 E13 分支 `origin/e13-e14`（`081924d`）及其 E13 门禁记录、C1–C8/H1–H3 证据；
- A 组公开仓库 `https://github.com/Ezio927/DevOps_BuildChecker`（E13 记录中的 A `main c68a87e`）与 A 项目提交 `e31c977 → 93ef2b3`；
- 课程服务器信息文件（IP/账号/密码只用于登录，未写入仓库或报告）；
- 服务器已有 Docker 29.1.3、Python 3.10.12 和 E11–E12 课程材料。

问题：在 E13 门禁分支上完成 E14 的候选选择、E11–E12 五阶段回归、四容器部署、固定样例与 A/B 真实项目 E2E、受控故障注入与恢复、日志扫描，并整理候选发布材料。

## 模型建议与取舍

采纳：

- **在课程服务器 `/root/241880199/e14/group-repo` 新建工作副本**，从 GitHub 拉取 `e13-e14`，避免复用旧 E4/E5 工作区。
- **使用课程包的四容器方案**：`labs/e13e14/compose.yaml` + `service.py` + `orchestrate.py`，四个角色分别监听 18081–18084。
- **镜像固定**：构建 `course-e11e12:241880199` 并记录完整 image ID，不使用 `latest`。
- **真实项目用 A/B 双方提交**：B 项目 `add734a → 77b40f`，A 项目 `e31c977 → 93ef2b3`；外部增量报告分别使用 E13 已归档的 `3f66b60d...` 和 `c574b1d5...`，请求中带 SHA256。
- **故障注入用 0.01 秒超时**：先在全新目录确认 `FAILED/TIMEOUT`，再用原请求在新目录重试成功；检查没有残留容器或 Docker 客户端进程。
- **证据只从真实运行复制**：job/trace、镜像 ID、产物数量、日志扫描结果都取自服务器输出；没有手写或猜测 ID。

拒绝：

- 拒绝把“四个容器 healthy”当作 E2E 成功证据；必须看五阶段产物和角色日志。
- 拒绝用 `latest` 或未固定 ID 的镜像填充发布清单。
- 拒绝在 E13 未合并时直接创建 `v0.9-rc` 标签；先写“候选待发布”，把合并与打标签留给有权限的人。
- 拒绝把课程服务器密码、SSH 私钥或 A 组凭据写入仓库、证据或报告。
- 拒绝用教师固定样例结果冒充 A/B 真实项目结果；两类运行在报告和证据目录中分开列。

## 人工修改与责任边界

- 用户提供课程服务器信息文件并明确要求“完成 E14”；AI 在该服务器上执行 fetch/clone、镜像构建、测试、五阶段运行、四容器编排、故障注入、证据整理和文档草稿。
- **git 写操作（提交、推送、PR、`v0.9-rc` 标签/Release）未由 AI 执行**；本轮只改工作区文件，等待仓库维护者决定。
- 报告中的镜像 ID、commit、job_id、trace_id、产物数量、测试结果和 SHA256 均来自服务器实际命令输出，未手工编造。
- 服务器密码没有出现在任何提交文件、证据文件或本记录中。

## 实际验证命令与结果

服务器工作副本：`/root/241880199/e14/group-repo`，`git rev-parse HEAD` = `081924dc9acd1560755334b87ffdd4ac05dde64d`。

```text
python3 run_e11e12.py build
  → course-e11e12:241880199，image ID sha256:f0419fb5c1150957284792e1fd8494ed8e57d830a7a530111cb6aed5504b0640
python3 run_e11e12.py test
  → Ran 21 tests ... OK
python3 run_e11e12.py prepare
  → /course/data/integration-sample
python3 run_e11e12.py run --request data/integration-sample/e12.json --out work/e14-sample-01
  → SUCCEEDED，job-63e15bc5189042c8bdd738a4f6d6b978，五阶段，156 个产物
python3 run_e11e12.py run --request data/e14-real-request.json --out work/e14-real-01
  → SUCCEEDED，job-4d73635d0e7a4a6caf57603b1d7a0d70，target 77b40f，155 个产物
python3 run_e11e12.py run --request data/e14-a-request.json --out work/e14-a-01
  → SUCCEEDED，job-785fb612165f4bab94b240bd3c50dcc4，target 93ef2b3，157 个产物
docker compose -f labs/e13e14/compose.yaml -p e14-241880199 up -d --wait
  → 4 个容器 healthy（buildchecker/echecker/draft/mdfixer，127.0.0.1:18081–18084）
python3 labs/e13e14/orchestrate.py --request data/integration-sample/e12.json --out work/e14-compose-sample-01
  → SUCCEEDED，job-53e62b1c1bd64ed9939e2cad9d96241f，162 个产物
python3 labs/e13e14/orchestrate.py --request data/e14-real-request.json --out work/e14-compose-real-01
  → SUCCEEDED，job-6bfaf72120874bd0b821510923f4a182，160 个产物
python3 labs/e13e14/orchestrate.py --request data/e14-a-request.json --out work/e14-compose-a-01
  → SUCCEEDED，job-aa83d9a7866947eabcadea9790d0ca20，162 个产物
python3 labs/e13e14/orchestrate.py --request data/e14-timeout.json --out work/e14-fault-timeout-01
  → FAILED，job-df5fdb54ad4a42078c7f03c8f2606a93，DRAFT HTTP 422 / error_code TIMEOUT，stages 为空
python3 labs/e13e14/orchestrate.py --request data/integration-sample/e12.json --out work/e14-fault-retry-01
  → SUCCEEDED，job-17961b8a04c844268ad3c4b53803e586，162 个产物
python3 labs/e13e14/scan_runtime_logs.py <五个编排目录> build/compose-services.log
  → runtime log scan: text_files=640 hits=0 errors=0
docker compose ... down
  → 只关闭 e14-241880199，共享 Docker 服务未停止
```

远端 CI：`081924d` 上的 `contracts`、`e7-b-quality-gate`、`e8e10-quality-gate`、`e11e12-integration`、`four-services` 五个检查均为 success；`four-services` 作业链接为 `https://github.com/241880199/DevOps_Draft/actions/runs/45022754030/job/137209051503`。

## 状态更新与需人工决定

- E13 已通过 PR #14 合并到 `main`（`ecc5d08`，2026-11-22）；本报告中 E14 运行基于其第一父提交 `081924d`。
- `v0.9-rc` 标签在 E14 运行时尚未创建；按本轮决定先合并 E14 证据并保持“候选待发布”，待 A 组材料与人工 review 补齐后再发布。
- A 组 E14 的已合并 SHA、镜像 ID/digest、CI 链接和签收仍需要 A 组提供；本次 RC 只覆盖 B 仓库 `241880199/DevOps_Draft`。
