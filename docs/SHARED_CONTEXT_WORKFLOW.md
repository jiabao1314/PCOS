# PCOS 共享资料维护流程

初始化：2026-10-29，Europe/Paris。十份共享资料位于仓库 `00_Shared_Context/`，Drive 文件夹 ID 为 `1JM3i2CU65MZYyhXnRcpG6i7orlIVaTEI`。已有科研原件、日期版本和权限保持原位。旧 `docs/STATUS.md` 是历史模块状态；最新聚焦稿件以共享状态及其证据为准。

## 每次任务开始

1. 用 Drive 连接器列出共享文件夹，并读取最新 PROJECT_STATUS、DECISIONS、NEXT_ACTIONS、CHATGPT_HANDOFF、SYNC_CHECK。确认桌面同步副本与云端内容一致，不能仅依赖本地修改时间。
2. `python3 scripts/shared_context.py pull` 执行基于 SHA-256 基线的合并前检查。双方均改变时立即停止，无基线且内容不同也停止；不得用旧本地副本覆盖 ChatGPT 更新。
3. 查 DATA_CATALOG、RESULTS_INDEX 和日期版本 README，优先复用已有数据、结果与代码。代码基线记录实际提交号及代码 SHA-256；有未提交修改时不能只写提交号。

## 实际分析后自动记录

准备一个本地 JSON 运行规格（置于忽略目录 `.shared_context_runtime/`）。结构示例：

```json
{
  "id": "YYYYMMDD_task_01",
  "task": "具体研究问题",
  "public_metadata_reviewed": true,
  "command": ["python3", "path/to/analysis.py", "--output", "results/dates/new.csv"],
  "inputs": ["path/to/existing_input.csv"],
  "code": ["path/to/analysis.py"],
  "outputs": ["results/dates/new.csv"],
  "verify_commands": [["python3", "path/to/independent_check.py"]],
  "next_actions": "下一步和完成标准",
  "error_resolution": "如有错误，写实际原因和处理；未解决则直说"
}
```

执行 `python3 scripts/shared_context.py run --spec .shared_context_runtime/run.json`。这是执行接口，示例路径不是可直接运行的科研分析。脚本执行真实命令及验证命令，私存 stdout/stderr；自动追加运行日志、状态、结果索引和下一步，输出按新路径保存，检查输入/代码运行前后哈希。缺少验证命令或输出不齐时只能记为 unverified，失败记 failed。具体科研检验及结论仍须审查；脚本不会从退出码推出科研结论。

公开日志不得含患者标识、凭证、敏感文件名或患者级输出。敏感任务不要使用含患者信息的命令参数；输入可引用既有受限档案的非识别性清单。仅将汇总代码/结果纳入公共索引。原始数据和处理数据有变化时同时维护 DATA_CATALOG（名称、来源、路径、版本、哈希、状态、许可）。新下载数据按既有规则存 Galaxy；医院原始资料留在既有私人位置。

## 同步与完成标准

`python3 scripts/shared_context.py push` 仅复制十份文本到已核验的 Drive 桌面目录，保存被替换副本到本地忽略档案，并检查本机字节一致。它明确输出 `cloud_verified: false`。Google Drive 桌面版本身负责后台上传；此脚本未安装定时任务，也不读取全部聊天历史。

`python3 scripts/shared_context.py plan` 给出十份文档及五份支持文件的公开白名单、字节数和 SHA-256。Codex 必须继续执行以下云端步骤：

- Drive 连接器按已知文件 ID 更新原文件，避免创建重复文件；先确认远端内容相对基线未改变。若桌面同步尚未完成，优先连接器写入。逐文件 fetch 读回文本并比对完整 UTF-8 字节；连接器未暴露校验和时记录实际核验方式。
- GitHub 连接器读取最新 main 提交/tree，以该 tree 为 base，只更改白名单路径，create_tree/create_commit 后以 expected_sha 更新 main；不得 force，不得批量暂存整个工作区。必要时用 git fetch 后本地比对新提交中每个 blob 和待发布文件。
- 若要发布新增分析结果，逐项审查许可/隐私并单独列明路径，不能因其出现在索引便自动上传。
- 在 SYNC_CHECK 写实测时间、代码/文档提交、验证范围和未完成项，再同步更新过的共享文件并再次读回。SYNC_CHECK 的内容提交可以由后继回执提交记录，避免自引用提交号/自引用哈希。
- 发布后新取远端 main 不会自动合并本地脏工作树；不 reset/checkout 覆盖用户修改。本次本地旧 main 与远端差异应保留并明确记录。

脚本不直接持有 Google/GitHub OAuth 凭证，也不假装能在独立 shell 调用聊天内的连接器。无人值守完整双云同步未配置；每次 Codex 任务结束通过 AGENTS 强制执行连接器核验。没有验证成功时，报告“分析完成、同步待完成”等准确状态。

## ChatGPT 交接

将共享 `CHATGPT_PROJECT_INSTRUCTIONS.txt` 加入已有 PCOS 项目的项目指令，并将共享 Drive 文件夹接入可读取的来源。当前工具没有修改项目设置或把文件夹添加为项目来源的操作，本次没有宣称已应用。可在 ChatGPT 明确要求读取上述 Drive 文件夹；具备编辑权限时更新 CHATGPT_HANDOFF。缺少编辑能力时返回可保存的交接内容，不能声称已写入。

ChatGPT 和 Codex 交换的是已经保存并核验的研究记录。未保存的讨论、完整聊天、未运行方案均不会因此自动传递。官方说明：[Projects and chats](https://learn.chatgpt.com/docs/projects)。
