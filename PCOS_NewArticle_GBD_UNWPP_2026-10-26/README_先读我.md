# 新文章组会汇报与完整核心复现包

日期：2026-10-26。本文以链接中最新的 **SubmissionPrep_XX_20261025** 为准，主线为 **GBD 2023＋UN WPP 2024国际参照人口构成**，NSFG不纳入本稿。本目录与旧稿 `PCOS_2026-10-26_continuation` 分开保存，原目录及旧稿未覆盖。

## 师兄先看这些文件

1. `presentation/PCOS_新文章组会汇报_5页_2026-10-26_终版.pptx`：恰好5页，包含研究问题、技术路线、三组主要结果及各1—2句解释。图表和路线对象可编辑，备注中有讲解与来源。
2. `docs/RESULTS_新文章结果说明.md`：结果表、解释、研究边界及结果文件索引。
3. `code/PCOS_NewArticle_complete.py`：一个文件完成Python核心复现，无项目内脚本依赖。
4. `code/PCOS_NewArticle_complete.R`：一个文件完成独立base-R核心复现，不调用Python。
5. `PCOS_NewArticle_Python.ipynb`及`PCOS_NewArticle_R.ipynb`：均含完整代码与实际执行输出，可在JupyterLab逐格运行。
6. `code/ALL_ANALYSIS_CODE_R_Python.txt`：将两种语言的完整源码汇编为单个便于阅读的文件，运行时应选择对应的.py或.R文件。

## 当前电脑已经安装的软件

- Python 3.12.14：独立环境位于本目录的`.venv`。
- JupyterLab 4.6.4，已配置本项目的Python与R两个内核。
- R 4.6.1与RStudio原已安装；本次补装IRkernel 1.3.2用于Jupyter中的R运行。
- Python分析使用NumPy 2.3.5、pandas 2.2.3、Matplotlib 3.10.7，安装清单见`requirements.txt`，完整锁定清单见`requirements.lock.txt`。

本项目的R分析只用base R。运行R脚本不要求安装survey、tidyverse等额外分析包。

## 在当前Mac上运行

双击项目根目录的`01_运行Python分析.command`、`02_运行R分析.command`或`03_打开JupyterLab.command`。Jupyter打开后选择相应Notebook，点击“Run All”。RStudio用户可打开`PCOS_NewArticle.Rproj`，再打开完整.R文件执行。

也可在终端先进入本文件所在目录，然后执行：

```bash
.venv/bin/python code/PCOS_NewArticle_complete.py
Rscript code/PCOS_NewArticle_complete.R
.venv/bin/jupyter lab
```

给另一台电脑使用：先将整个研究包解压，保持目录层级，安装Python 3.11以上版本（推荐3.12）及R，再执行`python3 code/setup_environment.py`。安装程序从PyPI与CRAN安装依赖和内核。`.venv`具有本机路径，不包含在交付ZIP中，需要在新电脑重新建立。当前电脑已经完成安装，无须重复安装。

## 输入、输出与复现范围

`data/input/`保存实际下载的GBD总不孕人数、原发/继发人数、同版人口、端点原始Rate、标准年龄权重和联合国4,522行人口子集。新稿来源与输入SHA-256见`docs/new_article_source_manifest.json`和`docs/input_manifest.json`。原GBD下载说明、查询和上游建模的获取限制仍适用，研究包没有重新生成GBD模型。

新写的两个单文件完整复现本稿**核心比较基准分析**：两病因、三种不孕类型、两种人口来源、34年、三种参照基准、三个终点对称分解、逐国剔除、年度链式分解，以及官方端点Rate复核。Python还输出人口份额TVD及科研图，R输出独立科研图。结果分别写到`results/python`和`results/R`，Notebook输出写到各自的`results/notebook_python`和`results/notebook_R`。

`data/published_expected/`是新稿已发布结果，仅用于计算完成后的逐项复核，不作为生成估计值的输入。若主动修改数据或研究范围，需同步调整固定范围断言及对照表，不能把原稿检查失败隐藏掉。R/Python交叉核对记录见`docs/R_Python_crosscheck.json`。

`source_article/submission/`保留新投稿准备稿的TeX、PDF、Word、高清图及原作者脚本；`source_article/plan_a/`保存其方案A分析档案。新单文件不重算历史预测或上游GBD模型，也不声称重新完成所有历史补充分析。该边界不影响本次PPT中的核心结果复现。

## 解释边界

GBD与UN人口来源下，PCOS参照构成贡献分别为58.5%和57.6%。这衡量带符号率差变化的会计贡献，不代表疾病的生物学病因、医疗效果或可避免负担。UN只替换参照18国年龄内人口份额；疾病率仍由GBD人数及同版人口得到。

联合draws仍未取得，自定义合并率差和分解贡献没有完整GBD后验区间。替代权重范围不是置信区间。UN人口资料不能独立验证PCOS或内异症患病率，二者的上游人口信息也可能部分重叠。内异症2023年跳变仍限制长期解释。所有稿件仍处于作者审核准备阶段，未投稿。

完整本地交付ZIP含已取得的原始GBD输入，供研究复核使用。另有排除GBD原始输入的公共代码结果包；公开平台同步使用公共包。软件环境、临时构建文件和个人认证信息不进入交付包。
