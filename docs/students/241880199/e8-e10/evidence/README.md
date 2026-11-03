# E8 B 组证据索引

本目录是 E8 手工路线与复验的关键证据副本；原始目录仍在服务器仓库 `work/` 下（`work/` 被 Git 忽略）。

- `e8-B-manual.dK1wtN/`：手册第 0—8 步的原始 OUT 副本（不含 `project/.git`）
  - `fixed-md-report.json`：固定 MD 报告，commit `fc5ee2a028b533d1a2166605386a56542e186627`
  - `candidate.patch` / `patch-plan.json`：只补 `main.o: main.c unused.h config.h`，style=direct
  - `expected-failure.json`：`STALE_REPORT` 拒绝证据
  - `student-source-commit.txt`：执行时外层仓库 HEAD `1ac4d83`
  - `environment-image-id.txt`：`sha256:b20d2faf…`
  - `steps/`：每步容器日志与 `STEP_EXIT_CODE`
  - `project/`：原输入（C0 样例文件，不含内部 `.git`）
  - `结论.txt`
- `e8-B-postchange-20261103-194501/`：新增测试后的一键复验 OUT
- `unit-tests-20261103-194500.log`：8 项单元测试全部通过
- `environment-build-20261103-194319.log`：`course-e8e10:241880199` 镜像构建日志

外部归档：`/root/devops-submissions/241880199/E8-20261103-194608.tar.gz`；本机副本 `D:\Projects\DevOps\E8\E8-20261103-194608.tar.gz`。
