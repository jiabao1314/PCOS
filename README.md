# 中国与G20病因特异不孕：GBD 2023 + 独立NSFG复现

当前版本（2026-10-25）完成了19个G20主权国家、女性15–49岁、1990–2023年PCOS及子宫内膜异位症相关不孕的GBD 2023比较分析，并新增美国NSFG 2022–2023个体公共调查的独立复杂抽样复现，用于检验结局定义与分母敏感性。

## 当前主成果

- [最终数据与同步状态](docs/FINAL_DATA_STATUS_2026-10-25.md)
- [Human Reproduction候选稿TeX](manuscript/human_reproduction.tex)
- [Reproductive Health备选稿TeX](manuscript/main.tex)
- [Human Reproduction候选稿PDF](output/revision_v2/PCOS_Human_Reproduction_candidate_v2.pdf)
- [Reproductive Health整合稿PDF](output/revision_v2/PCOS_Reproductive_Health_integrated_v2.pdf)
- [Additional file 1](output/revision_v2/PCOS_Additional_file_1_v2.pdf)
- [Additional file 2：代码与派生结果](output/revision_v2/PCOS_Additional_file_2_code_results_v2.zip)
- [可编译TeX源文件包](output/revision_v2/PCOS_manuscript_TeX_sources_v2.zip)
- [NSFG复现结果](results/external)
- [外部证据与GBD draws核验](docs/EXTERNAL_TRIANGULATION_AND_DRAWS_AUDIT_2026-10-25.md)
- [Galaxy上传清单与状态](docs/GALAXY_PCOS_UPLOAD_MANIFEST_2026-10-25.json)
- [创新性、不足与期刊核验](docs/JOURNAL_AND_NOVELTY_AUDIT_ZH.md)

## GBD 2023 主分析

总不孕主分析输入36,176行，年度原发/继发Number 36,176行，端点分层Number/Rate 4,256行，匹配女性人口4,522行；同版、完整网格、分母和端点Rate核验通过。

核心结果包括：
- 中国PCOS相关不孕15–49岁标准化患病率从333.56升至605.08/10万；其他18个G20主权国家合并参照从606.48升至726.45/10万。
- 中国减参照差值由−272.92变为−121.38/10万，净变化+151.54。
- 对称分解：中国产生率变化+271.51、参照国家率变化−208.62、参照国家人口份额变化+88.65；后者对应净差值变化的58.5%。年度链式敏感性给出+87.11（57.5%）。
- 原发/继发分型显示，继发不孕贡献69.4%的净差值变化；这与58.5%的参照构成贡献属于相交维度，不能相加。
- 内异症2023年接近参照对终点年份敏感；2022总差值为−8.76，而2023为−0.20/10万，因此不作稳定长期收敛结论。
- 预测模型未稳定优于朴素基准，故不报告长期外推作为主结果。

## NSFG 2022–2023 独立个体复现

GitHub Actions直接从CDC官方 `ftp.cdc.gov` 下载公共女性受访者ZIP并锁定SHA-256：`ef9f0ec715ce7909b50f1ea67958166b2cd1ad3482c4b083174898ec8c7ceaaa`。原始文件5,586名女性、1,912个变量；主要20–49岁访谈年龄域4,855人，CDC筛查年龄敏感性4,856人。

设计使用 `WGT2022_2023`、`VEST`、`VECL`；20个分层、80个PSU、60个设计自由度。R `survey` 与独立Python线性化实现重建36个比例和36×36联合设计协方差，达到数值一致。

主要无调整结果：
- PCOS：广义当前生育困难45.16% vs 17.07%，PR 2.65（95%设计CI 2.30–3.04）；当前婚姻/同居人群12个月不孕PR 1.77（1.22–2.57）。
- 内异症：广义当前生育困难33.00% vs 18.59%，PR 1.78（1.40–2.25）；当前婚姻/同居人群12个月不孕PR 0.84（0.50–1.43），区间跨1，不支持保护性结论。
- NSFG用于独立测量/定义敏感性三角验证，不是中国GBD水平、病因归因或终点跳变的直接外部验证。

## GBD联合draws：仍受提供方访问限制

GBD 2023的95%不确定区间来自posterior draws，但公共Results Tool仅发布最终估计和边际区间。当前没有获得跨国家、年龄、年份、病因和不孕类型联合对齐的posterior draw文件。已向IHME Data Team发送正式请求并获得自动收件回执，尚未获数据或批准。

因此：
- 派生的中国–参照差值、合并标准化率、分型贡献和参照构成分解仍报告点估计；
- 不从边际lower/upper独立抽样制造伪draws；
- 国家剔除、权重/终点敏感性和趋势模型CI不冒充GBD posterior uncertainty。

## 云端同步

- GitHub：当前代码、NSFG独立R/Python验证、设计协方差、整合TeX/PDF均已发布。
- Google Drive `2026PCOS`：已保存官方NSFG审计输入包、Human Reproduction候选稿、Reproductive Health备选稿、补充材料、TeX源文件和完整整合ZIP。
- Galaxy PCOS历史：既有GBD原始数据仍在；当前Chat浏览器连接仅支持读取、没有Galaxy写入/API工具，因此新增NSFG和整合v2文件已准备为Galaxy上传包，但未虚报已上传。详见上传清单。

## 投稿边界

Human Reproduction作为高风险一区候选；Reproductive Health作为二区备选。相近研究已覆盖常规GBD更新、趋势、分型、分解与预测，因此不能以这些内容宣称“首次”。当前较强的增量是：显式区分中国率、参照国家率、参照国家人口份额对国际差距解释的影响，并用独立NSFG个体数据展示结局定义/分母变化如何改变关联强度。

仍需真实研究团队最终补充和确认作者、单位、通讯作者/ORCID、伦理适用认定、基金、利益冲突、作者贡献、全体作者批准及永久归档DOI；项目尚未正式投稿。
