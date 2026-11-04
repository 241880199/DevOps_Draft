# AI 使用记录

工具/模型/日期：Claude Code 编程助手（会话模型标识 `deepseek-flash[1m]`），2026-11-04。

输入上下文与问题：课程 E10 B 手册、`labs/e8e10/lab.py`、`labs/e8e10/test_profile.py`、组内仓库 E8/E9 已有证据与报告，以及本人学号 241880509。任务是按手册完成 E10 B 的拒绝、接受、回滚与动态重检，增加有独立预期的个人测试，并生成可复核的证据和报告。

模型建议：

- 按手册第 0—10 步执行手工路线，保留每一步的 `steps/` 日志、三次 `validation.json`、源字节副本和动态重检原始文件。
- 新增 `StudentE10B` 两个测试：一个覆盖编译失败，一个覆盖“构建和功能测试都通过、但仍存在 MISSING 声明”的候选。
- 在独立副本中完成手册第 11 步：构造 Makefile 补 `config.h`、`main.c` 增加 `extra.h` 的候选，验证 `no_missing=false` 时拒绝且源 Makefile 字节不变。
- 报告中分别记录外层学生源码 SHA、样例内部 C0 提交和验证沙箱提交，避免混用。

采纳/拒绝及理由：

- 采纳隔离沙箱验证和五个检查项。它能同时保留构建失败原因、头文件变化结果和重检图，比只检查退出码更接近 E10 的质量判定目标。
- 采纳两个测试。测试一对应手册明确要求的编译失败场景；测试二补足“能构建但仍有 MD”的独立边界，两者预期不同，不是重复用例。
- 未修改 `lab.py::validate` 的算法。现有实现已经满足“全通过才写回、失败保留源字节”，在没有独立缺陷证据时改动核心逻辑会增加回归风险；个人贡献以测试和扩展证据为主。
- 未只运行一键入口。一键入口会覆盖完整流程，但手工路线能保存每一步的输入、命令和中间结果，便于教师复核。
- 未采用“先写回再回滚”的替代方案，原因是它会让源项目短暂处于未验证状态。

人工修改与分工：顾家谭提供学号、仓库、分支和个人身份；AI 助手在用户授权下于本机 WSL2 环境执行手册命令、生成证据并整理报告草稿。报告中的镜像 ID、提交 SHA、检查项、测试数量和 OUT 均取自真实运行输出，未手工编造。

实际验证命令/输入/结果：

- `lab_ready` → `lab_new_run e10 B` → `OUT=work/e10-B-manual.tz03UM`。
- 手册第 4 步 → `EXPECTED_TEST_REJECTION`，`accepted=false`、`test=false`、`rollback=true`。
- 手册第 6 步 → `ACCEPTED_ALL_CHECKS_PASS`，五项检查全真、`accepted=true`。
- 手册第 8 步 → `EXPECTED_BAD_PATCH_REJECTION`，`error` 为 `git apply` 的 `No valid patches in input`。
- 手册第 9 步 → `B_GATE_PASS`，`results.csv` 三行 `True`。
- 自主任务 → `STUDENT_EXTENSION_REJECTED_BUILDS_WITH_MD`，`build/test/header_change=true`、`no_missing=false`、`accepted=false`。
- 单元测试 → `Ran 11 tests ... OK`，`TEST_EXIT_CODE=0`。
- 一键复验 → `COMPLETED e10 B`，退出 0。

参考实现与个人贡献边界：课程包提供 `fixture`、`scan`、`patch`、`validate`、`buildchecker` 和原 7 项测试；组员 241880199 增加 `StudentE8B`，241880567 增加 `StudentE9B` 并修改 `patch()` 去重。本次个人贡献是 `StudentE10B` 两个测试、E10 B 手工与一键真实运行证据、自主扩展场景，以及本报告/ADR/AI 记录。未调用外部大模型 API，样例生成和验证均在本地容器内完成。
