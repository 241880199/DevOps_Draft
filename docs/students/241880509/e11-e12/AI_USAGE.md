# AI 使用记录（E11 B 轨道）

工具/模型/日期：Claude Code 编程助手（会话模型标识 `deepseek-flash[1m]`），2026-11-11。

输入上下文与问题：课程 E11 操作手册与实验包（`run_e11e12.py`、`pipeline.py`、`server.py`、`test_contract.py`、`prepare.py`、DRAFT 回放适配器）、个人 E8–E10 仓库与报告、E11 课堂任务说明，以及本人学号 241880509。本人轨道为 B（DRAFT→MDFixer），任务是完成 E11-B、macro/mixed 自主任务、`STALE_REPORT` 负例、契约测试与真实运行证据，并整理可复核的报告。

模型建议：

- 在个人仓库副本 `exp6/group-repo` 中导入 `run_e11e12.py` 与 `labs/e11e12`，不覆盖既有 `labs/e8e10`；用仓库内 E9 版 `lab.py`（含 `patch()` 去重）作为下游。
- 先构建 `course-e11e12:241880509`、跑契约测试，再 `prepare` 生成固定样例，运行 `mode=e11-b`，保留 `result.json`、四阶段封装、DRAFT 两轮日志、补丁、验证与重检。
- 新增 5 个 B 轨道个人测试：双 MD 修复且保留 RD、macro/mixed 补丁落点、`STALE_REPORT`、fixed-md envelope commit 校验。
- 用篡改 commit 的固定 MD 做负例，确认 `result.json` 为 `FAILED` 且不进入 `repair`。
- 启动真实 HTTP API，以 `e11-b.json` 提交，验证 202 受理、同键同任务、冲突 409、越界 400、轮询终态和下载哈希。

采纳/拒绝及理由：

- **采纳**阶段 envelope + `check_envelope()`：报告中的 `schema_version/kind/commit/status` 是所有下游消费的前提；负例能稳定复现 `STALE_REPORT`。
- **采纳** DRAFT 两轮真实构建与同一镜像运行：只验证构建退出码无法证明程序输出正确；`output_matches=true` 是必要条件。
- **采纳**五项验证后才写回 Makefile：构建成功但仍有 MD 的候选必须在 `no_missing=false` 时拒绝，这是 E10 的边界延续。
- **采纳** macro/mixed 两种声明风格的补丁落点测试：手册 B 轨道自主任务要求核对补丁位置。
- **拒绝**把 A 轨道（BuildChecker→EChecker）写入个人报告：本人只负责 B 轨道；共享包中的 A 代码和包级 CI 不作为个人成果。
- **拒绝**在 E11 提前切换为真实增量报告：手册明确 E12 才切换；提前切换会把 E12 的工作混入 E11 结论。
- **拒绝**修改 `pipeline.py`/`server.py` 的编排逻辑：现有实现已满足 E11 契约；在没有独立缺陷证据时改动核心代码会增加回归风险，个人贡献以测试、负例和环境适配为主。

人工修改与分工：顾家谭提供学号、仓库、分支、个人身份和运行环境；AI 助手在用户授权下于本机 WSL2 执行手册命令、导入代码、生成证据并整理报告草稿。**git 写操作（分支、add、commit、push、PR）按课程规则和用户要求全部留给本人**，AI 未执行。本人在报告生成后完成分支 `e11-e12-integration`、提交 `b322793` 与 push；push 触发的 `e11e12-integration`、`e7-b-quality-gate`、`e8e10-quality-gate` 三个检查均为 success。报告中的镜像 ID、commit、job_id、trace_id、artifact SHA256、测试数量与 OUT 均取自真实运行输出，未手工编造。

实际验证命令/输入/结果：

- `python3 run_e11e12.py build` → 镜像 `course-e11e12:241880509`，ID `sha256:91c3d7dee370...`，退出 0。
- `python3 run_e11e12.py test` → `Ran 15 tests ... OK`，退出 0（原 10 + 新增 5 项 B 轨道测试）。
- `python3 run_e11e12.py prepare` → 生成 `data/integration-sample`，base `948585f`、target `2fe9a50`。
- E11-B → `SUCCEEDED`，`job-f9f8caa936014d008d65143abe60a505`，`trace-1a5638c3ded341b79b603c98ea9a82e6`；iter-01 `MISSING_MAKE`、iter-02 exit 0、镜像 `sha256:5a5d7bf3...`、输出 `1`；`validation.accepted=true`；重检仅 RD。
- 自主任务 B → macro/mixed 两个测试通过，补丁分别落在 `DEPS` 变量行和 `main.o` 规则行。
- STALE_REPORT → `FAILED`，`stages=['draft']`。
- HTTP API（`e11-b.json`）→ 202、同键同 job、冲突 409、越界 400、终态 `SUCCEEDED`、下载三处 SHA256 一致。

参考实现与个人贡献边界：课程包提供 `run_e11e12.py`、`labs/e11e12` 的编排、API、契约测试、DRAFT 回放与迁移环境；E8–E10 的 `lab.py`、BuildChecker 和既有测试来自个人仓库。本次个人贡献是 5 个 `test_student.py` B 轨道测试、E11-B 的真实运行证据、macro/mixed 自主任务与 `STALE_REPORT` 负例、环境适配（镜像站基础镜像与 docker CLI，digest 不变）、B 请求的 API 联调记录，以及本报告/ADR/AI 记录。未调用外部大模型 API，DRAFT 的候选为保存回放。
