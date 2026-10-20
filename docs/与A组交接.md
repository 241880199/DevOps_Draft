# B→A 平台接口与共享服务器交接（E5 非必需）

更新日期：2026-10-20

交方：B 组 241880199（DRAFT 轨道，`/root/241880199/draft`）

接方：A 组 241880465（BuildChecker 轨道，`/root/241880465/devops`）

## 0. 范围

**E5 本身不要求 A/B 交互。** 按 E5 授课 PPT 和 `05_验收清单.md`，A 组独立完成 BuildChecker 的 trace/Make 声明与 MD/RD 解释，B 组独立完成 DRAFT 的初始失败、候选构建与运行验证；两边各自闭环，B 组 E5 不以 A 组产出为前提。

本文只保留两件事：

1. **B→A 的平台接口契约**：B 的 DRAFT 环境产物以后如何交给 A 的 BuildChecker 消费（属于后续平台集成，不是 E5 验收项）；
2. **同一台云服务器上的资源协调**：目录、镜像标签、Docker 守护进程和网络的使用约定。

本文不包含 A 组 E5 的操作步骤，也不替 A 组做 E5 验收。

## 1. B→A 平台接口契约（后续集成用，非 E5）

### 1.1 B 侧已完成的产物

| 项 | 值 |
|---|---|
| B 仓库 | <https://github.com/241880199/DevOps_Draft> |
| B E5 代码提交 | `1bcf62761e26684367d935f4fab7c0b27126a702`（E5 候选来源） |
| B 当前服务镜像提交 | `47daafe42fe5bd8b7fc214fee56450e02676433a`（CI 修复后） |
| DRAFT 服务镜像 | `course1020-draft:local` = `sha256:1e393cbbce98b48da071c7d74e4b7758fe0852c55ca909d023c23dcf6261eed1` |
| E5 候选镜像 | `course1020-draft-e5:local` = `sha256:0a62ffe30dd2cad37b5c3aac90e16a79b6930702513fb117d28380f7f01d645b` |
| 候选 Dockerfile | `/root/241880199/draft/work/candidate/Dockerfile` |
| 候选 SHA-256 | `d91d585e0ee9476b05101a8477d30dc59a63c6f55c368d177d346d5f2ebab589` |
| 候选构建日志 | `/root/241880199/draft/work/e5-01/candidate-build.log` |
| 运行日志 | `/root/241880199/draft/work/e5-01/verify.log`（内容 `hello E3`） |
| 一致性检查 | `/root/241880199/draft/work/e5-01/verify-evidence.txt`（8/8 PASS） |
| 证据打包 | `/root/241880199/e5-evidence-final.tar.gz`；本机 `D:\Projects\DevOps\E5\work\` |

B 的 E5 结论只用于说明这个环境可用：初始镜像缺 `make`，`RUN make` 以 127 失败；候选安装 `build-essential` 后构建 exit 0；用构建得到的同一镜像 ID 禁网运行，exit 0，stdout 为 `hello E3`。

### 1.2 环境契约字段

字段名可按 A 组现有 Schema 调整，但含义不要丢：

```json
{
  "environment_id": "env-e5-b-20261020-01",
  "producer": "DRAFT / B 组 241880199",
  "source_repo": "https://github.com/241880199/DevOps_Draft",
  "source_commit": "47daafe42fe5bd8b7fc214fee56450e02676433a",
  "e5_source_commit": "1bcf62761e26684367d935f4fab7c0b27126a702",
  "image_ref": "course1020-draft-e5:local",
  "image_id": "sha256:0a62ffe30dd2cad37b5c3aac90e16a79b6930702513fb117d28380f7f01d645b",
  "service_image_id": "sha256:1e393cbbce98b48da071c7d74e4b7758fe0852c55ca909d023c23dcf6261eed1",
  "dockerfile_path": "work/candidate/Dockerfile",
  "dockerfile_sha256": "d91d585e0ee9476b05101a8477d30dc59a63c6f55c368d177d346d5f2ebab589",
  "base_image": "m.daocloud.io/docker.io/library/python@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f",
  "workdir": "/work",
  "build_command": "make",
  "verify_command": "./hello",
  "expected_output": "hello E3",
  "build_exit_code": 0,
  "verify_exit_code": 0,
  "verify_network": "none",
  "artifact_notes": "Single known-answer fixture; not a paper benchmark project."
}
```

### 1.3 A 组如何消费这个环境

```bash
# 只读运行 B 的候选镜像，确认环境可用
docker run --rm --network none \
  sha256:0a62ffe30dd2cad37b5c3aac90e16a79b6930702513fb117d28380f7f01d645b

# 把 A 自己的样例挂进同一个镜像，做 clean build（示例）
docker run --rm --cap-add SYS_PTRACE --network none \
  -v /path/to/a-fixture:/work -w /work \
  sha256:0a62ffe30dd2cad37b5c3aac90e16a79b6930702513fb117d28380f7f01d645b \
  sh -c 'make clean && make'
```

注意：

- `course1020-draft-e5:local` 是**候选程序镜像**，里面是 B 的 `main.c`/`Makefile`/`hello`；`course1020-draft:local` 是 **DRAFT 服务镜像**，两者不要混用。
- B 的候选镜像默认以 root 运行；A 组做自己的检测时应使用自己的样例和独立输出目录，不要把 B 的 `work/` 当成 A 的检测输入。
- 这张契约只描述“B 提供给 A 的环境”，不代表 E5 的跨组验收。

### 1.4 后续平台闭环的 A→B 字段（E6/E7，非 E5）

B 后续的 MDfixer 只消费 **MD**，不消费 RD。到平台集成阶段，A 组可按下表回传；E5 阶段不需要交这些：

| 字段/产物 | 说明 |
|---|---|
| `findings[]` | 每条 `{target, dependency, type: MISSING|REDUNDANT, evidence}` |
| `actual_graph_uri` / `declared_graph_uri` | 若 A 已有图产物，按 ADR-002 用 URI/路径交接 |
| `trace_evidence` | MD 对应的 trace 文件、行号、进程归属 |
| `declared_location` | Make 数据库中的声明行/位置 |
| `detector_version` / `trace_id` | 统一版本与追踪标识 |
| 修复前后对比 | 仅 Makefile 变化、`findings=[]` 的复检结果 |

字段名以 A 组现有 Schema 为准；B 在 E6/E7 记录 DRAFT 的 `image_id`、`candidate_sha256`、`trace_id` 时也按同样方式保留来源。

## 2. 同一台服务器上的协调

| 资源 | B 组 | A 组 | 约定 |
|---|---|---|---|
| 工作目录 | `/root/241880199/draft` | `/root/241880465/devops` | 各自只改自己的目录 |
| 服务镜像标签 | `course1020-draft:local` | `course1020-buildchecker:local` | 不要互相覆盖 |
| E5 候选镜像 | `course1020-draft-e5:local` | A 不需要 | 只读使用 |
| Docker 守护进程 | 共用 | 共用 | **禁止** `docker system prune` / `docker image prune -a` / `docker builder prune` |
| 端口 | B 的 compose 服务 | A 的 compose 服务 | 启动前先 `docker ps` 看端口占用 |
| 网络 | 服务构建用 bridge，程序验证用 `--network none` | 跟踪容器用 `--network none` + `SYS_PTRACE` | 不要开放 2375/2376 |
| 证据 | `work/` 被 gitignore | 同 | 交接用 SFTP/tar，不提交大日志 |

如果 A 组要清理自己的构建缓存，先确认没有其他人在跑构建；只删除自己标签的镜像，不要按时间或 dangling 批量删除。

B 组不会删除 `course1020-draft-e5:local`，供 A 组后续联调只读使用。若镜像不存在，先用本文第 1.1 节的 ID 确认是否在同一台 Docker 守护进程上（`docker images --digests`）。
