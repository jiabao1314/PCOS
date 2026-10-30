#!/usr/bin/env python3
"""Create three clean teaching notebooks. No executed outputs published."""
from pathlib import Path
import ast,csv,json
import nbformat as nb
ROOT=Path(__file__).resolve().parents[1]
M=nb.v4.new_markdown_cell;C=nb.v4.new_code_cell
INIT="""from pathlib import Path
import sys
here = Path.cwd().resolve()
ROOT = next(p for p in [here, *here.parents] if (p / "docs/20261030_INPUT_CHECKSUMS.csv").exists())
sys.path.insert(0, str(ROOT / "code"))
import reproduce as rep
import numpy as np
import pandas as pd
print("复现包：", ROOT.name)
"""
def write(name,cells):
    n=nb.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'PCOS v6 (Python 3.12)','language':'python','name':'pcos-v6'},'language_info':{'name':'python','version':'3.12'}})
    nb.validate(n);nb.write(n,ROOT/'notebooks'/name)
def main():
    cells=[M("""# 01 从原始数据到论文估计量

对应当前已接受的Human Reproduction v6；Overleaf r1仅修复编译。顺序：核对7输入 → Python完整计算 → 看清权重与参照 → 手算三项分解 → 亚型加和 → 02逐图 → 03独立R。

19国（中国+18参照），1990–2023，女性15–49岁七年龄组，两病因、三亚型。复现GBD下游描述性点估计分析，不重拟合IHME模型。无合格联合draws，不生成后验区间。
"""),C(INIT),M("## 1 核对输入\n4份真实GBD CSV、UN人口子集、权重及UN来源清单。缺失或SHA256改变就停止。私人完整版已带齐；公开版须合法恢复GBD文件。"),C("rep.verify_inputs()"),M("## 2 从原始CSV完整复算\n原稿和输入只读；计算写入本包results/python、tables/python、figures/python。旧汇总只在计算完成后作回归核对。此Python步骤无需先安装R；独立R核对在03。"),C("rep.run_python()"),M(r"""## 3 标准化率与参照

由匹配GBD病例数/人口重建 $r_{cat}=10^5N_{cat}/P_{cat}$。七年龄权重先归一化 $w_a=w_a^*/\sum_aw_a^*$。

中国 $A_{CHN,t}=\sum_aw_ar_{CHN,at}$。参照国年龄内份额 $s_{cat}=P_{cat}/\sum_{c\in\mathcal R}P_{cat}$，合并参照率 $A_{\mathcal R,t}=\sum_aw_a\sum_cs_{cat}r_{cat}$。

$D_t=A_{CHN,t}-A_{\mathcal R,t}$。UN只替换人口份额，病率仍来自GBD。下面只显示权重与全国/合并参照汇总，不打印受限国家-年龄源单元。
"""),C("""weights = pd.read_csv(ROOT / "data/input/weights.csv")
weights["normalized_weight"] = weights["weight"] / weights["weight"].sum()
display(weights)
a = pd.read_csv(ROOT / "results/python/all_annual_benchmark_aspr.csv")
display(a[(a.cause=="Polycystic ovarian syndrome") & (a.subtype=="Total") & (a.benchmark=="dynamic") & a.year.isin([1990,2023])])
"""),M(r"""## 4 从底层数组手算1990–2023三项分解

$$\Delta D=X+Q+S,$$
$$X=\sum_aw_a(r_{CHN,a1}-r_{CHN,a0}),$$
$$Q=-\sum_aw_a\sum_c\frac{s_{ca0}+s_{ca1}}2(r_{ca1}-r_{ca0}),$$
$$S=-\sum_aw_a\sum_c\frac{r_{ca0}+r_{ca1}}2(s_{ca1}-s_{ca0}).$$

三项都是带符号的绝对贡献。$100S/\Delta D$不是患病归因分数、后验概率或置信度，可以超出0–100%。计算下方数组后与完整计算结果核对。
"""),C("""cells = pd.read_csv(ROOT / "results/python/rate_cells.csv")  # 受限单元只在私人包，勿公开
ages, years = list(range(15,50,5)), list(range(1990,2024))
refs = sorted(set(cells.country)-{"China"})
z = cells[(cells.cause=="Polycystic ovarian syndrome") & (cells.subtype=="Total")]
idx = pd.MultiIndex.from_product([refs,ages,years],names=["country","age_start","year"])
v = z.set_index(["country","age_start","year"]).reindex(idx)
r = v.gbd_rate.to_numpy().reshape(18,7,34)
p = v.gbd_pop.to_numpy().reshape(18,7,34)
s = p / p.sum(axis=0,keepdims=True)
cn = z[z.country=="China"].set_index(["age_start","year"]).reindex(pd.MultiIndex.from_product([ages,years])).gbd_rate.to_numpy().reshape(7,34)
w = weights.normalized_weight.to_numpy()
X = np.sum(w*(cn[:,-1]-cn[:,0]))
Q = -np.sum(w*np.sum((s[:,:,0]+s[:,:,-1])/2*(r[:,:,-1]-r[:,:,0]),axis=0))
S = -np.sum(w*np.sum((r[:,:,0]+r[:,:,-1])/2*(s[:,:,-1]-s[:,:,0]),axis=0))
net = np.sum(w*(cn[:,-1]-np.sum(s[:,:,-1]*r[:,:,-1],axis=0))) - np.sum(w*(cn[:,0]-np.sum(s[:,:,0]*r[:,:,0],axis=0)))
assert abs(X+Q+S-net)<1e-8
d = pd.read_csv(ROOT / "results/python/symmetric_decomposition_1990_endpoints.csv")
row = d[(d.cause=="Polycystic ovarian syndrome") & (d.subtype=="Total") & (d.source=="GBD") & (d.end==2023)].iloc[0]
assert np.max(abs(np.array([X,Q,S,net])-row[["china_rate_effect","reference_rate_effect","reference_country_composition_effect","net_gap_change"]].to_numpy(float)))<1e-8
display(pd.DataFrame({"component":["X","Q","S","net","100S/net"],"value":[X,Q,S,net,100*S/net]}))
"""),M("## 5 亚型加和与v6补充S10\n408行年度表逐行Total=Primary+Secondary。终点接近零可能来自原发/继发抵消，不证明历年稳定相同。"),C("""annual_types = pd.read_csv(ROOT / "results/python/v6_annual_subtype_differences.csv")
assert len(annual_types)==408 and annual_types.sum_residual.abs().max()<1e-8
print("408行加和最大残差",annual_types.sum_residual.abs().max())
display(pd.read_csv(ROOT / "tables/python/TableS10.csv"))
"""),M("## 6 下一步\n到02选择recomputed逐图运行，最后03独立R验收。GATHER清单、S9文献比较及S11定义比较是来源/方法表；随包保存，不伪装成统计输出。")]
    write('20261030_01_Data_to_Estimands.ipynb',cells)
    tree=ast.parse((ROOT/'code/revision_analysis.py').read_text(encoding='utf-8'))
    func=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='figures')
    blocks=[];pending=[]
    for stmt in func.body:
        pending.append(stmt)
        if isinstance(stmt,ast.Expr) and isinstance(stmt.value,ast.Call) and isinstance(stmt.value.func,ast.Name) and stmt.value.func.id=='savefig':
            blocks.append('\n'.join(ast.unparse(x) for x in pending));pending=[]
    assert len(blocks)==12
    titles=['图1：总体轨迹与率差','图2：原发与继发亚型','图3：三项对称分解','图4：GBD与UN人口参照','图5：当年/固定/等国基准','补图S1：删一参照国与年龄范围','补图S2：三基准年度轨迹','补图S3：构成项与有符号净变化','补图S4：子宫内膜异位症轨迹','补图S5：参照国构成变化','补图S6：19国末年变动审计','补图S7：年龄×亚型末年贡献']
    reasons=[
    '先看中国与合并参照的水平，再看差值。中国下降不必然意味着差值下降，参照也在变化。',
    '总量可能掩盖亚型不同趋势。两亚型用相同全部育龄女性分母和权重，可与总率加和一起理解。',
    '每组X+Q+S等于黑色菱形净变化。正负号须按中国率、参照率及参照份额各项定义解释。',
    '替换人口份额、保留GBD病率。相近结果是人口权重稳健性检查，不能称独立疾病验证。',
    '相同2023疾病率，更换参照基准就可能改变差值符号。三种基准不是同义替代。',
    '删除一国后在年龄内重新归一化其余17国；20–49也重新归一化年龄权重。画的是2023端点差。',
    '看34年轨迹，避免只看2023。UN仅用于人口份额，仍是同一GBD模型率。',
    '100S/有符号净变化可不在0–100%。50%虚线不是显著性阈值，39.8%–67.9%为设定范围，不是可信区间。',
    '末端接近零不代表历年接近零。三端点标记定位模型末年变化，不能据此推断疫情/临床机制。',
    '年龄内各国人口份额用固定标准年龄权重平均再作差，不是实际全龄人口占比或疾病率变化。',
    '同一模型来源的19国末年输出审计，不等于独立流行病学验证，不为末年突变编造机制。',
    '每柱是年龄权重×2022–2023率增量。七年龄×两亚型加和为总率增量，不是病因分数。']
    setup="""from notebook_support import figure_inputs
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from IPython.display import display, Image
SOURCE = "recomputed"  # 可改为reference学画图，但不是原始数据复现
a,d,sens,shifts,ez,ec,dyn = figure_inputs(ROOT,source=SOURCE)
print("图表数据来源:",SOURCE)
PCOS = "Polycystic ovarian syndrome"
TYPES,AGES = ["Total","Primary","Secondary"],list(range(15,50,5))
COLORS = ["#19566c","#ba572a","#6b8990"]
signed = lambda x,digits=2:f"{x:+.{digits}f}"
ss = sens[(sens.cause==PCOS)&(sens.subtype=="Total")&(sens.start==1990)&(sens.end==2023)&(sens.source=="GBD")]
labs = ss.scenario.str.replace("omit_","Without ",regex=False).replace({"main":"Main","ages20_49":"Ages 20-49"})
OUT = ROOT / "figures/notebook"
OUT.mkdir(parents=True,exist_ok=True)
def savefig(fig,name):
    fig.savefig(OUT/(name+".pdf"),bbox_inches="tight")
    fig.savefig(OUT/(name+".png"),dpi=180,bbox_inches="tight")
    display(Image(filename=str(OUT/(name+".png"))))
    plt.close(fig)
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"pdf.fonttype":42,"axes.spines.top":False,"axes.spines.right":False})
"""
    c2=[M("# 02 逐图理解：5张主图 + 7张补图\n\n先运行两个初始化单元，再任选一图。图形单元直接展示原论文的真实筛选/绘图代码，输出到figures/notebook。建议每图先预测变化方向，再运行，回答改变的是疾病率、人口份额还是基准定义。"),C(INIT),C(setup)]
    guide=[]
    for i,(title,reason,block) in enumerate(zip(titles,reasons,blocks),1):
        name=next(ast.literal_eval(s.value.args[1]) for s in ast.parse(block).body if isinstance(s,ast.Expr) and isinstance(s.value,ast.Call) and isinstance(s.value.func,ast.Name) and s.value.func.id=='savefig')
        c2 += [M('## '+title+'\n\n'+reason+'\n\nPNG/PDF: figures/notebook/'+name),C(block)]
        guide.append({'order':i,'figure':title.split('：')[0],'output_basename':name,'notebook':'20261030_02_All_12_Figures.ipynb','meaning':reason})
    c2 += [M("## 总体理解\n相同中国疾病率，在不同参照构成/定义下有不同差值；恒等式区分率变化和份额变化。敏感性范围和计算误差均不替代缺失的联合后验区间。本次复现不新增统计确定性。")]
    write('20261030_02_All_12_Figures.ipynb',c2)
    c3=[M("# 03 老师独立R复现与验收\n\nR直接读取原始CSV独立运算，不用Python输出生成估计；之后才交叉核对。12幅R图采用base R样式，科学数值、选样、单位与对应论文图一致。"),C(INIT),M('## 1 独立base R全分析\n需要单独安装R。可在RStudio打开.Rproj后source(\"code/reproduce_all.R\", encoding=\"UTF-8\")。'),C('rep.run_r()'),M("## 2 全部12类数值表 + v6年度亚型表核对\n核对键唯一、行集合、每列、NA位置，绝对误差阈值1e-8；还检查存档论文数值、11份原数值TeX表身以及408行v6年度表。缺失就报错。"),C('report=rep.check(require_r=True)\nprint(report["status"])\ndisplay(pd.DataFrame(report["independent_R_Python_checks"]))\ndisplay(pd.DataFrame(report["historical_aggregate_checks"]))'),M("## 3 老师验收\n核实7输入、4,522+4,522人口格、27,132率格、1,064官方端点率、1,224年度基准、1,440敏感性、408年度亚型及12幅图。按下表定位每个论文表图。\n\n这里在Mac的验收不代表老师Windows已验收。老师复现后保存系统/版本/日志/差异；任何失败不可默认为通过。作者确认复现后再自行决定投稿，本包不投稿。"),C('figures_py=sorted((ROOT/"figures/python").glob("Figure*.png"))\nfigures_r=sorted((ROOT/"figures/R").glob("Figure*.png"))\nassert len(figures_py)==len(figures_r)==12\nprint("Python/R各12图；核对:",report["status"])\ndisplay(pd.read_csv(ROOT/"docs/20261030_FIGURE_TABLE_MAP.csv"))')]
    write('20261030_03_Independent_R_and_Audit.ipynb',c3)
    (ROOT/'docs/20261030_FIGURE_LEARNING_GUIDE.json').write_text(json.dumps(guide,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Created three clean notebooks with twelve actual paper plotting cells.')
if __name__=='__main__':main()

