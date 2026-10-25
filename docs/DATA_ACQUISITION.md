# 数据提取与验收清单（尚未下载真实GBD结果）

更新时间：2026-10-25（Europe/Paris）。GBD 2023为首选；不能获取两病因完整不孕分项时，整体退回GBD 2021，禁止拼接版本。

## 1. 首批试下载

在 https://vizhub.healthdata.org/gbd-results/ 登录后，选择Infertility损伤类别与Endometriosis、Polycystic ovarian syndrome病因交叉。国家China，女性Female，35–39岁，2023年，Prevalence和YLDs，Number和Rate。总不孕口径下预期8个结果单元。保留筛选截图、实际标签/ID、查询时间、官方CSV、下载邮件/任务标识和方法定义。先验证目标数据存在，不能将疾病本身的负担替代所致不孕。

工具当前未登录且出现自动访问验证。没有记录或调用隐藏接口，没有绕过验证。方法页面通过网页检索访问返回403，病例定义未完成核对。GBD采用的定义不得直接用WHO临床12个月定义替代。

## 2. 完整提取

固定19个主权国家见config/study.json；EU和AU不作为额外人口加入。实际国家标签必须根据导出映射到配置中的规范标签，原始标签和ID同时保留。GBD 2023：1990–2023，7个五岁年龄组，2病因，2指标，2度量，总不孕预期36,176行；同版女性年龄别人口4,522行。GBD 2021对应34,048行和4,256行。原发/继发不孕单独存放，核对互斥与可加性后才能作为可选分层，不重复加入总不孕。

另需：官方GBD标准人口各年龄权重和来源；与目标版本匹配的人口；方法文件；数据使用条款；匹配draws可得性。人口预测仅在完成主分析后获取，UN WPP 2024属于条件模块。

## 3. 保存位置

- Galaxy：现有PCOS历史（用户所称文件夹），以原始文件名上传CSV、人口、权重、方法文档和query记录。验收后保留原文件，清理另存。
- 本地：data/raw只读保留下载，data/processed保存规范化输入；记录每个文件SHA256。
- GitHub公开仓库：先同步代码、方案与数据字典。原始数据公开再分发前核对许可。私有账户信息、会话、密码、API密钥不入库。
- Drive 2026PCOS：研究包及后续分析产物。

## 4. 规范化文件接口

burden.csv必需列（参见src/analyze.py）：gbd_version, location_id, year, sex_id, age_group_id, cause_id, impairment_id, infertility_type, measure_name, metric_name, location_name, age_name, sex_name, cause_name, impairment_name, val, lower, upper。保留额外原始字段，例如measure_id、metric_id、sequela_id、原始名称、提取日期和query_id。版本为GBD 2023或GBD 2021；age_name使用15-19等ASCII标签；规范化名称不改变ID。

population.csv：gbd_version, location_id, year, sex_id, age_group_id, population。单位为人，不是千人。

weights.csv：age_name, weight。必须为官方标准人口的对应年龄权重，程序只在15–49内归一化，不自行假设等权。

不提供伪数据模板作为研究输入。tests仅使用临时合成数值验证公式，运行结束即清理。

## 5. 数据门控

仅当试下载、病例定义、分母、标准人口权重、损伤与病因ID、总不孕定义和原始清单均经来源核对后，更新config/data_review.json并锁定版本。缺失不作0。核验lower≤val≤upper，患病率0–100000，人数允许小数，Number/同龄女性人口×100000应重现Rate。主分析要求完整年度×年龄×国家×病因×指标×度量网格。

无联合匹配draws时，派生差值、率比、合并参照及分解只给点估计。不得把各国上下限相加或从边际UI独立抽样伪造draws。
