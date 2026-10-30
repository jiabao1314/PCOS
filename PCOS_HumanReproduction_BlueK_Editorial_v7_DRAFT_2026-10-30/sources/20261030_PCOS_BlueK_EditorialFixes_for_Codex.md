# Codex 执行任务：PCOS 老师 Blue K 已修改稿的有限技术修正

**日期**：2026-10-30（Europe/Paris）  
**任务性质**：已授权的定向文字/引文/披露修订；不是重新设计研究、重新做统计或投稿  
**状态**：`authorized_to_edit / not_yet_executed`；完成前不得写为 `verified`  
**优先级**：P0：先保证蓝字修改完整继承；P1：9项小幅修正；P2：新稿核验与共享

## 0. 首先理解这项任务（严格遵守）

1. 老师的 **《PCOS 20261030 Blue K.pdf》19页是已完成的修订稿**；第1页明确标注“blue text marks additions or replacements”。蓝色不是待办提示，**不得整体撤回、删除或重新设计老师修改**。蓝字出现在第1—13页；程序可检测约171个蓝色文本span，但这不是171项独立待办。
2. **以 Blue K PDF 的正文内容为新工作稿的内容基线**。`Human Reproduction v6 / Overleaf r1` 为旧的已接受科学/排版基线，只能用来寻找可编辑源、比对并恢复真实遗漏，**不能直接以旧v6为成稿，导致Blue K中的新增内容丢失**。
3. 本次仅修正下列9项可定位问题，保留老师其余蓝字修改及所有科学数值。不得自行扩大到重下GBD、改变估计目标、改权重、重构图表、加入预测模型或医院/NSFG分析。
4. **不投稿、不外发邮件、不覆盖/删除旧稿**。全部新文件使用20261030日期前缀，另建独立 `PCOS_HumanReproduction_BlueK_Editorial_v7_DRAFT_2026-10-30/`；“v7_DRAFT”仅表示候选新稿，不能称为作者已接受/已投稿。

## 1. 真实来源与开始前必读

- 随同本执行文件提供的 `PCOS 20261030 Blue K.pdf`（真实19页；蓝字1—13页）。**这份PDF随附在执行ZIP中**；不要假设仅凭ChatGPT历史就能在Codex文件系统读到。先检查是否已在Codex工作目录/Drive的本次稿件文件夹；若没有，直接使用随附PDF。
- 现有v6/Overleaf r1（用于提取编辑源和精确比较）：`https://drive.google.com/drive/folders/1T02U_BMnBNQm1sCvBo7GE4P0vBMMNq32`；实际文件名 `20261030_PCOS_HumanReproduction_v6_Overleaf_r1_Manuscript.tex`、`20261030_PCOS_HumanReproduction_v6_Overleaf_r1_Supplement.tex`。版本别名请以真实manifest为准，不自拟路径。
- 既有v6交付目录：`https://drive.google.com/drive/folders/1X-9Gsv8TAp2HVR7hdPhg9Y4TiTEPg9pf`。研究快照 Git commit `1abf337d9f23cc69292e03cd581b6a1557e6effe`。
- 首先使用Google Drive连接读取共享目录 `https://drive.google.com/drive/folders/1JM3i2CU65MZYyhXnRcpG6i7orlIVaTEI` 的 **最新** `PROJECT_STATUS.md`、`DECISIONS.md`、`NEXT_ACTIONS.md`、`CHATGPT_HANDOFF.md`、`SYNC_CHECK.md`，再按需读取 `RESULTS_INDEX.csv`、`DATA_CATALOG.csv`、`CODEX_RUN_LOG.md`。本任务编制时最近的共享状态为2026-10-30 **19:36巴黎时间**（Galaxy数据归档完成），但实际运行时须再读最新版本，禁止依据本段当作永远最新。
- GitHub: `https://github.com/jiabao1314/PCOS/tree/main/00_Shared_Context`；Overleaf: `https://www.overleaf.com/project/6adda2876e26d2e60e482e89`。如有同时修改，先合并再写回，保留历史。

## 2. 必须先解决“PDF与可编辑原稿”的对应

- 在 Drive/GitHub/已有工作目录中查找老师这份**蓝字版**的可编辑 `.tex/.docx`。若存在，逐段与PDF核对后再用。
- 若蓝字版只有PDF，则从PDF可提取文字层获取完整19页文本，将Blue K相对于v6的**全部**新增/替换内容合入旧的可编辑v6 TeX；不能只对v6应用下列9处补丁就说已采用老师的稿。
- 建立 `BlueK_vs_v6_crosswalk.csv`：页码、段落定位、Blue K原文、v6对应原文、状态（Blue K已合入/原稿一致/待处理）、说明。蓝字可按语义块归并，不要求一span一行；核验摘要、方法、结果、讨论、表格、参考文献及页末图说明无遗漏。
- 以PDF页码和英文字串定位，不依赖页码在新LaTeX中保持不变。源PDF标蓝是审阅痕迹，不等于期刊正式提交格式。

## 3. 定向修正（不要再改老师已经合理的其他段落）

### FIX-01 [P1] 第3页：明确“绝对差距缩小”，而非有符号差值变小

**查找完整句**：
`Consequently, a smaller national-versus-pool difference need not reflect a decline in the national rate.`

**建议替换为**：
`Consequently, a smaller absolute gap between the national and pooled-reference rates need not reflect a decline in the national rate.`

**原因**：本稿定义 `D=China−reference`；1990年D=−272.92，2023年D=−121.38。有符号D是增大+151.54，绝对差距才缩小。不得把“absolute gap”误改成“中国发病下降”。

### FIX-02 [P1] 第1页摘要 STUDY QUESTION：主问题应问“1990—2023率差变化”

**现有句**：
`How did changing reference-country population shares contribute to China’s PCOS-attributed infertility rate difference from an 18-country pool during 1990–2023?`

**建议替换为**：
`How did changing within-age reference-country population shares contribute to the 1990–2023 change in China's age-standardized PCOS-attributed total-infertility rate difference from an 18-country pooled reference?`

将排印中的直撇号换为模板适用的弯撇号；保持 `China-minus-reference` 的方向，主分析是 total infertility、当年份额。检查标题/摘要/方法/结论目标一致。摘要其他11个栏目及核心数值不变；**不要虚构摘要字数上限**，按实际目标刊现行指南核对（若访问受限注明未验证）。

### FIX-03 [P1] 第10页：“net-change components”术语不严谨

**现有句**：
`The share and net-change components were close under this population-source substitution.`

**建议替换为**：
`The reference-share components and total changes were similar under the two population sources.`

原因：净变化是各分量之和，不是与share并列的独立“component”。保留后面“UN替换只能检验人口权重、不能独立验证GBD疾病率”的句子。

### FIX-04 [P1] 第12页 Acknowledgements：恢复原v6中已有、可核实的AI版本信息

Blue K删掉了原v6已记录的这项事实：**2026-10-29 Codex运行记录 `gpt-6.1-sol`**。请读取 `AI_VERSION_EVIDENCE.json` / 原v6声明及真实运行日志，恢复这一项**限定于对应会话**的版本与日期，保留ChatGPT/Codex在代码、校核、起草、技术编辑方面的真实用途、作者核查责任。

若当前日志证实只有2026-10-29这一次版本，不得把 `gpt-6.1-sol` 说成所有工作/所有会话均使用的版本；其余无法核实的版本明确写“not independently verified”。不要虚构模型版本、作者逐项签字、最终已批准事实；作者/经费/伦理等XX仍保留。研究使用AI并非作者身份；按目标刊现行政策核查 Methods、Acknowledgements、cover letter三处是否一致。

可采用的**候选英文补句**（须先核实日志并根据上下文整合，不能盲目粘贴）：
`The documented Codex session on 29 October 2026 recorded the model identifier gpt-6.1-sol; model identifiers for other sessions were not independently verified. The human authors checked the scientific content and remain responsible for the manuscript.`

对于其中“checked”若作者尚未实际确认，则改为未来待核实说明，不可冒称已核验。

### FIX-05 [P1] 第14页参考文献：Xu et al. 2025游离引用

参考文献有：`Xu Y ... J Evid Based Med. 2025;18:e70100. doi:10.1111/jebm.70100.`；原v6有文内引用，但Blue K改写后不再引用。

在正文中核对其真实相关性后：① 有合适的已保留GBD疾病负担背景句则恢复 `(Xu et al., 2025)`，**不添加未经原文支持的新主张**；或② 若不再使用则删除参考文献列表中该条。全文执行文内引文↔文后文献双向校验，禁止删掉其它真实引用或重排出不一致的作者年份。

### FIX-06 [P1] 第13页 Supplementary data：区分公开与私人复现包

**现有**：
`The reproducibility archive contains code, aggregate results, source specifications, a complete annual subtype CSV and execution instructions; licensed GBD originals and restricted source cells are excluded.`

**建议替换为**：
`The public reproducibility repository contains code, aggregate derived results, source specifications, a complete annual subtype CSV and execution instructions; licensed GBD originals and restricted country–age source cells are excluded.`

第13页 Data availability 本来已明确private archive，保持一致。老师复现的 `FULL_PRIVATE` 包实际含经许可的原始输入，不可误说“私人包也排除原件”；若需说明其权限，只说保存在非公开位置、以真实manifest为准。不得将许可GBD原件、国家年龄源单元、医院原件或私有访问链接写入GitHub。

### FIX-07 [P2] 第11页：明确Yang研究是2020年调查

**现有**：
`Yang and colleagues’ Chinese community survey used Rotterdam PCOS ascertainment among married Han women aged 20–49 ...`

**建议**：
`In the 2020 Chinese community survey, Yang and colleagues used Rotterdam PCOS ascertainment among married Han women aged 20–49 ...`

保留原有 `(Yang et al., 2022)` 引文及全文对本项目的分母差异讨论。依据该研究2020组年龄20–49，不能把2010组年龄范围错套成同一个范围；如果核实原文差异则准确更正。

### FIX-08 [P2] 第9页与第11—12页：删除工作记录用语，改准确选样描述

- 第9页：`In the existing age-specific decomposition` → `In the age-specific decomposition`。
- 第11—12页：`the economically selected reference-country set` → `the purposively selected G20 country set`（如实际措辞需要，可写 `the purposively selected set of 18 G20 reference countries`）。

不更改18个主权国家集合，不把G20叫作代表性世界样本，也不因措辞改变重新估计数值。

### FIX-09 [P2] 正式干净版 vs 蓝字审阅版

- **审阅标注版**：保留老师Blue K PDF原件（颜色及原始说明不变）；另生成我们的变更对照/修订说明，最好列明上面FIX-01—08的“前→后”。
- **投稿干净版**：删去首页临时 `Editorial revision: blue text marks ...` 和 `Numerical results and plotted data have not been re-estimated.` 两句内部编辑说明，并将文字恢复正常黑色；如果正文需保留科学事实，不要删去方法和限制中“不重新估计/无联合draws”的真实说明。无须宣称期刊明文禁止蓝字。
- 两个版本保留相同的最终科学内容；不在clean版遗漏老师已合入的新增段落。**本次不执行投稿。**

## 4. 必须保留的科学边界及数字

- 主比较：女性15—49岁七年龄组、1990—2023、中国减18个其他G20主权国家、同年GBD年龄内人口份额为主；`D(t)=China−reference`，`ΔD=D(2023)−D(1990)`。
- 主分解**点估计**：`+271.51 − 208.62 + 88.65 = +151.54`／10万人；`58.5%` 是有符号净变化分解比例，非病因、患者或可避免病例比例。
- 2023继发不孕基准下GBD差值：`+2.16 / −47.99 / −127.89`；UN人口份额下：`+2.26 / −48.34 / −127.89`；两套基准不得混列。
- 国家剔除印度`+56.16（39.8%）`、剔除俄罗斯`+110.34（67.9%）`是敏感性情景；不是95%区间。40—44岁`+23.76`、35—39岁`+20.42`、15—19岁`−2.27`为标准化分量。
- 没有来源确认的**联合对齐**GBD posterior draws，衍生量只可报告点估计。不能把边际UI、独立模拟、国家bootstrap、角点舍入或压力情景伪装成联合后验区间/独立验证。
- 七组已发表六位年龄权重与Chen 2026附表匹配；官方全精度来源仍待独立确认。**本任务不改权重或重跑率差**；如发现真实来源冲突，形成单独问题报告及可复现的条件方案，不擅自重算覆盖本文。
- 保留原主稿**3张主表、5幅主图**，补充材料**S1–S11表、S1–S7图**、现有英文参考文献与主要结论。新增值都应指向原有CSV；如无对应输出则不可称已完成。

## 5. 执行、检查、交付验收（Codex必须真实完成）

**输入核验**：记下 Blue K PDF、v6原稿 `.tex/.docx`、补充、主要汇总CSV与代码的SHA256及路径；核实可编辑蓝字源是否存在。不得把旧文稿当作已含蓝字。

**生成独立候选版**（文件名均以`20261030_`开头）：
- `20261030_PCOS_HumanReproduction_BlueK_v7_DRAFT_Manuscript.tex`、`.docx`、`.pdf`（clean投稿稿）；
- `20261030_PCOS_BlueK_v7_DRAFT_ChangeLog.md` / `.csv`（FIX-01—09逐项原句、最终句、原因、页码、在新文件的定位、核验状态）；
- 如补充需保持一致，则生成 `20261030_PCOS_HumanReproduction_BlueK_v7_DRAFT_Supplement.tex`/`.docx`/`.pdf`，否则附“补充未改、与clean正文兼容”的逐项检查记录；
- `20261030_PCOS_BlueK_v7_DRAFT_Verification.json`：版本、输入/输出哈希、TeX编译日志/错误警告、Word/PDF逐页核验、引文映射、表图/正文数字对照、原稿保护、共享状态。

**质量门槛**：
1. `BlueK_vs_v6_crosswalk.csv`覆盖老师所有语义修订，**不是只执行9处patch**；蓝字版现有合理表述全部保留。
2. 对第3/10页两处术语、第1页问题、第12页AI、第14页Xu、第13页公开包、第9/11页措辞逐项验证为通过；全文不得有两个互相矛盾的表达。
3. 论文正文、图注、图表、补充中的所有可核实数值与旧v6结果一致；若文本说“有新统计结果”，必须找到真实执行日志，否则删除该主张。
4. 只改变编辑内容，不触发GBD模型重拟合、新数据下载、重跑原始统计或新后验区间；即使运行了排版/QC，也要标明其与科研结果计算的区别。
5. TeX真正编译成功，主稿和受改补充真正生成PDF，检查公式、参考文献、页脚、英文撇号、连字符及图表。Word编辑版与TeX最终正文一致；不能以“已提交脚本”代替实际核验。
6. 没有敏感原始GBD/医院病例或私密认证信息进入公开仓库；所有旧稿、XX、原分析文件及旧Git提交保留，不做force push、reset或覆盖。

**保存及同步**：
- 新稿、日志、Word/PDF与许可允许的汇总双存原PCOS Google Drive和GitHub（内容及hash读回核验）；研究原件只留Galaxy及既有私人位置。
- **Overleaf PCOS项目只上传两份论文类 `.tex`（主稿以及确有新版时的补充）；严禁上传PDF/Word/ZIP/图片/CSV/bib或其他文件，也不允许仅改扩展名。** 上传后核验正确项目、文件名和内容，必要时实测编译；保留旧v6 .tex。
- 完成后再次读共享最新版本，合并写回 `CHATGPT_HANDOFF`、`CODEX_RUN_LOG`、`RESULTS_INDEX`（若新增已验证制品）、`NEXT_ACTIONS`、`SYNC_CHECK`；**只有用户作出新的科学决定才更改科研定义条目**。记录实际做过/未做过，不要标“已验证”于尚未运行的工作。
- 最后用中文简报：完成/未完成的FIX清单、最终文件/云端链接、旧稿是否保留、数字是否保持、AI声明依据、是否真实编译及核验、是否上传Overleaf、是否投稿（必须为否）、阻塞问题。

## 6. 严格停止条件

如果找不到Blue K PDF可读内容且无法恢复，**不得**仅改旧v6然后称“老师蓝字已落实”；应报告具体源文件阻塞，并保留已检索的日志。若原稿版本或基线冲突，应先合并并生成差异检查，不擅自覆盖；若关键期刊官网不可访问，不得虚构硬性格式要求；如无真实联合draws，不进行“95%UI补全”。

**本任务的成功标准**：以老师已修改的Blue K科学正文为完整新底稿 + 8项定位文字/引用修复 + 第9项clean/审阅双版 + 与全部既有结果一致 + 可编辑TeX/Word和PDF及真实核验 + 新版本独立交付，不破坏任何旧稿或数据。
