# B 组 → A 组交接文档（E5 阶段）

更新日期：2026-10-20

交方：B 组 241880199（DRAFT 轨道，`/root/241880199/draft`）

接方：A 组 241880465（BuildChecker 轨道，`/root/241880465/devops`）

## 0. 这份文档解决什么

B 组的 DRAFT 产物是 A 组 BuildChecker 的**上游环境**：A 需要一个“能构建项目、能运行程序”的镜像和明确的 clean build / 验证命令，才能在其上做依赖跟踪与 MD/RD 检测。本文给出：

1. B 组 E5 已经产出的、A 组可以直接消费的镜像与证据；
2. 平台闭环所需的字段与路径；
3. 同一台服务器上的资源协调约定；
4. A 组接手 E5 时需要注意的环境适配（与 B 组同源的 Docker Hub / Debian 网络问题）。

A 组自己的 E5 MD/RD 复现仍是 A 组的任务；本文不替 A 组下结论。

## 1. B 组 E5 交付物（已完成，可直接引用）

| 项 | 值 |
|---|---|
| B 仓库 | <https://github.com/241880199/DevOps_Draft> |
| B E5 代码提交 | `1bcf62761e26684367d935f4fab7c0b27126a702`（E5 候选来源） |
| B 当前服务镜像提交 | `47daafe42fe5bd8b7fc214fee56450e02676433a`（CI 修复后，服务镜像 `1e393cbb…`） |
| DRAFT 服务镜像 | `course1020-draft:local` = `sha256:1e393cbbce98b48da071c7d74e4b7758fe0852c55ca909d023c23dcf6261eed1`（CI 修复后；E5 基线为 `d31f…`，`work/build-02`） |
| E5 候选镜像 | `course1020-draft-e5:local` = `sha256:0a62ffe30dd2cad37b5c3aac90e16a79b6930702513fb117d28380f7f01d645b` |
| 候选 Dockerfile | `/root/241880199/draft/work/candidate/Dockerfile` |
| 候选 SHA-256 | `d91d585e0ee9476b05101a8477d30dc59a63c6f55c368d177d346d5f2ebab589` |
| 候选构建日志 | `/root/241880199/draft/work/e5-01/candidate-build.log` |
| 运行日志 | `/root/241880199/draft/work/e5-01/verify.log`（内容 `hello E3`） |
| 一致性检查 | `/root/241880199/draft/work/e5-01/verify-evidence.txt`（8/8 PASS） |
| 证据打包 | `/root/241880199/e5-evidence.tar.gz`；本机 `D:\Projects\DevOps\E5\work\` |

B 组 E5 结论：初始镜像缺 `make`，`RUN make` 以 127 失败；候选安装 `build-essential` 后构建 exit 0；用构建得到的同一镜像 ID 禁网运行，exit 0，stdout 为 `hello E3`。

## 2. A 组可直接消费的环境契约

B 组建议按平台契约的字段交接（字段名可按 A 组现有 Schema 调整，但含义不要丢）：

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

A 组若要在这个环境里跑自己的跟踪，可以：

```bash
# 只读运行 B 的镜像，确认环境可用
docker run --rm --network none \
  sha256:0a62ffe30dd2cad37b5c3aac90e16a79b6930702513fb117d28380f7f01d645b

# 把 A 自己的 md-rd 样例挂进同一个镜像，做 clean build（示例）
docker run --rm --cap-add SYS_PTRACE --network none \
  -v /path/to/a-fixture:/work -w /work \
  sha256:0a62ffe30dd2cad37b5c3aac90e16a79b6930702513fb117d28380f7f01d645b \
  sh -c 'make clean && make'
```

注意：B 的候选镜像默认以 root 运行，`/work` 里是 B 的 `main.c`/`Makefile`/`hello`。A 组做 MD/RD 跟踪时应使用自己的样例和独立输出目录，不要把 B 的 `work/` 当成 A 的检测输入。

## 3. A 组接手 E5 的操作提示

A 组当前仓库是 `/root/241880465/devops`（远程 `https://github.com/241880199/DevOps.git`，2026-10-20 观察 HEAD 为 `0e138b5`），仍是 E2/E3/E4 内容，**没有** E5 学生包的 `labs/A-buildchecker`。A 组需要先把学生包的 A 轨道代码覆盖进来，做法与 B 组相同：

1. 从 `DevOps_1020_Student_Cloud/labs/A-buildchecker` 取文件（排除 `.git`、`work`、`.env`），覆盖到 A 仓库根目录；
2. 按本组网络做与 B 同源的适配：
   - `services/buildchecker/Dockerfile` 的 `ARG BASE_IMAGE` / `ARG DOCKER_CLI_IMAGE` 改为 `m.daocloud.io/docker.io/library/...`，**digest 保持** `f82c9645…` / `9190b061…`；
   - 若 Dockerfile 首行有 `# syntax=docker/dockerfile:1`，删除（本组 ECS 解析该前端会超时）；
   - 预拉取 `python@sha256:70729b46…`、`python@sha256:f82c9645…`、`docker@sha256:9190b061…`；
3. 构建服务镜像并跑单测：

   ```bash
   cd /root/241880465/devops
   python3 scripts/lab_cloud.py build --out work/build-01 --build-timeout 1200
   ```

   预期 A 服务测试通过（教师参考记录为 15 项）；
4. **E7 前补齐 `ci/`**：把学生包 `ci/A-main-protection.json`、`ci/rejection-demo/A/test_ci_reject_demo.py`、`ci/rejection-demo/A/fixed/test_ci_reject_demo.py` 复制到 A 仓库根目录的 `ci/` 下；文档 04 里的 `../../ci/...` 在 A 仓库根目录应改为 `ci/...`；
5. 采集 E5：

   ```bash
   python3 scripts/lab_cloud.py e5 --out work/e5-01 --build-timeout 600
   cat work/e5-01/evidence/program-output.txt
   grep -n '^main.o:' work/e5-01/evidence/make-db.txt
   grep -n 'config.h' work/e5-01/evidence/trace/t.*
   ```

   预期：`program-output.txt` 为 `1`；`make-db.txt` 中 `main.o: main.c unused.h`；`trace/t.*` 中能看到 `config.h` 的读取；结论 **MD = config.h，RD = unused.h**。`lab_cloud.py e5` 使用 `--cap-add SYS_PTRACE`，否则 strace 会报 `Operation not permitted`。

A 组如果选择在 B 的镜像里跟踪，需要注意 B 的镜像是 Debian trixie、含 gcc/make；A 的 `md-rd` 样例本身只有 `main.c`、`config.h`、`unused.h`、`Makefile`，直接挂载即可。但 A 的 E5 证据应保存在 A 自己的仓库 `work/`，不要写进 B 的 `work/`。

## 4. 同一台服务器上的协调

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

## 5. A → B 的回传（平台闭环，E5 阶段为 PENDING）

B 的后续 MDfixer 只消费 **MD**，不消费 RD。A 组完成 E5/E6 后，建议回传：

| 字段/产物 | 说明 |
|---|---|
| `findings[]` | 每条 `{target, dependency, type: MISSING|REDUNDANT, evidence}` |
| `actual_graph_uri` / `declared_graph_uri` | 若 A 已有图产物，按 ADR-002 用 URI/路径交接 |
| `trace_evidence` | MD 对应的 trace 文件、行号、进程归属 |
| `declared_location` | Make 数据库中的声明行/位置 |
| `detector_version` / `trace_id` | 统一版本与追踪标识 |
| 修复前后对比 | 仅 Makefile 变化、`findings=[]` 的复检结果 |

E5 阶段 A 组只需先完成 MD/RD 的手工解释；上述结构化字段可在 E6 回传。B 组在 E6/E7 阶段会把 DRAFT 的 `image_id`、`candidate_sha256`、`trace_id` 按同样方式记录，双方字段名以 A 组现有 Schema 为准。

## 6. 验收对照

| 项 | B 组（本交接） | A 组（待完成） |
|---|---|---|
| 初始/原始样例 | `make: not found`，build exit 1 | clean build 成功；MD `main.o→config.h`，RD `main.o→unused.h` |
| 候选/修复 | 候选构建 exit 0，同一镜像运行输出 `hello E3` | 仅 Makefile 变化，`findings=[]` |
| 证据 | `work/e5-01/`、`work/candidate/` | A 自己的 `work/e5-01/evidence/` |
| 状态 | **PASS（E5）** | **PENDING** |

## 7. 交接检查

A 组接手后先确认：

```bash
cd /root/241880465/devops
git status --short
git log --oneline -2
ls scripts/lab_cloud.py services/buildchecker 2>/dev/null
docker image inspect course1020-draft-e5:local --format '{{.Id}}' 2>/dev/null || true
```

若 `scripts/lab_cloud.py` 不存在，说明还没有覆盖 E5 学生包；若 B 的候选镜像不存在，先用第 1 节的镜像 ID 确认是否在同一台 Docker 守护进程上（`docker images --digests`）。B 组不删除该镜像，供 A 组联调使用。
