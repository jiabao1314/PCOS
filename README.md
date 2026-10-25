# 中国与G20病因特异不孕：GBD 2023

真实数据分析：19个G20主权国家、女性15–49岁、1990–2023年，分别研究PCOS及子宫内膜异位症所致不孕。已生成英文论文草稿、结果表和图。总不孕主分析输入为36,176行，年度分层Number另有36,176行、端点分层验证4,256行，匹配人口为4,522行；同版、完整网格和分母核验通过。

- [执行状态与限制](docs/STATUS.md)
- [英文论文TeX](manuscript/main.tex)
- [论文PDF](output/pdf/GBD2023_infertility_manuscript_draft.pdf)
- [预分析方案](docs/PROTOCOL_ZH.md)
- [数据下载与字典](docs/DATA_ACQUISITION.md)
- [结果表](results/tables)
- [图表](results/figures)

主要发现：中国PCOS相关不孕ASPR从333.56升至605.08/10万，仍低于其余18国合并参照，但差距缩小；病例增加主要对应年龄别患病水平变化，人口因素部分抵消。分层显示原发不孕仍明显低于参照，继发不孕接近参照。内异症2023年近似参照的结果对末年和参照构成敏感，不能概括为稳定长期收敛。

## 复现

Python 3.12。将合法取得的原始数据放入数据字典指定目录；源数据因IHME条款及文件体量，存于研究者的Galaxy/Drive档案，不包含于本公开代码仓库。预分析方案的早期“未取得数据”表述属于执行前记录，以当前STATUS和回执为准。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python src/prepare_inputs.py
.venv/bin/python src/analyze.py
.venv/bin/python src/trend_sensitivity.py
.venv/bin/python src/endpoint_sensitivity.py
.venv/bin/python src/forecast_validation.py
.venv/bin/python src/make_figures.py
.venv/bin/python src/analyze_strata.py
.venv/bin/python src/manuscript_tables.py
.venv/bin/python -m unittest discover -s tests -v
tectonic --outdir output/pdf manuscript/main.tex
```

预测验证比较朴素模型、训练期AICc选择的低阶ARIMA和阻尼ETS，完整结果包含失败保留判断。没有通过稳定增益条件，故不外推未来病例。TeX项目自带矢量图及表，可独立编译；重新生成图后需同步复制PDF到manuscript/figures。

无联合匹配draws，不生成派生GBD不确定区间；趋势CI仅条件模型CI。基准差额不称可避免病例，国家层面差异不作因果或个体解释。测试使用临时人工固定值，仅验证数学和数据门控，不作为研究结果。稿件中的作者及利益声明待真实团队填写，期刊分区和录用尚未确认。
