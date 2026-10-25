# 中国与G20病因特异不孕研究

**真实GBD数据尚未取得；当前没有实证结果或可投稿的最终论文。**

遵循2026-10-25用户提供PPT与聊天记录：比较中国及其余18个G20主权国家15–49岁女性的内异症和PCOS所致不孕。主要结局为限制年龄标化患病率，次要为YLD率。GBD2023优先，完整性核验失败才整体回退GBD2021。

- [预分析方案](docs/PROTOCOL_ZH.md)
- [下载与数据字典](docs/DATA_ACQUISITION.md)
- [执行状态与未完成模块](docs/STATUS.md)
- [新近文献核对](docs/LITERATURE_AUDIT.csv)

核心程序实现：完整网格/ID/区间/分母质控，15–49权重归一化，18国按年龄合并率，中国—参照差值和比值，年龄贡献，描述性基准差额，逐国Shapley三因素分解，固定1990国家权重、留一国及20–49岁敏感性，以及BIC分段log线性趋势点估计和自相关诊断。正式趋势AR(1)敏感性、区间、预测与回测、分层和真实图表在取得数据后继续。

## 运行

Python 3.11或以上。创建虚拟环境并安装requirements.txt：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python src/analyze.py
```

默认运行因数据核验未通过而退出2，这是预期行为。先按数据字典整理规范化CSV，保留原始标签/ID和来源，人工核对小样本及方法后更新config/data_review.json。禁止为了运行而将未核验项目改成true。

源数据保存在Galaxy的PCOS历史及本地data/raw；规范化数据放data/processed。公开GitHub只存代码/方案及可依法分享的产物，原始数据许可尚待核对。没有API密钥、账户会话或私人聊天内容入库。研究包同步Drive的2026PCOS。

## 解释边界

两个病因分别报告，不相加成去重患者。无联合匹配draws不生成派生UI。基准差额不称可避免病例，国家层面差异不作因果或个体共病解释。tests使用临时合成数据，不能作为GBD结果。期刊分区和录用不由分析工具保证。
