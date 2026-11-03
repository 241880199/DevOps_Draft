# AI 使用记录

工具/模型/日期：Codex（GPT-5），2026-11-03。

输入上下文与问题：课程 E9 B 手册、DRAFT 仓库的 `labs/e8e10/lab.py`、`test_profile.py`、个人测试示例，以及 241880567 在课程服务器上的真实运行环境。任务是在独立分支完成三种声明风格验证、加入自主实现和测试，并保留可复核证据。

模型建议：

- 按手册创建 direct、macro、mixed 三个独立 C0 样例，比较 Patch、修改计划和原 Makefile 字节。
- 用 macro 样例的独立副本演示 Patch 真正落地，不修改原输入项目。
- 自主任务选择重复 MISSING 去重：在 `patch()` 中维护 `(target, dependency)` 集合，并增加 macro 风格测试验证只追加一次 `config.h`。

采纳/拒绝及理由：

- 采纳手册路线和 `(target, dependency)` 去重。该粒度不会误删不同目标所需的同名头文件。
- 未采用按 dependency 全局去重，因为它会漏掉不同目标的合法声明。
- 未扩展为共享变量跨目标影响分析；该任务需要新的声明图和影响范围模型，超出本次受限实现。

人工修改：报告中的 OUT、镜像 ID、源码 SHA、测试结果与 Patch 内容均取自 241880567 服务器真实运行输出。分支合并、PR 与最终质量门槛由仓库维护者在复核后执行。

实际验证命令/输入/结果：

- `lab_new_run e9 B` -> `OUT=work/e9-B-manual.XzsO0N`。
- 手工 direct/macro/mixed 路线 -> 三次 `STYLE_PASS`，`STEP_EXIT_CODE=0`。
- `apply-demo` -> `APPLY_TO_COPY_PASS`，`STEP_EXIT_CODE=0`。
- `python3 run_lab.py e9 --track B --out work/e9-B-postchange-20261103-213027` -> `COMPLETED e9 B`，退出码 0。
- `python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v` -> `Ran 9 tests in 0.194s`，`OK`，退出码 0。

参考实现与个人贡献边界：课程包提供 `fixture`、`scan`、`patch`、三种声明样例和原 7 项测试；前次 E8 工作已增加 1 项 B 组测试。本次个人贡献是 `patch()` 的 MISSING 去重、`StudentE9B` 独立测试、E9 B 真实运行证据及本报告/ADR/AI_USAGE。
