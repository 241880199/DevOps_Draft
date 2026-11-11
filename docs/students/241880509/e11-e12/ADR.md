# ADR-011：E11 B 轨道 DRAFT→MDFixer 集成接口决策

编号：ADR-011  
日期：2026-11-11  
作者：顾家谭 / 241880509（B03 组，B 轨道）

## 问题

E11 的 B 轨道要把 E5–E10 已完成的两个组件接成一条链路：

- DRAFT：用候选 Dockerfile 做两轮真实构建（初始失败 → 修复成功），并用构建得到的同一镜像运行验证；
- MDFixer：消费固定 MD 报告，按原声明风格生成 Makefile 补丁，在隔离沙箱中验证，通过后写回并做动态重检。

需要决定：DRAFT 与 MDFixer 以什么边界组合、固定 MD 如何版本化、补丁在什么条件下才允许写回、失败时在哪一步停止，以及 E12 切换为真实报告时哪些接口保持不变。

## 候选方案

1. **进程内组合 + 统一 envelope**（采用）：`pipeline.py` 在同一任务内依次调用 DRAFT 回放与 MDFixer，阶段产物写成带 `schema_version/job_id/trace_id/kind/commit/status/data/artifacts` 的 JSON，下游只从 envelope 读取。
2. DRAFT 与 MDFixer 各自独立服务、通过 HTTP 串行调用：边界清晰，但 E11 的目标是轨道内集成，引入两个服务的部署与网络故障面，超出本阶段验证范围。
3. MDFixer 直接读取 DRAFT 的中间变量/日志：实现最短，但无法保存阶段产物、无法核对 commit 与哈希，也不能复现“报告版本不一致停止修复”的契约。
4. 用真实增量报告替代固定 MD：这是 E12 的目标；E11-B 手册明确要求继续消费固定 MD，提前切换会把 E12 的工作混入 E11 结论。

## 采用方案与原因

采用方案 1，`pipeline.execute()` 在 `mode=e11-b` 中固定以下顺序：

`snapshot(target)` → `auto_build(target, candidate)` → 校验 `fixed-md` envelope → `patch(target, data)` → 写 `candidate.patch` → `validate(target, patch)` → `full_check(target)` 重检。

原因：

- 复用 E8–E10 的 `scan/patch/validate` 与 BuildChecker 的 `full_check`，不复制算法，个人贡献集中在集成、测试和环境适配。
- 阶段 envelope 使每个中间结果都能单独保存、哈希和比对；`check_envelope()` 在消费前统一校验 `schema_version=e11e12-1`、`commit`、`status` 与 `kind`，`STALE_REPORT` 会在生成补丁前终止。
- DRAFT 使用真实 `docker build` 两轮和同一 `image_id` 禁网运行，避免“构建成功但运行输出不对”被误判为成功。
- MDFixer 只在五项检查全通过时把沙箱 Makefile 写回 target 工作副本；任一项失败保留源字节并记录 `checks/error/rollback`。

## 输入输出字段

|阶段|kind|关键输入|关键输出|
|---|---|---|---|
|DRAFT|`draft`|target 项目、候选 Dockerfile、`expected_output`|两轮构建日志、`image_id`、`verification`|
|修复输入|`fixed-md`|固定 MD envelope（commit 必须等于 target）|`data.findings`|
|修复|`repair`|MD `data`、target Makefile|`candidate.patch`、`repair-plan.json`、输入报告 artifact|
|重检|`recheck`|沙箱验证结果、修复后全量图|`validation.json`、`findings[]`、`patched_makefile_sha256`|

所有 artifact 使用 `artifact://<job_id>/<相对路径>`，并同时记录 `sha256` 与 `bytes`；下载端必须重新计算哈希。

## 兼容性与测试

- 保留 E8–E10 的 `labs/e8e10/lab.py` 与 11 项测试不动；E11 新增 `test_student.py` 5 项 B 轨道测试：双 MD 修复且保留 RD、macro/mixed 补丁落点、`STALE_REPORT`、fixed-md envelope commit 校验。
- 原有 `test_contract.py` 10 项继续通过；总计 15 项 `OK`。
- 失败语义：`SCHEMA_MISMATCH`、`STALE_REPORT`、`ARTIFACT_TYPE_MISMATCH`、`ARTIFACT_HASH_MISMATCH`、`DRAFT_FAILED`、`REPAIR_REJECTED`、`OUTPUT_EXISTS` 等在消费前或对应阶段返回；`STALE_REPORT` 的实测见 `evidence/stale-report/`。
- 已知限制：只支持 `main.c/helper.c/config.h` 的显式 C/Make 规则和 `-O0/-O1/-O0 -DMODE=1` flags；DRAFT 使用保存候选回放，不调用模型；E11 的 MD 输入固定为 `fixed-md.json`。

## 后果

- 代价：DRAFT 每轮都真实构建，MDFixer 的 `validate()` 还会复制项目并完整构建一次，运行时间高于只跑构建或只跑补丁。
- 收益：DRAFT 与修复都有独立证据；报告版本不一致时不会生成补丁；补丁只有在补丁可应用、构建、功能测试、头文件变化重编译、动态重检五项全部通过后才写回。
- 迁移到 E12 时，只需把 `fixed-md` 阶段替换为 `incremental-check` 的真实 `data`，`repair/recheck` 的消费逻辑与校验保持不变。
