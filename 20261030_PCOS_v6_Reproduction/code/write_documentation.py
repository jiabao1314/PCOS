#!/usr/bin/env python3
"""Write dated instructions and exact paper-to-data map."""
from pathlib import Path
import csv,json,hashlib
R=Path(__file__).resolve().parents[1]
def write(n,t):(R/n).write_text(t.strip()+'\n',encoding='utf-8')
def main():
    write('20261030_README_ZH.md',r"""
# PCOS v6 完整复现与逐图学习包

建议把整个文件夹复制为 D:\20261030_PCOS_v6_Reproduction（也可放其他盘），先解压再运行。所有路径以本包为根，不需要原Mac项目。不要只复制notebook或单个脚本。

本包对应已接受的Human Reproduction v6及Overleaf r1编译稿，科学快照1abf337d9f23cc69292e03cd581b6a1557e6effe。仅纳入当前论文必需模块；旧预测、YLD、NSFG和医院可行性工作不是本论文分析。没有患者数据。论文原件位于paper；不更改原稿或既有XX。

## 老师：完整复现

1. 使用本次提供的FULL_PRIVATE完整压缩包，解压后确认data/input有7个文件，包括4份IHME CSV；不要公开上传这些许可输入及生成的rate_cells.csv。
2. 安装64位Python 3.12及R（本次验证Python 3.12.14、R 4.6.1；R仅用base R）。Windows安装Python时启用py启动器。首次安装依赖需要联网；研究原始数据已经在私人包内，无须重新下载。
3. 在包内打开PowerShell，执行：
   powershell -NoProfile -ExecutionPolicy Bypass -File .\20261030_Setup_Windows.ps1
   powershell -NoProfile -ExecutionPolicy Bypass -File .\20261030_Run_All_Windows.ps1
   ExecutionPolicy Bypass仅对本次命令进程生效，不修改电脑永久策略。
4. 检查verification/20261030_REPRODUCTION_CHECK.json的status为passed。保存日志、环境和所有差异；不要因命令启动就视为复现通过。
5. 检查figures/python和figures/R各12张图。论文版式以Python图为准；R为独立数值复算和同定义示意，绘图样式不同。
6. RStudio独立路线：打开20261030_PCOS_v6.Rproj，执行 source("code/reproduce_all.R", encoding="UTF-8")。R从原始输入独立计算，不调用Python；自身核对存档值，结果见verification/20261030_R_INDEPENDENT_CHECK.csv。Python的03 notebook再进行双语言全表交叉核对。

若不用PowerShell脚本，在包根目录执行：
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe code\reproduce.py all

macOS/Linux同样可运行：
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python code/reproduce.py all

Rscript需在PATH；Python入口还会查找Windows标准R安装位置。若找不到，按提示设置PATH或直接走RStudio路线。不要编辑数据来消除错误。

## 你：逐步理解12张图片

双击20261030_Start_Jupyter.cmd；若浏览器未自动打开，使用终端显示的本机地址。选择PCOS v6 (Python 3.12)内核。

- 01_Data_to_Estimands：7输入哈希、完整Python复算、权重和参照公式、从底层数组手算X/Q/S、408行亚型加和与S10。
- 02_All_12_Figures：初始化后任选一图；每图均有中文解释和原论文实际绘图代码。可修改筛选或颜色再运行，图片输出figures/notebook。
- 03_Independent_R_and_Audit：独立R分析、全表核对和老师验收。

02默认SOURCE="recomputed"，读取本次重新计算结果。若只想用GitHub公开包学习画图，可明确改为SOURCE="reference"；这只重绘已有公开汇总，不等于从原始数据复现。原始数据缺失时01和03必须报错，不静默改用参考结果。
notebooks/executed保存本次实际执行版供直接查看；notebooks顶层为干净可重跑版。输入/表图对应见docs/20261030_FIGURE_TABLE_MAP.csv。

## 目录

- data/input：原始4 GBD + UN子集 + 权重 + 来源清单。
- data/published_expected：计算之后的历史回归检查，不作估计输入。
- code：原核心Python/R、独立R敏感性与12图、便携总入口、notebook构建器。
- reference/aggregates：当前论文12类公开汇总和408行年度表；reference/tables为原表身与文献/定义表。
- results/python、results/R：本次复算输出。rate_cells.csv含受限源单元，保留私人包。
- tables/python：11原数值表身逐字核对及v6 S10数值输出。
- figures/python、figures/R、figures/notebook：原论文风格、独立R风格及逐图教学输出。
- paper：当前主稿/补充论文tex及云端编译PDF。无需编译TeX即可复现数值与图表。
- docs：来源、权限、哈希、图表地图、方法边界、运行说明。
- verification：本次真实核验。logs：R等运行日志。

## 预期检查与边界

7输入哈希；两套各4,522人口格；27,132病例/率格；1,064官方端点率；1,224年度基准行；36端点分解；216删一国；12链式分解；1,440敏感性；408年度亚型行；5主图+7补图。

Python结果须与论文存档数值逐表一致（容差1e-8）；R/Python核对12类表+408行表，报告每表实际最大误差。病例数百万量级在CSV导出末位可能有约1e-9绝对差，应结合列名和相对误差理解；率与比值另有逐列记录。11个原数值TeX表身逐字相同。GATHER、S9文献比较、S11定义比较是方法/证据表，保存原文及来源，不伪造为计算结果。

本机实际运行在macOS，另做含空格/中文目录的迁移检查。没有Windows D盘实机，因此“可复制到D盘、代码使用相对路径”不等于已在老师电脑运行通过。首次Windows执行仍需老师验收；不捏造跨平台验证。

复现的是已有GBD点估计的下游描述性分析，不重估GBD模型；缺合格联合draws，不生成差值/分解后验区间。设定敏感性范围不是置信区间，UN人口权重不是疾病外部验证，标准权重仍为既有六位复刻而非新确认全精度官方向量。原始完整UN全球源不是运算所需输入，已保存Galaxy；本包使用已哈希核对的4522行子集，提供可选extract_wpp2024.py及Galaxy映射。

本包不含投稿动作、不发送邮件。用户计划老师复现后投稿；当前不投稿。
""")
    write('docs/20261030_DATA_RIGHTS_ZH.md',"""
# 数据范围与公开边界

FULL_PRIVATE为用户及有合法研究使用权限的合作者本地复现准备，包含4份既有许可GBD原始导出；不因整理成包而改变来源许可。不得把FULL_PRIVATE、IHME CSV、rate_cells或国家-年龄源单元公开到GitHub。研究原档和Galaxy映射保留，未下载新研究数据。

GitHub只存显式审查的代码、无输出notebook、公开UN子集/来源/权重、全国或合并参照汇总、原论文及核验摘要。公开包不带4份许可GBD CSV；完整复现须从既有合法档案恢复相同字节，缺失即停止。data/published_expected/population_country_age_crosswalk.csv也只在私人包，不列公开清单。

UN WPP2024子集根据既有来源记录归属United Nations Population Division，CC BY 3.0 IGO；见data/input/UN_WPP2024_source_manifest.json。源数据适用各机构条款，本包不授予新的再分发权。

没有医院文件或患者级数据，不需要老师获取医院数据。Overleaf既定规则仅论文tex，本次代码/数据包不上传Overleaf；现有已核验论文保持。
""")
    write('docs/20261030_TEACHER_REVIEW_CHECKLIST_ZH.md',"""
# 老师复现签核记录（请在自己的电脑完成后填写）

本模板不是已完成的老师验收。

电脑系统/日期：
Python/R版本：
本包哈希/来源：
7输入哈希核对：
全流程命令与日志：
Python与论文12类汇总核对：
13类R/Python数值核对：
11原数值表身与S10：
12幅Python图与12幅R图：
是否理解参照构成与率差、X/Q/S及S/净变化：
是否保留无联合draws、四舍五入权重和描述性解释限制：
失败/差异及处置：
审核人/结论：
作者决定是否投稿：

请保留本地新增结果，不覆盖本次出包核验；任何新修订建立新日期版本。
""")
    guide=json.loads((R/'docs/20261030_FIGURE_LEARNING_GUIDE.json').read_text(encoding='utf-8'))
    rows=[]
    agg={
    'Figure1_PCOS_trends':'all_annual_benchmark_aspr.csv','Figure2_PCOS_subtypes':'all_annual_benchmark_aspr.csv',
    'Figure3_decomposition':'symmetric_decomposition_1990_endpoints.csv',
    'Figure4_population_source':'all_annual_benchmark_aspr.csv; symmetric_decomposition_1990_endpoints.csv',
    'Figure5_benchmark_sensitivity':'all_annual_benchmark_aspr.csv',
    'FigureS1_reference_exclusions':'composition_sensitivities.csv','FigureS2_benchmark_trajectories':'all_annual_benchmark_aspr.csv',
    'FigureS3_composition_sensitivity':'composition_sensitivities.csv','FigureS4_endometriosis_trajectory':'all_annual_benchmark_aspr.csv',
    'FigureS5_country_shifts':'age_weighted_reference_shifts.csv','FigureS6_terminal_country':'terminal_year_audit.csv',
    'FigureS7_terminal_age_type':'endometriosis_terminal_age_type.csv'}
    for x in guide:rows.append({'paper_item':x['figure'],'type':'computed figure','data':agg[x['output_basename']],'Python_output':'figures/python/'+x['output_basename']+'.png','R_output':'figures/R/'+x['output_basename']+'.png','notebook':'02 figure cell '+str(x['order']),'verification':'R/Python source-table numeric comparison; Python graph pixel comparison','question':x['meaning']})
    names=['prevalence','decomposition','benchmark','s1_endpoints','s2_sensitivity','s3_age','s4_chained','s5_population','s6_rate_conventions','s7_terminal','s8_rounding']
    src=['all_annual_benchmark_aspr','symmetric_decomposition_1990_endpoints','all_annual_benchmark_aspr','all_annual_benchmark_aspr','composition_sensitivities','age_decomposition','annual_chained_decomposition','population_share_TVD','national_annual_standardized','terminal_year_audit','standard_weight_rounding']
    for i,(n,s) in enumerate(zip(names,src)):
        label='Table '+str(i+1) if i<3 else 'Table S'+str(i-2)
        rows.append({'paper_item':label,'type':'computed table','data':s+'.csv','Python_output':'tables/python/'+n+'.tex','R_output':'results/R/'+s+'.csv','notebook':'01 + 03','verification':'exact original TeX body plus full independent numeric table check','question':'Same values, units and rounding as accepted v6.'})
    rows.append({'paper_item':'Table S10','type':'computed table','data':'v6_annual_subtype_differences.csv','Python_output':'tables/python/TableS10.csv','R_output':'results/R/v6_annual_subtype_differences.csv','notebook':'01 section 5; 03','verification':'all 408 rows vs accepted v6 archive and independent R','question':'Recent endometriosis primary/secondary cancellation.'})
    for n,question in [('GATHER checklist','Reporting checklist'),('Table S9','Literature comparison and evidence levels'),('Table S11','Clinical/GBD outcome and population distinctions')]:
        rows.append({'paper_item':n,'type':'source/method table, not estimated','data':'paper/Supplement.tex and source citations','Python_output':'reference/tables or paper/Supplement.tex','R_output':'not a statistical estimate','notebook':'01 final note','verification':'preserved accepted paper source; no invented numerical computation','question':question})
    with (R/'docs/20261030_FIGURE_TABLE_MAP.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    m=json.loads((R/'docs/input_manifest.json').read_text(encoding='utf-8'))
    with (R/'docs/20261030_INPUT_CHECKSUMS.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['path','bytes','sha256','md5']);w.writeheader()
        for p,x in m.items():w.writerow(dict(path=p,bytes=x['bytes'],sha256=x['sha256'],md5=hashlib.md5((R/p).read_bytes()).hexdigest()))
    provenance=json.loads((R/'docs/20261030_SOURCE_PROVENANCE.json').read_text(encoding='utf-8'))
    provenance['adaptations']=['R core explicit UTF-8 file input/output for Windows and decode Rscript ~+~ path spaces','Python revision main(check_r=False) permits Python-only teaching; full R checks run later via reproduce.py check','Python TeX table writer explicit UTF-8; no numerical formulas changed','Independent new base-R sensitivity and plotting code; Python orchestrator, notebooks and Windows launchers added']
    (R/'docs/20261030_SOURCE_PROVENANCE.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Wrote dated instructions, teacher template, figure/table map and checksums.')
if __name__=='__main__':main()

