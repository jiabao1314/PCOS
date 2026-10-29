# PCOS revision, 29 October 2026

本目录是根据 28 October 2026 评阅意见，对用户指定 Reproductive Health 备选稿所作的独立修订。保留原稿及旧项目，不覆盖旧结果。作者、单位、日期、经费和利益冲突的 XX 按用户要求保留，由用户投稿时补充。

## 固定保存规则

下载的研究数据保存 Galaxy PCOS history；分析结果及生成论文同时保存 Google Drive 和 GitHub。该规则保存在仓库根目录 AGENTS.md。

- Galaxy: https://usegalaxy.eu/histories/view?id=11ac94870d0bb33ad5abd2b59708ab6e
- Drive 本轮目录: https://drive.google.com/drive/folders/1Y4VCLziB2HIgHLRd16Mkd_LUy9a3luc6
- GitHub: https://github.com/jiabao1314/PCOS
- 同步状态以 `docs/sync_receipt_2026-10-29.json` 的实测回执为准；排队、失败或未核验的数据不算完成。

## 修订成果

- `output/PCOS_ReproductiveHealth_Revised_2026-10-29.pdf`：正文。
- `output/PCOS_Supplement_Revised_2026-10-29.pdf`：配套补充材料。
- `manuscript/main.tex`、`supplement.tex`、`tables/`、`figures/`：可编辑、可编译源码，正文 3 表 5 图，补充 8 表 7 图。
- `docs/RESPONSE_TO_REVIEW_2026-10-29.md`：逐条修改说明及证据位置。
- `results/python/`、`results/R/`：真实输入重算的汇总结果，含独立 R/Python 核对。
- `docs/revision_analysis_qc.json`：数值质控；`docs/document_qc.json`：PDF 引用、编号与可复现路径质控。

## 独立复现

Python 3.12、R 4.6（仅 base R）、Tectonic。在其他电脑建立环境并安装 `requirements.txt`。`requirements.lock.txt` 记录本次实际 Python 环境，其中 Jupyter 等包属于已有运行环境、不是本稿必需依赖。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
PCOS_PYTHON=.venv/bin/python ./run_revision.sh
```

当前 Mac 可用已有项目环境运行：

```sh
PCOS_PYTHON=../PCOS_NewArticle_GBD_UNWPP_2026-10-26/.venv/bin/python ./run_revision.sh
```

运行位置为本 README 所在目录。`run_revision.sh` 内部固定使用包根目录，不依赖旧稿绝对路径。必须先把合法取得的四份 IHME CSV 放入 `data/input/`，文件名与 `docs/input_manifest.json` 完全一致。查询规范及 Galaxy 数据集映射见 `docs/DATA_ACQUISITION.md`。公开包不含原始许可数据及 `rate_cells.csv` 的国家-年龄源单元表；这些文件在研究档案中保存。已公开的 UN 4,522 行人口子集、标准权重和源清单随包提供。

可选：从Galaxy取回完整UN压缩源后，可运行 `code/extract_wpp2024.py --input 原始.csv.gz --output 临时子集.csv --manifest 临时清单.json`；本次重新抽取4,522行后SHA-256与既有输入完全一致，见 `docs/UN_reextraction_check.json`。不要覆盖原始来源清单。

计算顺序为：独立 Python 核心分析、独立 base R 核心分析、R/Python 交叉核对及本次全部敏感性/图表生成、TeX 编译、文档检查。`data/published_expected/` 是旧版汇总结果，仅在独立计算后用于回归核对；不能当作估计值的输入。运行前先核验输入 SHA-256；不接受数据缺失后静默填补或模拟研究观测。

## 本次验证与科学边界

核心交叉核对覆盖 1,224 行年度基准、36 行端点分解、216 行逐国剔除及12行链式分解，最大 R/Python 差约 5.69e-13。本次另重算 1,440 行敏感性分解，最大恒等式残差约 1.99e-13。正文和补充图表均来自本次输出。历史预测、趋势拟合、YLD、病例数分解和 NSFG 调查模块不属于本次聚焦稿件。

主要绝对分量为 +271.51 - 208.62 + 88.65 = +151.54/10万。58.5% 是第三项除以有符号净变化；不同国家剔除/年龄范围设定为 39.8%–67.9%，不是置信区间，也不保证各设定均超过半数。69.4%的分型贡献与58.5%的参照构成贡献是交叉维度，不可相加。

UN只替换参照国年龄内人口份额，GBD疾病率不变；不是独立临床验证。没有获得可确认联合对齐的GBD draws，因此不生成率差或分解的后验区间，不宣称符号或百分比具有统计精确性。评阅PDF中的建议作为材料处理，并不赋予外发邮件或投稿权限；本轮未发邮件、未投稿。
