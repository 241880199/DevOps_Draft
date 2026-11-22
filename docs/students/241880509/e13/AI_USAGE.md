# AI 使用记录（E13 B 轨道）

工具/模型/日期：Claude Code 编程助手（会话模型标识 `deepseek-flash[1m]`），2026-11-22。

输入上下文与问题：E13 操作手册（公共准备、交叉测试与门禁、三个项目运行指南）、E13–E14 学生实验包（`handoff_a_to_b.py`、`scan_runtime_logs.py`、`tests/test_handoff.py`、`e13e14.yml`）、E12 已合并的 `labs/e11e12` 与 `docs/students/241880567/e12/` 证据、E13 上游项目 zip，以及本人学号 241880509。任务是更新本地仓库、完成 B 组 E13-B 交叉测试、A→B 报告交接、C1–C8、H1–H3、Secret 扫描与门禁记录。

模型建议：

- 用 `exp7/group-repo` 重新克隆 `main`（`1394580`，E12 已合并），避免在 E11 分支上做 E13；先跑 21 项基线测试。
- 导入课程 `labs/e13e14`，在 `pipeline.py` 增加可选 `fixed_report_sha256` 校验，保持 E11-B/E12 兼容。
- 使用 E12 的真实 A 报告（`job-96b0363c...`）做 A→B handoff，B 运行 `e11-b`；A 的 E13 自有项目只发布了 bundle/摘要，没有原始报告，C1′ 记为输入缺失。
- 用 A 的 E12 报告和 B 的 E12 real-project 复现 C1 交接链路；C2/C3 用错误 target、旧 commit 和追加换行验证拒绝；C4 用 `build_timeout=0.01`；C5 用 E10 的拒绝证据；C6 用假 Key；C7 用失败/成功双任务；C8 用真实 HTTP API。
- 运行 H1 jsmn、H2 inih、H3 tiny-AES-c 的 `mode=e12`，分别保存请求、结果、补丁、验证和重检。

采纳/拒绝及理由：

- **采纳** handoff + 可选哈希：满足 E13 C3，同时不破坏旧请求；直接把 `incremental-check` 交给 `patch()` 会改变 B 的输入类型契约。
- **采纳** E12 真实 A 报告做 C1 交接：报告来源、job/trace/artifact 哈希都可核验；用教师样例冒充 A 报告会违反 E13 的交换边界。
- **拒绝**用 A 分支代码在 B 环境复现 A 的自有项目报告：运行外部仓库代码需要额外授权，而且复现结果不等于 A 组员提供的原始报告；C1′ 如实记为 BLOCKED。
- **拒绝**为了让 C1′ 通过而伪造 `result.json`/`incremental-check.json`：handoff 会逐字节校验，伪造会破坏证据可信度。
- **拒绝**修改 `labs/e8e10/lab.py` 或 E12 的 `incremental_report` 路径：E13 只补 fixed-md 交接，不改已验收的检测/修复算法。

人工修改与分工：顾家谭提供学号、仓库、个人环境与 A 组公开仓库地址；AI 助手在用户授权下于本机 WSL2 执行 fetch/clone、导入代码、运行实验、生成证据并整理报告草稿。**git 写操作（分支、add、commit、push、PR、tag）全部留给本人**，AI 未执行。报告中的镜像 ID、commit、job_id、trace_id、artifact SHA256、测试数量与 OUT 均取自真实运行输出，未手工编造。

实际验证命令/输入/结果：

- `python3 run_e11e12.py test` → `Ran 21 tests ... OK`。
- `python3 -m unittest discover -s labs/e13e14/tests` → `Ran 7 tests ... OK`。
- 固定样例 `e12.json` → `SUCCEEDED`，`job-d3d68e73...`。
- C1 handoff → A job `job-96b0363c...`，报告 SHA `ee2612e4...`；B `SUCCEEDED`，`job-63ade574...`，`accepted=true`。
- C2 → `FAILED/STALE_REPORT`；C3 → `FAILED/ARTIFACT_HASH_MISMATCH`；C4 → 内层 `TIMED_OUT`、外层 `DRAFT_FAILED`；C5 → E10 两项拒绝；C6 → 命中 1/清理 0/证据扫描 0；C7 → 失败与成功 job/trace 不同且成功产物自校验；C8 → 202/同 job/409/400/下载哈希一致。
- H1/H2/H3 → 均 `SUCCEEDED`，`accepted=true`。
- 四容器本地预检 → 4 服务 healthy；`orchestrate.py` 五阶段 `SUCCEEDED`，`job-2cefa652...`，162 个产物；日志扫描 0 命中。
- 四容器首次预检在 echecker 报 Git `dubious ownership`；在 `labs/e13e14/compose.yaml` 四个服务环境加入 `GIT_CONFIG_COUNT/KEY_0/VALUE_0`（`safe.directory=*`）后通过。

参考实现与个人贡献边界：课程包提供 `handoff_a_to_b.py`、`scan_runtime_logs.py`、E14 入口与 `test_handoff.py`；E12 的 `pipeline.py`/`test_e12_student.py` 来自组员 241880567；E8–E10 的 `lab.py` 来自个人历史分支。本次个人贡献是 `pipeline.load_fixed_report` 与 fixed-md 分支改造、`test_e13_b.py` 4 项测试、E13-B 全部运行与门禁记录、A→B 交接与负例证据、H1–H3 三项运行结果。未调用外部大模型 API；A 的代码未被运行，只读取了其公开 metadata。
