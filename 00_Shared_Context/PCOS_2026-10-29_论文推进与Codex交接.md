# PCOS/GBD 论文推进与 Codex 交接（2026-10-29）

**状态：科研审阅与下一步任务草案；不是新统计结果或用户已确认的新科研决定。**
**来源版本：** Google Drive `00_Shared_Context/PROJECT_STATUS.md` 最后更新 2026-10-29T17:15:26+01:00；`DECISIONS.md`、`NEXT_ACTIONS.md`、`CHATGPT_HANDOFF.md`、`SYNC_CHECK.md` 同日；GitHub `PCOS_Revision_2026-10-29/README.md`、`manuscript/main.tex`、`docs/revision_analysis_qc.json`、`docs/RESPONSE_TO_REVIEW_2026-10-29.md`。

## 一、保持主稿范围

- **当前主稿：** `PCOS_Revision_2026-10-29/`，女性15–49岁七年龄组，1990–2023年，中国与另外18个G20主权国家，GBD 2023估计的PCOS相关总/原发/继发不孕。不要混入医院四文件临床可行性分支、早期NSFG研究或历史预测模块。
- **估计目标：** 描述性的中国减去参照国 pooled age-standardized infertility prevalence rate difference；分解中国率、参照国率及年龄内参照国家人口份额变化。当前份额、固定1990份额、等国家份额回答不同问题；不将一个基准下的数值外推为另一个基准下的估计目标。
- **已核验记录：** R/Python四核心表合计1,488行，最大差约5.69e-13；1,440行敏感性分解，恒等式最大残差约1.99e-13。以上是已有QC记录，本次未重算。
- **现有主结果：** 1990–2023总不孕率差变化 +151.54/10万，其分解为 +271.51（中国率）−208.62（参照国率）+88.65（份额）。58.5% = 份额项 / 有符号净变化；在指定国别剔除与年龄范围敏感性中为39.8%–67.9%，非95%区间，不能声称所有设定中都超过50%。
- **基准示例：** 2023年继发不孕在UN当前份额下中国−参照差 +2.26/10万；在UN固定1990份额下 −48.34；等国家份额下 −127.89。这是更换**估计目标/参照定义**带来的符号差异，不是同一参数置信区间内的显著变化。
- **严格限制：** 未获得确认联合对齐GBD draws，因此派生差值、比例和分解只报告点估计，不拼接边际UI、不把独立模拟/国家bootstrap或情景压力范围称后验区间。UN人口份额替换不是疾病率外部验证。研究使用许可与医院伦理审批不能混同。

## 二、科研审阅中发现的投稿前重点

**P1：文献定位/创新性（必须修稿，拟开展）**

已有PCOS相关不孕GBD研究报道多国、跨年疾病负担及分解（Liu等，*Human Reproduction* 2024，doi:10.1093/humrep/dead241；Liang等，*Frontiers in Public Health* 2025，doi:10.3389/fpubh.2025.1693486；另有中国/全球趋势研究见doi:10.1016/j.rbmo.2025.105239）。当前稿件要主动区分：**现有研究主要描述PCOS负担及其时间变化；本稿的具体方法学问题是，在固定年龄权重下， pooled 国际参照的国家构成仍随时间变化，导致比较率差及其变化混入参照构成项。** Kitagawa分解是已有方法，不能宣称算法创新。应在Background增加1段直接对比，避免泛称“first”或“new method”。文献综述并非完整系统检索，引用内容提交前再经人工核对。

**P1：估计目标与基准解释（已写但建议再加可见性）**

在Methods或正文Table 3旁增加一个简短的“benchmark interpretation”表/段，三行列明：当年份额=当年18国人口加权参照；固定1990份额=以历史国家构成重加权当年率；等权=18国每个国家同权。正文结果的符号变化描述为“不同benchmark定义下的差异”，不要暗示同一因果量反转。

**P1：不确定性与限定（现有正确，继续保留）**

若没有联合对齐draws，不生成派生95%UI或p值。摘要、表注、Figure 5、Discussion应保持“model point estimates”的限定。对+2.26/10万的近零结果，不写成真实人群中已确定高于参照；不写“statistically significant”。

**P1：复现与正文一致性（由Codex复核，拟开展）**

复用现有`results/python/`、`results/R/`和质控日志，创建一份逐条CLAIM→TABLE/FIGURE→CSV列→代码→输入manifest的核对表，不必重跑全部历史模型。重点核对摘要、Figure 5/Table 3符号和单位、58.5%分母定义、敏感范围来源、subtype 69.4%与reference share 58.5%不可相加、G20国家集、15–49年龄权重归一化、GBD人口/UN份额替换、伦理和数据可用性文本。新结果仅以实际运行日志为准。

**P2：期刊适配（拟开展）**

保留当前`Reproductive Health`备选修订稿，临近投稿时才按官方最新期刊范围、稿件格式、伦理和报告要求做适配核查。目标中科院一区但不保证分区/录用；作者/经费/单位XX由用户补齐，暂不妨碍科研修订。

## 三、英文可直接纳入 Background 的候选段（尚未写入主稿）

> Previous GBD-based studies have quantified the temporal burden of PCOS-attributed infertility across countries and age groups, including trends, projections, and decompositions of burden changes. These analyses do not, by themselves, resolve a distinct question arising in comparative epidemiology: whether an age-standardized difference relative to a population-pooled multinational reference remains interpretable when the reference countries' within-age population shares change over time. Even with fixed age weights and a fixed country set, the composition of the pooled reference can vary. We therefore distinguish changes in estimated rates from changes in reference-country shares using an established symmetric decomposition, and compare contemporary, historically fixed, and equal-country benchmarks as alternative descriptive estimands rather than competing estimates of one causal quantity.

将合适的既有及新增文献引用加到该段；避免原文复制以及“首创”措辞。该段属于**拟采用文稿草案**，未经过作者审阅和编译。

## 四、交给 Codex 的执行指令

1. 开始前重新读取Google Drive的`PROJECT_STATUS`、`DECISIONS`、`NEXT_ACTIONS`、`CHATGPT_HANDOFF`及`SYNC_CHECK`，确认本地/远端版本与改动状态；历史保留、冲突先合并。
2. 以`PCOS_Revision_2026-10-29`为唯一主稿，核对以上论文正文的估计目标/创新性/单位/敏感性；不要混进医院和NSFG工作范围。优先复用已有CSV和代码，不必重复下载或重跑全部统计。
3. 做一份`MANUSCRIPT_CLAIM_AUDIT.md`：逐项列出数字主张、真实代码/CSV证据、是否已验证、未解决问题。独立核查发现不一致时先列差异，不默默改结果。
4. 在**新修订分支或保留旧稿副本**中试着纳入Background上面的英文段落（根据文献核对后完善引用）及基准解释对照，不覆盖2026-10-29验证版。生成diff并执行TeX编译、引用/编号/单位检查。
5. 保存结果与论文到允许的Drive/GitHub位置，禁止把许可GBD原件、患者原件或凭证公开。对更新的每个共享文件完成原位读回/哈希验证；如果无法双端同步，必须报告“待同步”。
6. 只有真正完成的任务才更新`CODEX_RUN_LOG`、`RESULTS_INDEX`、`PROJECT_STATUS`、`NEXT_ACTIONS`，并保留运行命令、版本及科学局限。此次交接的“拟开展”不得预先改成“已验证”。

## 五、完成标准

- 创新性段落对比至少已有上述3项PCOS/GBD相关文献且引用可核对；不冒称方法创新或独立外部临床验证。
- 主要数值/图表证据链逐项核对，缺乏联合draws的边界与所有统计结论保持一致。
- 新TeX/PDF修订独立存档，旧稿不覆盖；新增分析仅在实际计算并验证后出现。
- Drive/GitHub同步有实际回执；项目交接文档有日期、执行状态与后续待办。

**本文件生成者：ChatGPT；更新日期：2026-10-29。当前文件为可供Codex接收的交接文档，未声称已写入Drive、GitHub或主稿。**
