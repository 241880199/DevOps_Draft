# AI 使用记录（E11）

工具/模型/日期：Claude Code 编程助手（会话模型标识 `deepseek-flash[1m]`），2026-11-11。

输入上下文与问题：课程 E11 操作手册与实验包（`run_e11e12.py`、`pipeline.py`、`server.py`、`test_contract.py`、`prepare.py`、DRAFT 回放适配器、BuildChecker 全量检测）、个人 E8–E10 仓库与报告、E11 课堂任务说明，以及本人学号 241880509。任务是完成 E11-A（全量图接入增量缓存）、E11-B（DRAFT 接入 MDFixer）、自主任务、契约测试与真实运行证据，并整理可复核的报告。

模型建议：

- 在个人仓库副本 `exp6/group-repo` 中导入 `run_e11e12.py` 与 `labs/e11e12`，不覆盖既有 `labs/e8e10`；用仓库内 E9 版 `lab.py`（含 `patch()` 去重）作为下游。
- 先构建 `course-e11e12:241880509`、跑 10 项契约测试，再 `prepare` 生成固定样例，最后分别运行 e11-a/e11-b，保留 `result.json`、阶段封装、图、日志和补丁。
- 新增 5 个个人测试：C1→C2 函数体提交复用两个目标、C2→C3 头文件指令提交刷新两个目标、macro/mixed 声明风格的补丁落点、`STALE_REPORT` 停止修复。
- 用篡改 commit 的固定 MD 做负例，确认 `result.json` 为 `FAILED` 且不进入 `repair`。
- 启动真实 HTTP API，验证 202 受理、同键同任务、冲突 409、越界 400、轮询终态和下载哈希。

采纳/拒绝及理由：

- **采纳**阶段 envelope + `check_envelope()`：报告中的 `schema_version/kind/commit/status` 是所有下游消费的前提；负例能稳定复现 `STALE_REPORT`。
- **采纳**“A 的 baseline-cache 来自真实 strace 图投影”：这是 E11-A 与 E10 增量扫描的关键差别；只复用 GCC `-MM` 无法证明全量图已接入。
- **采纳**固定 MD 留在 E11-B：手册明确 E12 才切换为真实增量报告；提前切换会把 E12 的工作混入 E11 结论。
- **采纳** 5 个个人测试与 macro/mixed 场景：手册自主任务要求核对补丁位置；测试同时固定了“函数体变化复用、指令变化刷新”的缓存语义。
- **拒绝**修改 `pipeline.py`/`server.py` 的编排逻辑：现有实现已满足 E11 契约；在没有独立缺陷证据时改动核心代码会增加回归风险，个人贡献以测试、负例和环境适配为主。
- **拒绝**把课程生成样例写成“真实项目”：`dataset.json` 明确是 `course-generated`，真实项目接入需要本组自己的仓库和两个完整 SHA，留待 E12/验收阶段。

人工修改与分工：顾家谭提供学号、仓库、分支、个人身份和运行环境；AI 助手在用户授权下于本机 WSL2 执行手册命令、导入代码、生成证据并整理报告草稿。**git 写操作（分支、add、commit、push、PR）按课程规则和用户要求全部留给本人**，AI 未执行。报告中的镜像 ID、commit、job_id、trace_id、artifact SHA256、测试数量与 OUT 均取自真实运行输出，未手工编造。

实际验证命令/输入/结果：

- `python3 run_e11e12.py build` → 镜像 `course-e11e12:241880509`，ID `sha256:91c3d7dee370...`，退出 0。
- `python3 run_e11e12.py test` → `Ran 15 tests ... OK`，退出 0（原 10 + 新增 5）。
- `python3 run_e11e12.py prepare` → 生成 `data/integration-sample`，base `948585f`、target `2fe9a50`。
- E11-A → `SUCCEEDED`，`job-e3f19aa81f8540fbaa4aeff0e6639c88`，`trace-c09b50c79156410baccf7b29e71d7bc4`；MD `config.h`/`extra.h`、RD `unused.h`；与 target 全量一致。
- E11-B → `SUCCEEDED`，`job-f9f8caa936014d008d65143abe60a505`，`trace-1a5638c3ded341b79b603c98ea9a82e6`；iter-01 `MISSING_MAKE`、iter-02 exit 0、镜像 `sha256:5a5d7bf3...`、输出 `1`；`validation.accepted=true`；重检仅 RD。
- 自主任务 A → C1→C2 `reused=['main.o','helper.o']`；C2→C3 `refreshed=['main.o','helper.o']`。
- 自主任务 B → macro/mixed 两个测试通过，补丁分别落在 `DEPS` 变量行和 `main.o` 规则行。
- STALE_REPORT → `FAILED`，`stages=['draft']`。
- HTTP API → 202、同键同 job、冲突 409、越界 400、终态 `SUCCEEDED`、下载三处 SHA256 一致。

参考实现与个人贡献边界：课程包提供 `run_e11e12.py`、`labs/e11e12` 的编排、API、契约测试、DRAFT 回放与迁移环境；E8–E10 的 `lab.py`、BuildChecker 和既有测试来自个人仓库。本次个人贡献是 5 个 `test_student.py` 测试、E11-A/B 的真实运行证据、自主任务与负例、环境适配（镜像站基础镜像与 docker CLI，digest 不变）、API 联调记录，以及本报告/ADR/AI 记录。未调用外部大模型 API，DRAFT 的候选为保存回放。
