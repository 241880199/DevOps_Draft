# AI使用记录

工具/模型/日期：Claude Code（deepseek-flash），2026-11-03。

输入上下文与问题：课程 E8—E10 手册（B 组 E8）、`labs/e8e10/lab.py`、`test_profile.py`、个人测试示例与报告模板。任务是按 B 组 E8 路线在本组服务器生成真实证据，并完成自主测试与提交材料。

模型建议：

- 按手册第 0—8 步逐条执行，固定 MD 报告、候选 Patch、旧报告拒绝三类产物分别保存。
- 自主任务选择“只有 REDUNDANT 的报告不产生删除操作”，新增 `StudentE8B.test_redundant_only_report_does_not_delete`。
- 不修改 `lab.py` 的检测/补丁算法，只新增测试，避免改变参考实现的判定。

采纳/拒绝及理由：

- 采纳手册路线与新增测试。测试的独立预期是 `patch()` 只处理 MISSING，因此只有 REDUNDANT 时 diff 与 plan 为空、源文件字节不变。
- 未采纳“删除 unused.h”或“直接手改 Makefile”的捷径，理由见 ADR。

人工修改：测试类由 AI 按学生选定的场景起草并执行；学生为最终提交与报告内容的责任人。报告中的 SHA、OUT、镜像 ID、测试数量均取自服务器实际命令输出，未使用材料中的示例运行数据。

实际验证命令/输入/结果：

- `docker run ... python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v` → `Ran 8 tests ... OK`，退出 0。
- `python3 run_lab.py e8 --track B --out work/e8-B-postchange-20261103-194501` → `COMPLETED e8 B`。
- 手工分步 OUT `work/e8-B-manual.dK1wtN`：`COMMIT_MATCH`、`PATCH_GENERATED_SOURCE_UNCHANGED`、`APPLY_CHECK_PASS_SOURCE_CLEAN`、`EXPECTED_REJECTION STALE_REPORT`、`SOURCE_BYTES_UNCHANGED`。

参考实现与个人贡献边界：`labs/e8e10/lab.py`、`run_lab.py`、环境镜像与原有 7 项测试来自课程实验包；个人贡献是新增 1 项测试（`test_profile.py` 增加 18 行）、本次真实运行证据与报告/ADR/AI_USAGE。未调用模型生成被检测项目的源代码。
