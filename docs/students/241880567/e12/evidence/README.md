# E12 证据说明

本目录来自 `/root/241880567` 的服务器实际运行，已排除仓库 `data/`、`work/` 中完整镜像层和 Make 原始 trace，仅保留可复核的 JSON、补丁、测试日志、关键构建日志、真实项目 bundle 和源码差异。

|目录|内容|
|---|---|
|`fixed/`|课程生成固定样例五阶段结果|
|`a_source/`|A 组 BuildChecker/EChecker 输出|
|`cross/`|B 组消费 A 报告并保存 provenance|
|`real/`|仓库内真实 Git 项目请求、元数据和结果|
|`api/`|HTTP API 幂等、冲突、边界、下载哈希和重启后查询|
|`tests/`|21 项测试日志|
|`environment/`|A/B 镜像构建日志|
|`source/`|汇总、源仓库 SHA、真实项目 bundle、代码差异|

服务器归档：`/root/devops-submissions/241880567/E12-241880567-20261111.tar.gz`。
