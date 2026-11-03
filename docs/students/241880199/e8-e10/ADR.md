# 决策记录

## 背景与约束

E8 B 组要在固定样例上独立验证“报告身份 → 候选 Patch”这一步，不能等待 A 组在线服务。样例的 `main.c` 包含 `config.h`，而 `Makefile` 的 `main.o` 只声明 `main.c unused.h`；因此构建仍能成功，但头文件变化不会触发重编译。约束是只修 MISSING，保留 REDUNDANT 观测和原有编译配方，并且拒绝身份不匹配的旧报告。

## 选择与替代方案

- 选择：使用本次生成的固定 MD 报告；只对 `main.o` 的显式依赖行做 `direct` 风格补丁；生成后用 `git apply --check` 检查，但不写回源文件；报告身份用样例内部 Git commit 做前置校验。
- 替代方案一：直接手改 Makefile。拒绝，因为无法证明“报告版本/身份”与“候选 Patch”分离，也绕过了课堂要求的拒绝用例。
- 替代方案二：顺手删除 REDUNDANT 的 `unused.h`。拒绝，因为本实验只处理 MISSING，删除会扩大变更面，且会改变 REDUNDANT 的观测结果。
- 替代方案三：等 A 组 BuildChecker 在线产出。E8 不采用；固定报告是课堂输入，跨组在线对接放到后续集成。

## 代价与覆盖范围

- 固定报告不是跨组真实服务交互，只能证明 B 侧消费与修复逻辑。
- 只覆盖 `direct` 声明风格与 `gcc -MM` 的局部头文件依赖；`macro`/`mixed` 风格留到 E9 B。
- E8 不做构建、测试和动态重检（留给 E10），因此本阶段的结论仅到“Patch 可应用、源文件未变、旧报告被拒绝”。

## 验证命令与实际证据

- 手工分步路线 OUT：`work/e8-B-manual.dK1wtN`。
- 固定报告 commit：`fc5ee2a028b533d1a2166605386a56542e186627`；`COMMIT_MATCH`。
- Patch：`candidate.patch` 只增加 `config.h`；`PATCH_GENERATED_SOURCE_UNCHANGED`；`APPLY_CHECK_PASS_SOURCE_CLEAN`。
- 旧报告：`STALE_REPORT`；`SOURCE_BYTES_UNCHANGED`。
- 新增测试后复验：`work/e8-B-postchange-20261103-194501`，`COMPLETED e8 B`；单元测试 `Ran 8 tests ... OK`（`work/unit-tests-20261103-194500.log`）。
