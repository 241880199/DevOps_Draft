# E10 B 组决策记录

## 背景与约束

E10 B 要把固定 MD 报告生成的候选 Patch 与“是否接受”分开判定。候选必须经过补丁可应用、构建、功能测试、头文件变化重编译、重检无 MISSING 五道检查；任一道失败都不得改动源项目。仓库已有 E8/E9 的 `fixture`、`scan`、`patch`、`validate` 和 9 项测试，本次只做 E10 的验证与补充用例。

## 选择与替代方案

- 选择：沿用 `validate()` 的隔离沙箱路线。每次把源项目复制到 `evidence/<case>/sandbox`，在副本中 `git apply`、`make clean && make app`、运行 `app`、修改 `config.h` 后再构建、最后用 `scan(sandbox)` 重检；只有 `patch_applies/build/test/header_change/no_missing` 全为真时，才把沙箱 Makefile 写回源项目。
- 替代方案一：直接在源项目上应用 Patch，失败后用 `git checkout -- Makefile` 恢复。实现简单，但失败路径依赖 Git 状态，无法保留隔离构建日志，也不能保证“拒绝时源字节不变”。
- 替代方案二：只检查构建和功能测试。会接受“能编译、功能正确，但声明图仍缺头文件”的候选；本次自主任务正是在这种输入上验证了 `no_missing=false` 时必须拒绝。
- 替代方案三：先写回再验证，失败后回滚。源项目会短暂处于未验证状态，其他进程或后续命令可能读到错误 Makefile，不符合“验证通过才写回”的边界。

## 代价与覆盖范围

- 代价：每个候选都要复制项目并完整构建一次，`validate()` 还固定等待 1.05 秒以区分 `config.h` 的修改时间；本次三次判定加动态重检的总耗时明显高于只运行一次 `make`。
- 覆盖范围：只支持显式 C/Make 规则、项目内头文件和 `-O0/-O1/-O0 -DMODE=1` 配置；不处理隐式规则、条件分支、跨目标共享变量和平台相关编译选项。
- 失败语义：`checks={}` 且 `error` 非空表示 Patch 本身无法应用；`checks` 部分为真表示已执行到某道检查；两种情况都要求 `rollback=true` 和 `source_unchanged=true`。

## 验证命令与实际证据

- 手工分步：`work/e10-B-manual.tz03UM`，依次得到 `EXPECTED_TEST_REJECTION`、`ACCEPTED_ALL_CHECKS_PASS`、`EXPECTED_BAD_PATCH_REJECTION`、`B_GATE_PASS`。
- 一键复验：`python3 run_lab.py e10 --track B --out work/e10-B-postchange-20261104-125109`，输出 `COMPLETED e10 B`，退出 0。
- 新增测试：`StudentE10B` 的编译失败用例和“构建成功但仍缺声明”用例；镜像内 11 项测试 `OK`，退出 0。
- 动态重检：BuildChecker `status=SUCCEEDED`，`trace_id=e6-0f87743f87134749a079066dcee5bcc1`，仅 REDUNDANT `main.o←unused.h`，无 MISSING。
