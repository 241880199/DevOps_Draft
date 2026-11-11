# ADR：E12 A/B 产物交接

## 问题

现有 `e12` 模式会在同一个编排服务中生成 `incremental-check`，无法证明 B 组真实消费了 A 组独立产生的报告。仅比较同名 Job 或手工复制 findings 也无法证明版本和内容未变化。

## 采用方案

请求新增两个字段：

```json
{
  "incremental_report": "/course/data/.../incremental-check.json",
  "incremental_report_sha256": "<64位SHA256>"
}
```

消费顺序：

1. 路径必须位于 `/course/data`。
2. 读取文件并按请求 SHA256 校验完整内容。
3. 校验 `schema_version=e11e12-1`、`kind=incremental-check`、`status=SUCCEEDED`。
4. 同时校验 envelope commit 与 `data.commit` 等于本次 target。
5. 本地执行 target 全量 BuildChecker，并将对象目标 findings 与 A 报告比较。
6. 在 B 的 `incremental-check.json.provenance` 保存 A 的 job/trace/kind/hash。
7. 只有以上检查通过后才进入 MDFixer。

## 替代方案

- 复制 A 的 findings 到固定 MD：无法证明是 E12 本轮输出。
- 只校验 job_id：job_id 不保证输入和产物内容一致。
- 只校验 SHA256：不能防止 A 报告属于旧 commit 或错误 kind。
- 信任 A 报告而不做本地全量对照：上游图错误可能直接污染 MDFixer 输入。

## 代价与边界

- 外部报告由调用方负责准备到 API 服务器 `/course/data`，这是部署约束。
- 当前 profile 仍只支持 `main.c/helper.c`、显式 Make 和受限 flags。
- 仓库内真实项目是 `fixtures/draft` 的扩展提交，不声明为第三方外部开源项目。
- 跨主机时仍使用 SSH 本地端口转发，不公开 API 端口。

## 验证

- 固定样例五阶段：`job-2eeae68d865a4a3a802eed050059d8ae`。
- A→B 外接：A `job-a76de78f81e5461590eab01cd8c3c162` → B `job-ba1970826b434bba8ad7390fb25e00ac`。
- 仓库内真实 Git 项目：`job-61e9d0fa19e54d3f81d927f9b60b2489`。
- 坏哈希被拒绝：`ARTIFACT_HASH_MISMATCH`。
- 21 项测试全部通过。
