# E9 B 组决策记录

## 背景与约束

E9 B 需要把同一个 MISSING `main.o←config.h` 分别投影到直接枚举、纯变量和混合声明三种 Make 写法。修复器只能增加缺失声明，必须保留 REDUNDANT 观测和原编译配方，并保证生成 Patch 时不修改输入 Makefile。

自主任务选择重复 MISSING 去重。上游报告可能由于图归并或适配器边界重复输出同一条 `(target, dependency)`；若逐条追加，会生成重复依赖并产生失真的修改计划。

## 选择与替代方案

- 选择：在 `patch()` 内维护 `(target, dependency)` 集合。第一次遇到 MISSING 时执行原声明风格判断和修改，后续完全相同的发现直接跳过。
- 替代方案一：在报告入口统一对 `findings` 做 set 转换。会改变报告顺序并影响 `findings` 中不同类型及目标交错的处理顺序，范围过大。
- 替代方案二：按 dependency 全局去重。不同目标可能都需要声明同头文件，全局去重会漏边。
- 替代方案三：只在 diff 文本上删除重复追加。生成 Patch 后才去重已经执行了无效修改，计划与 Edit 列表仍可能重复。

## 代价与覆盖范围

- 基于 `(target, dependency)` 去重不会合并不同目标上的相同依赖，符合构建图语义。
- 当前只处理完全相同 MISSING 的重复；若两个不同目标共享同一纯变量，首目标修改变量后会影响其他目标，仍需跨目标影响分析，不能在当前教学范围内自动保证最小修改。
- 修复仍是保守的追加策略，不处理删除 REDUNDANT、隐式规则、条件分支和更复杂的 Make 表达式。

## 验证命令与实际证据

- 手工样例：`work/e9-B-manual.XzsO0N`，direct/macro/mixed 三组均输出 `STYLE_PASS`，macro 副本输出 `APPLY_TO_COPY_PASS`。
- 修改后复验：`python3 run_lab.py e9 --track B --out work/e9-B-postchange-20261103-213027`，输出 `COMPLETED e9 B`。
- 定向测试：`python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v`，9 项 `OK`，退出码 0。
- 关键保存文件：`direct.patch`、`macro.patch`、`mixed.patch`、三份 `*-plan.json` 及 `evidence/unit-tests-20261103-212936.log`。
