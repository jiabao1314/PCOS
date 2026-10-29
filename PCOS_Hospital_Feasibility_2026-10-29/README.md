# PCOS 不确定性与医院数据可行性评估：2026-10-29

本轮对应用户关于补充不确定性证据、医院数据用途和高水平SCI文献的评估请求。原始工作簿只在现有私人Drive同步目录读取，没有改写，没有复制进本目录或公共GitHub。公开内容仅含汇总质量审计、GBD汇总压力测试、分析代码与研究建议；不含姓名、门诊号、联系方式或患者级记录。

- `docs/评估与操作方案_2026-10-29.md`：完整评估和可执行方案。
- `results/hospital_feasibility_audit.json`：4份文件的记录数、缺失、重复标识、字段一致性及候选关联汇总。
- `results/GBD_marginal_limit_stress.csv`：基于原始率边际界限的非概率压力范围，不能当作95%区间。
- `results/GBD_reference_tipping_points.csv`：在固定中国率和年龄权重下，参照率统一改变至差值为零的阈值。
- `results/GBD_stress_metadata.json`：明确统计解释限制。
- `code/audit_hospital.py`、`code/uncertainty_stress.py`：可复算代码。

本次医院数据审查没有拟合临床结局模型，没有作治疗效果比较，没有将医院样本用于校准国家患病率。伦理/许可、中心数、妊娠结局定义与可补充的随访资料尚待用户确认。作者等XX不在本轮询问范围。

## 复算

使用Python 3.12、pandas、numpy、openpyxl及xlrd。只读原始数据，输出汇总；原始路径由研究者在本地传入。

```sh
python code/audit_hospital.py --source-dir '/private/hospital/folder' --output results/hospital_feasibility_audit.json
python code/uncertainty_stress.py --input-dir ../PCOS_Revision_2026-10-29/data/input --output-dir results
```

GBD压力测试依赖上一修订包的真实输入及独立复算结果进行交叉校验。新增分析结果与评估按固定规则保存Drive和GitHub；本轮没有下载新的研究数据，医院原始敏感数据保持在其既有私人位置。不能将患者级医院数据纳入公开代码结果包。
