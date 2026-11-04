# E10 B 证据索引

所有文件来自 2026-11-04 的真实运行。容器镜像 `course-e8e10:241880509`（`sha256:6c51868fa20c79c8978909d71ae204f74a5c3322b38d0c819aa166f5a54c2b7d`），手工 OUT 为 `work/e10-B-manual.tz03UM`，一键复验 OUT 为 `work/e10-B-postchange-20261104-125109`。

## e10-B-manual.tz03UM/

| 文件/目录 | 内容 |
|---|---|
| `fixed-md-report.json` | C0 固定 MD 报告，样例内部提交 `4d2637e...`；MISSING `main.o←config.h`、REDUNDANT `main.o←unused.h` |
| `candidate.patch` | 只修改 Makefile 的候选补丁：`main.o` 增加 `config.h` |
| `patch-plan.json` | 声明风格 `direct`，目标 `main.o`，依赖 `config.h` |
| `source-before.Makefile` | 接受前源 Makefile 字节副本 |
| `source-after-accept.Makefile` | 接受后源 Makefile 字节副本；坏 Patch 拒绝后与源文件 `cmp` 一致 |
| `broken.patch` | 内容为 `invalid patch` 的无效候选 |
| `reject-test/` | 故意错误测试预期（99）的验证：`validation.json`、`build.log`、`incremental.log`、`recheck.json`、`sandbox/` |
| `accept/` | 正确候选的验证：五项检查全真，写回 Makefile；含构建/增量日志、重检报告和沙箱源码 |
| `reject-patch/` | 坏 Patch 的验证：`checks={}`，`error` 为 `git apply` 的 `No valid patches in input`，源字节不变 |
| `student-extension/` | 自主任务：Makefile 补 `config.h`、`main.c` 增加 `extra.h` 的候选；构建/测试/头文件变化通过但 `no_missing=false`，被拒绝 |
| `recheck-buildchecker/` | 最终受测项目的真实 BuildChecker 动态重检：`findings.json`（仅 REDUNDANT `main.o←unused.h`）、`actual-graph.json`、`declared-graph.json`、`make-db.txt`、`processes.json`、构建日志 |
| `steps/` | `classroom_helpers.sh` 保存的每一步容器输出和 `STEP_EXIT_CODE` |
| `results.csv` / `gate.json` | 三类判定：test-rejection、accepted、patch-rejection 均为 True；gate passed、rows=3 |
| `student-source-commit.txt` | 外层学生源码执行时 SHA `32028b358d96dbd57a902e209c114b2f640c98c3` |
| `environment-image-id.txt` | 本次镜像完整 ID |
| `结论.txt` | 本次 E10 B 的一句话结论 |

## e10-B-postchange-20261104-125109/

一键入口 `python3 run_lab.py e10 --track B --out work/e10-B-postchange-20261104-125109` 的复验结果：`results.csv`、`gate.json` 和三份 `validation.json`。退出码 0，输出 `COMPLETED e10 B`。

## 其他

- `unit-tests-20261104-125056.log`：镜像内 11 项单元测试，`Ran 11 tests ... OK`，退出 0。
- `environment-build-manual-20261104-124845.log`：镜像构建日志；因 Docker 29.1.3 旧版构建器不支持 `--progress=plain`，使用等价的 `docker build -f ... -t course-e8e10:241880509 labs/e8e10/environment`。
- 归档副本已去除内部 `.git`、`*.o` 和 `app` 二进制，保留 JSON、日志、补丁和源码；原始 OUT 仍在本机 `work/` 下。
