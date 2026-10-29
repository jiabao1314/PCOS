# 共享配置与同步验证

核验日期：2026-10-29T17:15:26+01:00（Europe/Paris）。范围：本次共享配置，未重跑历史科研分析。

## 实测结果

- 配置实现提交：`4d1379f24e19fe18bbb792c3f724f8e5d399fb58`（GitHub main）。15个白名单文件逐一读取已提交blob，与本机字节完全一致。原有425文件路径全部保留；未提交已有工作区修改、原始数据或患者资料。
- Drive：10份共享文件及5份配置支持文件，均经metadata确认父目录，再经授权原文件回下载，SHA-256及完整字节与本地一致；未把上传响应当成最终读回。
- 脚本测试：`python3 scripts/test_shared_context.py`，7项通过，退出码0；验证双向更新、冲突前置阻断、删除保护、无基线保护和真实运行三种状态。
- `python3 scripts/shared_context.py pull` 实际运行成功，桌面副本一致，SHA-256同步基线已建立；`plan`实际运行成功。自动记录接口在临时文件上已验证，无真实科研重算。
- 当前状态/日志/下一步/本回执是在首次核验后更新，使用后继文档提交保存；下表记录最终待比对内容的SHA-256，本回执不包含自己的哈希或自己的提交号。发布后最终再次读回的结果在本地运行回执与GitHub提交历史可复核。

## 已核验位置与账号复用

- Drive父目录：[2026PCOS](https://drive.google.com/drive/folders/1Db9GIWdXt9eoCOD9oMgNCmoGkiOcQXey)。共享目录：[00_Shared_Context](https://drive.google.com/drive/folders/1JM3i2CU65MZYyhXnRcpG6i7orlIVaTEI)。未更改分享权限。
- ChatGPT现有PCOS项目ID：`g-p-6add9d6f309081919b26dcc0fa63fe0e`；Codex现有PCOS：`9991e1a1-0a3f-4c6e-99dc-050e879eaaac`。list_projects已确认，无重复创建。
- Drive桌面路径见config/shared_context.json；其PCOS/2026PCOS父目录既有文件与云端列表一致，新建共享目录自动出现在本机。连接器可写且实测回下载一致；gh/rclone未装，未新建OAuth凭证。
- 本地初始main仍为`f17691ea374fec76cabc331d94a0220c06cd94fd`，与远端原有差异和未提交修改保留；仅fetch更新origin/main，没有reset/checkout覆盖工作区。

## 文件读回索引

以下为相同Drive文件ID的原位维护，修改前需读取最新内容。支持文件在Drive共享目录根部按文件名保存；GitHub保留下面仓库路径。

| 仓库路径 | Drive文件ID | SHA-256（本回执除外） |
|---|---|---|
| `00_Shared_Context/PROJECT_OVERVIEW.md` | `1e3BJmldGHSY8uM_KIYP28op_qApIz662` | `0f82f5b2dbfc6534a40f7a30b80e8a4506c752df02d179e584ad0a6b2a9d304c` |
| `00_Shared_Context/PROJECT_STATUS.md` | `1wznV9jWZmTNJXGYdFSvSk_Zl_bzzotmz` | `afda51171f5c1edffb240f3fd51c2c7e8a99cda52dd28e2e6ac8ea498ebfe765` |
| `00_Shared_Context/CHATGPT_HANDOFF.md` | `1cDlh2el6jA9bnGsRWusfuDx-PVZymokX` | `6ccfb28c41bec8633026b65a26a0daef7fe7889ce2bb405d14bc508809f28c3f` |
| `00_Shared_Context/CODEX_RUN_LOG.md` | `15dZ_LPYyOsooT5bFivRPZSUPiOHyIAVg` | `f9048baec8b0c9fe50fb234cdaa3353d9e84bf6f9141f020bbe0920619c8fb49` |
| `00_Shared_Context/DATA_CATALOG.csv` | `1FhvPYllcSMI3iX3bp9xQrlPunTNkk_f0` | `c2bcf20ff4e714c411ab9c27fb6055c3e44013b74cec5a1e8507830e98aabe2f` |
| `00_Shared_Context/RESULTS_INDEX.csv` | `1qO-_x-aVZBlOOVcFieho4MH5XKWgvy7W` | `6878daa56245ec846b20d242b1a721df9d4c1bd0d73b329eece1f4228a8c46e3` |
| `00_Shared_Context/DECISIONS.md` | `1xzP-OMTmwv18prRITfaw3fOqnDBcRwkk` | `7348c98df4cd240c7cdfb0e4f125b972f081b8e2b137c7c5a175adceebd066f1` |
| `00_Shared_Context/NEXT_ACTIONS.md` | `10wdRXs-KbgZJ7sO--U1pEgA-s_oGD0QB` | `ec6be0d9dfb1aa1b3667a3b95cfc67ea872d1e715358c0e4aca283d106b8e905` |
| `00_Shared_Context/CHATGPT_PROJECT_INSTRUCTIONS.txt` | `19USY_KNEXPdjPCxV7YVqcObIGUhZpx1M` | `f64cf3bb975d8c7e68f6af895b58f4cb155f00f3b91eb74295d44af40336503e` |
| `00_Shared_Context/SYNC_CHECK.md` | `1ZBVJOvlCY87Zt7rYLwGMsehPhemqlbLK` | `发布后读回；不自引用` |
| `AGENTS.md` | `1BsHBV_1ebSj59AzKt_n1eM8Nx7Ra2-DM` | `c222aadc696690173ba4c283593bf5a28f651a23367014736981c1f3b6f68e16` |
| `scripts/shared_context.py` | `1_ERvMJuKWjEEeYQw8CuZ8EElo_jLepXk` | `ac46ea66918e6d6f91591490c39373d92fcb8d0c77a756a0eda1760f3160fe15` |
| `scripts/test_shared_context.py` | `1pyrE9b_fxfQZMrpb4OCD2wA8Nf3F_uWq` | `521fa9b2199b0f51259b7fda3eb9029c3e26dc6f122ce5a1df828f7af84d399b` |
| `config/shared_context.json` | `1TECcEeUArvxNaRcfNfh4oL0Ms1nEDxzN` | `66ea42b882f5e4b0d56cb2e290dc9ea64a5ec7e2a42ae1c1ab271ee913b37867` |
| `docs/SHARED_CONTEXT_WORKFLOW.md` | `1wRPBBCWOqIAOILHgPp0pr5B2XAQHy-RN` | `2b89e95742fee7d643592629f00b411da180863ff867edba2870e64f374795fd` |

## 尚未完成与能力边界

- ChatGPT项目设置：已生成CHATGPT_PROJECT_INSTRUCTIONS.txt，尚未加入项目设置；共享Drive文件夹尚未绑定为项目来源。当前连接器没有修改这两项设置的操作，需要用户在既有项目应用并验证读取。
- 完整ChatGPT/Codex聊天历史未同步。共享文档承载已保存交接；当前未请求绕过权限读取私有历史。官方依据：[Projects and chats](https://learn.chatgpt.com/docs/projects)。
- 无人值守完整双云同步未部署。run接口自动维护日志/状态/结果索引/下一步，push只核验Drive桌面字节；每次任务仍由Codex连接器完成Drive/GitHub云端核验。AGENTS已规定此完成条件。
- DATA_CATALOG含72条现有数据清单记录（含4个医院非识别性别名）；RESULTS_INDEX含262条成果记录。这是文件/哈希清单，不代表所有条目已重新统计验证或当前已逐一云端读回。未知生成代码处明确标注，不能猜测。
- 历史修订原始输入清单哈希已核对；历史成果科学QC和云端状态仅引用既有记录。Galaxy完整UN压缩源最后旧记录为running，本轮未访问Galaxy更新其状态，不宣称完成。
- 医院旧回执的pending_clarifications已由用户后续确认解决，见DECISIONS；伦理审批未确认；XX投稿字段保持待用户填写。
