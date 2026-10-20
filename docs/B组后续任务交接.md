# B 组（DRAFT）E5 → E6/E7 交接文档

更新日期：2026-10-20

交接人：241880199（B 轨道）

接收人：241880567 及后续 B 组成员

## 0. 一句话状态

**E5 已完成并通过本地一致性检查；E6、E7、GitHub CI 均未开始。** 服务器上的仓库已经包含 E5/E6/E7 全部 B-draft 代码，E6/E7 只需按本文命令继续执行，不需要重新搭环境。

## 1. 服务器、仓库与镜像

| 项 | 值 |
|---|---|
| 云主机 | `121.40.121.129`（root，Ubuntu 22.04.5 LTS，x86_64） |
| 工作目录 | `/root/241880199/draft` |
| 仓库 | <https://github.com/241880199/DevOps_Draft> |
| 分支 | `main` |
| E5 代码提交 | `1bcf62761e26684367d935f4fab7c0b27126a702`（提交说明：`E5: update B-draft lab and pin mirror image sources`） |
| 报告/证据提交 | 紧随其后的 `docs` 提交；最终 HEAD 以 `git rev-parse HEAD` 为准 |
| GitHub 远程 HEAD | 2026-10-20 已推送；以 `git ls-remote origin HEAD` 为准（E5 代码提交 `1bcf627`） |
| 服务镜像 | `course1020-draft:local` = `sha256:d31f3887293d24b89c57b0f91772a309e4d00f09c2d4d0baf4319f233fddfe08` |
| E5 候选镜像 | `course1020-draft-e5:local` = `sha256:0a62ffe30dd2cad37b5c3aac90e16a79b6930702513fb117d28380f7f01d645b` |
| Docker | 29.1.3（客户端与服务端） |
| 服务镜像内 Python | 3.13.14 |

注意：`/root/241880567/draft` 还是 E4 的 `8fbd6f8`。**先不要直接在该目录继续**；当前 `main`（`1bcf627` + 报告/证据提交）已经推到 GitHub，在 241880567 的克隆里 `git pull --ff-only`，或者直接从 `/root/241880199/draft` 复制一份新克隆。不要覆盖对方未提交的文件。

`work/` 在 `.gitignore` 中；E5 证据已按 `.gitignore` 的说明用 `git add -f` 纳入 `docs` 提交，服务器另有 `/root/241880199/e5-evidence.tar.gz`，本机备份在 `D:\Projects\DevOps\E5\work\`。

## 2. E5 产物索引（接手前先核对）

| 文件 | 证明什么 |
|---|---|
| `work/e5-01/iter-01/Dockerfile` | 初始失败 Dockerfile，固定 `FROM ...python@sha256:70729b46…` |
| `work/e5-01/iter-01/build-retry.log` | 真实失败日志：`/bin/sh: 1: make: not found`，镜像内 127，`docker build` 退出 1 |
| `work/e5-01/iter-01/result-retry.json` | `{"build_exit_code": 1}` |
| `work/e5-01/iter-01/error-localization.json` | 关键词命中与根因行，来自真实日志 |
| `work/e5-01/iter-01/prompt-error-driven.txt` | 错误驱动提示全文 |
| `work/e5-01/iter-01/prompt-context-driven.txt` | 上下文驱动提示全文 |
| `work/candidate/model-response-*.txt` | 4 个候选的原始回复 |
| `work/candidate/candidate-0*.Dockerfile` | 4 个候选正文 |
| `work/candidate/decision.json` | R1–R4 选择记录：候选 1、3 归一化后相同，选 1 |
| `work/candidate/provenance.json` | 模型、日期、原始回复路径、人工修改、构建验证结果 |
| `work/candidate/Dockerfile` | 最终候选；SHA-256 `d91d585e0ee9476b05101a8477d30dc59a63c6f55c368d177d346d5f2ebab589` |
| `work/e5-01/candidate-build.log` | 候选真实构建，退出 0，`cc main.c -o hello` |
| `work/e5-01/image-id.txt` | 构建得到的镜像 ID `sha256:0a62ffe3…` |
| `work/e5-01/verify.log` | 同一镜像禁网运行，输出 `hello E3`，退出 0 |
| `work/e5-01/verify-evidence.txt` | 8 项交叉检查全部 PASS |
| `work/e5-01/summary.json` | 基线、候选、验证、环境说明汇总 |

快速复核（在仓库根目录）：

```bash
cd /root/241880199/draft
python3 - <<'PY'
import json, hashlib
from pathlib import Path
print(json.load(open('work/e5-01/iter-01/result-retry.json')))
print(json.load(open('work/e5-01/iter-02/result.json')))
print(json.load(open('work/e5-01/iter-02/verify-result.json')))
print((Path('work/e5-01/verify.log')).read_text())
print(hashlib.sha256(Path('work/candidate/Dockerfile').read_bytes()).hexdigest())
PY
```

预期输出依次为 `{'build_exit_code': 1}`、`{'build_exit_code': 0}`、`{'verify_exit_code': 0}`、`hello E3`、`d91d585e…`。

## 3. 已做的环境适配（不要盲目回退）

本组 ECS 直连 Docker Hub 和 `deb.debian.org` 很慢，E5 做了三处适配，均已在报告“故障与限制”中记录：

1. **镜像站**：`services/draft/Dockerfile` 的 `BASE_IMAGE`、`DOCKER_CLI_IMAGE` 和 `fixtures/ci-candidates/DeepSeek-E5.Dockerfile` 的 `FROM` 改为 `m.daocloud.io/docker.io/library/...`，但 **digest 未变**：
   - Python 服务镜像：`sha256:f82c96458eedc847b233e582eb31336f4954b39cae020b6dcf5b3ed0e5cbcd74`
   - Docker CLI：`sha256:9190b0613792e658a7783cf14b2d5ace5941bb68ede7276922ea36ee457d76ad`
   - E5 候选基础镜像：`sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f`
2. **删除 syntax 前端**：`services/draft/Dockerfile` 首行 `# syntax=docker/dockerfile:1` 已删除；BuildKit 解析该前端时会访问 Docker Hub 并超时，本次 Dockerfile 不需要它。
3. **候选的 Debian 镜像重写**：最终候选在 `apt-get update` 前有一行
   ```dockerfile
   RUN sed -i 's|http://deb.debian.org|http://mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources
   ```
   这是人工加入的网络适配，已写入 `provenance.json` 的 `manual_changes`。它不改变固定 `FROM`、项目文件、`RUN make` 和 `CMD`。

如果之后网络恢复，可以把镜像站换回官方路径，但必须保持 digest 不变，并重新跑一遍 E5 的两轮构建和运行验证；不要只改文件不重跑。

## 4. E6 接手步骤

### 4.1 用自己的候选（推荐）

```bash
cd /root/241880199/draft
python3 scripts/lab_cloud.py e6 --candidate work/candidate/Dockerfile \
  --out work/e6-own --build-timeout 600
echo "AUTO_BUILD_EXIT_CODE=$?"
python3 scripts/verify_e6_b_evidence.py --run-dir work/e6-own/evidence
```

预期：

- 第一轮初始构建必须是真实 `MISSING_MAKE`（`build_exit_code=1`，日志含 `make: not found`）；
- 第二轮候选构建 `build_exit_code=0`；
- 保存 `image_id`，并用**同一个 image ID** 禁网运行；
- 程序退出码 0，stdout 为 `hello E3`；
- `verify_e6_b_evidence.py` 输出 `passed: true`，并给出 `trace_id`、`candidate_sha256`、`image_id`。

### 4.2 用包内候选回放（备选）

```bash
python3 scripts/lab_cloud.py e6 --replay \
  --out work/e6-replay --build-timeout 600
echo "REPLAY_EXIT_CODE=$?"
python3 scripts/verify_e6_b_evidence.py --run-dir work/e6-replay/evidence
```

回放时必须在报告和 `provenance.json` 中写 `is_recorded_replay=true`，并注明来源是 `fixtures/ci-candidates/DeepSeek-E5.Dockerfile`。不要把回放说成“本次新生成的模型回复”。

### 4.3 E6 注意事项

- 候选必须保留 `RUN make` 和 `CMD ["./hello"]`；E7 的故障注入依赖这两行。
- `lab_cloud.py e6` 每次使用新的 `--out` 目录；已有目录非空会被拒绝。
- 服务镜像代码改动后，先用 `python3 scripts/lab_cloud.py build --out work/build-03 --build-timeout 1200` 重新构建并跑单测（当前基线 24 passed）。
- 构建服务容器使用 `--network bridge` 访问注册表；最终程序验证仍用 `--network none`。不要把两者混为一谈。

## 5. E7 接手步骤

### 5.1 本地门禁

```bash
cd /root/241880199/draft
python3 scripts/lab_cloud.py gate --candidate work/candidate/Dockerfile \
  --out work/e7-01 --build-timeout 600
echo "E7_GATE_EXIT_CODE=$?"
cat work/e7-01/gate/gate-result.json
```

预期：`E7_GATE_EXIT_CODE=0`；服务单元测试通过；五个场景 `success`、`wrong-output`、`invalid-candidate`、`build-failed`、`runtime-timeout` 全部 `passed=true`；`runtime-timeout` 的 `verify-container-id.txt` 对应容器已被清理（`docker container inspect` 返回 no such）。

参考记录：教师试跑中 E6 为 13 项服务测试，E7 扩为 24 项，加入并修复门禁测试后为 25 项。以本次实际日志为准。

### 5.2 补充一项测试

按验收清单“自己补充的一项测试”要求：

1. 在 `services/draft/tests/` 新增一个针对真实行为的测试（例如候选约束校验、输出匹配、超时状态或清理逻辑）；
2. 重新构建服务镜像 `python3 scripts/lab_cloud.py build --out work/build-03 --build-timeout 1200`；
3. 重跑 `lab_cloud.py gate`，确认测试数增加且门禁仍为 0；
4. 在报告“E7”和“自主扩展测试”中写清测试检查了什么、修改了哪些文件、运行结果。

### 5.3 GitHub CI 与合并门禁

服务器当前没有 `gh`。两种做法：

- 在服务器安装：`sudo apt-get update && sudo apt-get install -y gh`，然后按学生包 `docs/04_GitHub_CI与合并门禁.md` 执行；
- 或者在本机用 `gh` 操作 GitHub，服务器只负责代码和 `work/` 证据；推送前先确认远程仓库和分支。

**E7 前置：补齐 `ci/` 与 `templates/`。** 本仓库根目录是 B-draft 本身，没有学生包里的 `labs/B-draft` 这一层；学生包的 `ci/` 和 `templates/` 目前**不在**仓库里。开始 CI 前，从 `DevOps_1020_Student_Cloud/` 复制以下最小集合到仓库根目录：

```bash
# 在学生包解压目录执行，目标路径按本组仓库位置调整
mkdir -p /root/241880199/draft/ci/rejection-demo/B/fixed /root/241880199/draft/templates
cp ci/B-main-protection.json /root/241880199/draft/ci/
cp ci/rejection-demo/B/test_ci_reject_demo.py /root/241880199/draft/ci/rejection-demo/B/
cp ci/rejection-demo/B/fixed/test_ci_reject_demo.py /root/241880199/draft/ci/rejection-demo/B/fixed/
cp templates/实验报告.md templates/候选来源记录.json templates/验收记录.csv /root/241880199/draft/templates/
```

复制后，文档 04 里所有 `../../ci/...` 路径在本仓库应改为 `ci/...`（例如 `cp ci/rejection-demo/B/test_ci_reject_demo.py services/draft/tests/`）。`ci/A-*` 与 A 组文件不需要复制到 B 仓库。

必须完成的闭环：

1. 正常 push 触发 `e7-b-quality-gate`，保存 run URL 和 artifact；
2. 配置 main 分支保护：必需检查 `e7-b-quality-gate`、App ID `15368`、`strict=true`、`enforce_admins=true`、通过 PR 合并、审批 0；
3. 创建故意失败的 PR（`ci/rejection-demo/B/test_ci_reject_demo.py`），确认 `OPEN / BLOCKED`，普通 `gh pr merge` 退出码 1；
4. 换成 `ci/rejection-demo/B/fixed/test_ci_reject_demo.py`，确认最新提交检查通过、PR 合并成功；
5. 下载失败和恢复两次的 artifact、保护配置、拒绝合并日志、最终合并记录，放到 `work/ci-rejection/`、`work/ci-recovery/`。

注意：如果服务器上 `gh auth login` 无法打开浏览器，按文档在电脑浏览器打开 <https://github.com/login/device> 输入验证码；不要把 Token 写进仓库、日志或镜像。

## 6. 未完成项清单

- [ ] E6：两轮构建与同镜像运行验证（`work/e6-own`）
- [ ] E6：`verify_e6_b_evidence.py` 通过
- [ ] E7：五场景门禁（`work/e7-01`）
- [ ] E7：超时容器清理证据
- [ ] 自己补充的一项测试 + 重新构建 + 重跑门禁
- [ ] CI 正常、失败、恢复三次运行及 artifact
- [ ] main 分支保护、拒绝合并日志、最终合并记录
- [ ] 填写报告 E6/E7/CI 三节和 `docs/验收记录.csv` 的 PENDING 项
- [x] 当前 `main` 已推送到 GitHub（2026-10-20；远程 HEAD 以 `git ls-remote origin HEAD` 为准）

## 7. 共享服务器注意事项

- 同一台服务器还有 A 组（`/root/241880465/devops`）和 B 组另一名成员（`/root/241880567/draft`）。不要执行 `docker system prune`、`docker image prune -a`、`docker builder prune` 等会删除他人镜像/缓存的命令。
- B 组镜像标签：`course1020-draft:local`（服务）、`course1020-draft-e5:local`（E5 候选）。A 组使用自己的 `course1020-buildchecker:local`，不要互相覆盖。
- 只构建课程指定项目；不要开放 Docker API 2375/2376；不要清理其他组员的容器。
- `work/` 默认被 Git 忽略；本次 E5 证据已 force-add 到 `docs` 提交。后续 E6/E7 不要无条件 `git add -f` 整个 `work/`，按验收需要挑选小文件，避免带入大日志和可能的敏感信息。
- 如果重新登录 SSH，Shell 变量（`repo`、`pr_num` 等）会丢失，按文档重新读取。

## 8. 交接验收（接手人第一步）

```bash
cd /root/241880199/draft
git status --short                 # 应为空
git log --oneline -2               # 应看到 1bcf627 及其后的报告/证据提交
python3 scripts/lab_cloud.py --help
ls work/e5-01/verify-evidence.txt work/candidate/Dockerfile
cat work/e5-01/verify-evidence.txt # 8/8 PASS
```

以上全部符合后，再开始 E6。若 `git status` 不干净，先查清是谁的改动，不要直接 `reset`。
