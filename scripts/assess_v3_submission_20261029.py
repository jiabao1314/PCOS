#!/usr/bin/env python3
"""Record a targeted literature/journal assessment and read-only format checks.

Literature and publisher URLs were actually opened during this Codex session;
this script does not pretend to execute those web searches or rerun statistics.
The original classification workbook is retained privately, never republished.
"""
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'PCOS_v3_Submission_Assessment_2026-10-29'
V3=ROOT/'PCOS_Revision_2026-10-29_v3'


def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():raise RuntimeError('Preserve dated assessment; output directory already exists.')
    OUT.mkdir()
    text=(V3/'manuscript/main.tex').read_text()
    abstract=text.split(r'\begin{abstract}')[1].split(r'\end{abstract}')[0]
    cleaned=re.sub(r'\\(?:cite|ref|label|url|href)\{[^}]*\}','',abstract)
    cleaned=re.sub(r'\\[a-zA-Z]+\*?(?:\[[^]]*\])?',' ',cleaned)
    checks=dict(abstract_words_approx=len(re.findall(r"[A-Za-z0-9]+(?:[-’'][A-Za-z0-9]+)*",cleaned)),
                word_count_method='TeX command stripping and tokenization; approximate, not a submission-system count',
                main_figures=len(re.findall(r'\\label\{fig:',text)),main_tables=len(re.findall(r'\\label\{tab:',text)),
                references=len(re.findall(r'\\bibitem',text)),reproductive_health_draft_header='Reproductive Health draft' in text,
                figure_alt_text_present='Alt text:' in text,HR_extended_study_question_heading='STUDY QUESTION' in text,
                four_part_abstract=all(x in abstract for x in ['Background:','Methods:','Results:','Conclusions:']),
                dedicated_cover_letter_in_v3=any('cover' in p.name.lower() for p in V3.rglob('*') if p.is_file()),
                intentionally_preserved_XX='XX Author' in text,
                source_manuscript_sha256=digest(V3/'manuscript/main.tex'),
                existing_scientific_audit=json.loads((V3/'docs/claim_audit.json').read_text())['all_claims_pass'],
                original_v3_files_modified=False,new_statistical_analysis=False)
    dump(OUT/'MANUSCRIPT_READINESS_CHECKS.json',checks)
    # Read the original workbook without modifying it or relying on an ephemeral extract.
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    wanted={'HUMAN REPRODUCTION','FERTILITY AND STERILITY','BMC MEDICINE','ECLINICALMEDICINE',
            'PLOS MEDICINE','REPRODUCTIVE HEALTH','INTERNATIONAL JOURNAL OF EPIDEMIOLOGY',
            'EUROPEAN JOURNAL OF EPIDEMIOLOGY','JOURNAL OF CLINICAL EPIDEMIOLOGY',
            'HUMAN REPRODUCTION UPDATE','REPRODUCTIVE BIOLOGY AND ENDOCRINOLOGY'}
    ranks=[]
    with ZipFile(ROOT/'sources/journal_audit/CAS2025_NCEPU_public_archive.xlsx') as z:
        strings=[''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)]
        for row in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//m:row',ns):
            cells=[]
            for c in row.findall('m:c',ns):
                v=c.find('m:v',ns);value=v.text if v is not None else None
                if value is not None and c.get('t')=='s':value=strings[int(value)]
                cells.append([c.get('r'),value])
            if any((value or '').upper() in wanted for _,value in cells):ranks.append(dict(row=row.get('r'),cells=cells))
    assert len(ranks)==11
    dump(OUT/'CAS2025_CANDIDATE_ROWS.json',dict(source='University-hosted archived 2025 upgraded CAS classification; not a live CAS certificate',
         source_url='https://cce.ncepu.edu.cn/xzzx/yjsjx1/7632005045644e61a0d12c7bbeff6204.htm',
         source_sha256=digest(ROOT/'sources/journal_audit/CAS2025_NCEPU_public_archive.xlsx'),rows=ranks))
    journals=[
        dict(journal='Human Reproduction',ISSN='0268-1161',CAS2025_major='医学1区',priority='First conditional stretch target',
             fit='PCOS-related infertility and reproductive epidemiology; the journal published the direct GBD-PCOS predecessor',
             risk='Incremental application, no joint posterior uncertainty, indirect clinical implications',
             requirements_verified=['General preparation, alt text, continuous lines, top-right page numbers, cover letter rationale, ORCID/signatures','Online-submission guidance discourages relying on unconverted LaTeX'],
             requirements_unverified=['Dedicated Original Article subpage returned timeout/403; current exact abstract, word, table/figure caps not established']),
        dict(journal='Fertility and Sterility',ISSN='0015-0282',CAS2025_major='医学1区',priority='Second conditional stretch target',
             fit='Official ASRM scope covers infertility/reproductive research',
             risk='Clinical/laboratory emphasis makes a benchmark-measurement study a less direct fit',
             requirements_verified=['ASRM official journal scope'],
             requirements_unverified=['Publisher author-guide URLs returned 403; exact current length, abstract, figure/table and fee rules not verified']),
        dict(journal='BMC Medicine',ISSN='1741-7015',CAS2025_major='医学1区',priority='Not recommended for current v3',
             fit='Official scope includes public/global health and influential general-medical research',risk='Current single-disease, one-index-country descriptive contribution has limited broad clinical/public-health impact'),
        dict(journal='EClinicalMedicine',ISSN='2589-5370',CAS2025_major='医学1区',priority='Not recommended for current v3',
             fit='Classification checked only this round',risk='Not shortlisted for current manuscript; author requirements not checked'),
        dict(journal='Reproductive Health',ISSN='1742-4755',CAS2025_major='医学2区',CAS2025_minor='公共卫生1区',priority='More realistic scope-aligned fallback; not a major-category Q1 target',
             fit='Official scope emphasizes global reproductive health; current v3 follows its general format',risk='Still needs a convincing substantive measurement question and honest uncertainty reporting'),
        dict(journal='International Journal of Epidemiology',ISSN='0300-5771',CAS2025_major='医学2区',CAS2025_minor='公共卫生1区',priority='Alternative methodological/educational route only if minor-category Q1 is acceptable',
             fit='Education Corner provides a possible reframing; not an unchanged original-research resubmission',risk='Requires a broadly reusable teaching contribution; generalization should not be asserted from one case'),
        dict(journal='European Journal of Epidemiology',ISSN='0393-2990',CAS2025_major='医学2区',CAS2025_minor='公共卫生1区',priority='Excluded from strict major-category Q1 shortlist',fit='Classification checked',risk='Not a default rescue target and not major-category Q1')]
    dump(OUT/'JOURNAL_MATRIX.json',journals)
    sources=[
        ('CAS statement','https://las.cas.cn/news/tzgg/202603/t20260327_8178738.html','Opened: official 27 March 2026 discontinuation statement'),
        ('2025 workbook provenance','https://cce.ncepu.edu.cn/xzzx/yjsjx1/7632005045644e61a0d12c7bbeff6204.htm','Opened: university attachment page; existing original workbook hash and candidate cells rechecked'),
        ('Human Reproduction scope','https://academic.oup.com/humrep/pages/about','Opened: publisher scope; current metrics not used as CAS evidence'),
        ('Human Reproduction preparation','https://academic.oup.com/humrep/pages/Manuscript_Preparation','Opened successfully initially; later fetches intermittent timeout'),
        ('Human Reproduction online submission','https://academic.oup.com/humrep/pages/Submission_Online','Opened: Word-oriented instructions and discouraged automatic LaTeX handling; page contains legacy details, so reconfirm in live submission system'),
        ('HR direct predecessor','https://academic.oup.com/humrep/article/39/1/108/7452815','Opened: Liu et al., 2024, DOI 10.1093/humrep/dead241; author article text'),
        ('Existing PCOS burden decomposition','https://www.frontiersin.org/journals/public-health/articles/10.3389/fpubh.2025.1693486/full','Opened publisher article and PMC copy; existing case-count decomposition'),
        ('RBMO trend study','https://pubmed.ncbi.nlm.nih.gov/41456540/','Existing v3 targeted verification reused; new PubMed retrieval was partially unavailable; no new full-text access claimed'),
        ('2026 GBD infertility overlap','https://link.springer.com/article/10.1186/s10020-026-01548-8','Opened publisher article/abstract, July 2026; newer GBD burden/causes/decomposition already covered'),
        ('ASRM scope','https://www.asrm.org/journals/','Opened official society scope for Fertility and Sterility'),
        ('BMC Medicine scope','https://link.springer.com/journal/12916/aims-and-scope','Opened publisher scope'),
        ('Reproductive Health scope','https://link.springer.com/journal/12978/aims-and-scope','Opened publisher scope'),
        ('Reproductive Health research instructions','https://link.springer.com/journal/12978/submission-guidelines/research','Opened: abstract 350, plain summary 250, declarations and restricted-data availability options'),
        ('IJE instructions','https://academic.oup.com/ije/pages/General_Instructions','Search tool returned official full instructions including Education Corner; no role as major-category Q1 claimed')]
    dump(OUT/'EVIDENCE_SOURCES.json',dict(checked_on='2026-10-29',timezone='Europe/Paris',scope='Targeted primary-source review, not a systematic review or a verified acceptance prediction',
         sources=[dict(label=a,url=b,access=c) for a,b,c in sources],
         access_limits=['HR dedicated Original_Article subpage could not be retrieved','Fertility and Sterility author-guide endpoints returned 403','No current APCs or editorial acceptance probabilities established'],
         ranking_rule='2025 upgraded CAS major category used conservatively; third-party 2026 lists and JCR Q1 are separate systems'))
    report=r'''# PCOS v3 创新性、一区竞争力与投稿前修改评估

核验日期：2026年10月29日，Europe/Paris。对象：`PCOS_Revision_2026-10-29_v3`。本轮是论文/文献/选刊评估，不重跑GBD统计，不修改v3，也未外发咨询或投稿。以下期刊顺序和新增修改均为建议，尚不视作用户选定期刊或已执行的新科研决定。

## 结论与建议路线

v3具有清楚的应用性增量、较强的计算可复核性，可以作为有初筛风险的一区冲刺稿；目前还不能评价为强势一区原始研究。最有价值的贡献是说明：即使年龄权重固定，跨国合并参照的年龄内国家份额改变，仍会改变中国减参照的率差及其变化；不同参照定义可能使一个接近零的点估计出现不同符号。

如果目标严格限定为**2025中科院医学大类一区**，建议在下述必改项完成后，以 **Human Reproduction 为第一冲刺，Fertility and Sterility 为第二条件性冲刺**。两者都存在较高初筛风险，不提供没有可靠依据的录用概率。若前者意见集中于增量/意义不足，不应只换刊而原样继续投。

如果优先考虑现有证据与受众匹配，**Reproductive Health 更现实，但属于医学大类二区、公共卫生小类一区**。这条路线不能被包装为大类一区。IJE/EJE同样是本次2025数据中的医学大类二区、公共卫生小类一区。

## 分区口径与已核实期刊

中科院文献情报中心2026年3月27日[正式声明](https://las.cas.cn/news/tzgg/202603/t20260327_8178738.html)：2026年起不再更新发布，其他机构分区与其无关。本报告使用已存档的2025升级版，重新核验原件SHA-256和单刊所在单元格；原件来自[华北电力大学附件页](https://cce.ncepu.edu.cn/xzzx/yjsjx1/7632005045644e61a0d12c7bbeff6204.htm)。这是公开高校存档核对，不是新开具的官方分区证明；单位对大类/小类及采用年份的认定仍以其制度为准。

| 期刊 | 2025大类及原表行 | 对v3的建议 | 主要理由与风险 |
|---|---|---|---|
| Human Reproduction，0268-1161 | 医学1区，281行 | 第一条件性冲刺 | [范围](https://academic.oup.com/humrep/pages/about)与生殖流行病学相符，且已刊载直接相关PCOS-GBD研究。主题可进入编辑视野，但必须证明相对既有研究的新增意义。 |
| Fertility and Sterility，0015-0282 | 医学1区，271行 | 第二条件性冲刺 | [ASRM官方范围](https://www.asrm.org/journals/)覆盖不孕和生殖研究；临床/实验研究导向使本稿的参照测量问题较间接。当前作者指南受403限制，不能宣称已完成该刊格式适配。 |
| BMC Medicine，1741-7015 | 医学1区，181行 | 当前不优先 | [官网](https://link.springer.com/journal/12916/aims-and-scope)强调有影响力的广泛医学及公共卫生研究。现稿的可推广性和实际决策后果不足以支持优先冲刺。 |
| EClinicalMedicine，2589-5370 | 医学1区，248行 | 当前不优先 | 本轮只核实分区；未为其核对作者细则。不能仅按分区将其列为现实首投。 |
| Reproductive Health，1742-4755 | 医学2区/公共卫生1区，2319行 | 匹配度较高的备选 | [范围](https://link.springer.com/journal/12978/aims-and-scope)贴近全球生殖健康，v3已有相应基本结构；不是大类一区。 |
| International Journal of Epidemiology，0300-5771 | 医学2区/公共卫生1区，2015行 | 小类一区认可时，可另拟方法教育稿 | 原稿不能直接按新算法论文转投；需要可推广的解释框架、清楚的教学例子和实际使用场景。 |
| European Journal of Epidemiology，0393-2990 | 医学2区/公共卫生1区，1923行 | 不列入严格大类一区路线 | 不能用旧年份或小类一区替代大类一区。 |

本轮没有核实APC、付费减免、审稿时长或录用率，不以第三方宣传作承诺。Human Reproduction Update虽然分区高，其综述定位也不适合将本稿原始二次分析直接投过去。

## 创新性：新增了什么，还缺什么

**有价值的部分。** 该稿将“指数国率变化、参照国率变化、参照国国家份额变化”分开，并明确动态、固定1990和等国家基准是不同描述性估计目标。58.5%是有符号净变化的会计比例，39.8%–67.9%是特定敏感性设定范围；这些限定提高了可信度。UN替换人口份额、独立重构及表图比对是可靠性与可复现性优势。

**方法创新有限。** 分解用的是经典Kitagawa型恒等式；“更换权重会更换加权率”本身是可预期的数学性质。新GBD年份、新国家组合、原发/继发分层或增加方法数量不能单独构成强创新。28项主张、1488核心行及1440敏感行通过核验，支持计算可信，却不能转换成新机制、因果证据或高临床影响力。

**竞争文献已拥挤。** [Liu等，Human Reproduction 2024](https://academic.oup.com/humrep/article/39/1/108/7452815)已研究PCOS归因不孕负担；[Liang等，Frontiers 2025](https://www.frontiersin.org/journals/public-health/articles/10.3389/fpubh.2025.1693486/full)已做趋势和病例数负担分解；[Wang等，Molecular Medicine 2026](https://link.springer.com/article/10.1186/s10020-026-01548-8)已经涉及GBD2021/2023不孕病因、分型、分解与预测。因此应突出参照构成及估计目标这一具体问题，避免“首次趋势分析/首创分解/GBD2023本身创新”。本轮是定向检索，未建立足以声称全球首次的系统文献证据。

**一区最可能提出的三个问题。**

1. 这是一个已知加权恒等式的个案，为什么值得生殖医学读者关注？目前需要更具体的监测、跨国比较或研究解释场景。
2. 没有联合后验draws时，58.5%、接近零的+2.26及其方向有多不确定？数值重算一致不能回答这一问题。
3. 为什么是中国与18个G20国家？不同估计目标产生不同符号，可能只是定义变化，不能据此声称发现真实临床风险反转。

没有联合UI并不自动否定一篇测量问题研究，但限制了它作为实证临床/人群比较Original Research的竞争力；若按方法教育方向重构，数学解释可以成立，经验数值仍必须保留条件性。

## 投稿前必须完成的科学及写作修改（建议，尚未执行）

| 优先级 | 需要修改 | 具体实施及验收标准 |
|---|---|---|
| P0 | 将主张收紧到实际被证明的范围 | 结论明确针对“年龄内按人口合并的多国参照”；不扩大为“年龄标化失效”或一般单国年龄标化率有偏。选定主估计目标，其余基准标作回答其他问题。 |
| P0 | 证明参照构成问题在实际研究解释中有用 | 背景增加一张简短的前人研究/参照定义对照，逐篇查它们是否真正使用本文这种pooling；不能把只比较单国ASPR的论文误判为犯同类问题。给出一段具体读者行动：先固定比较问题，再选择权重，并同时报告绝对分解。 |
| P0 | 处理“数学演示”和“疾病事实”的证据层级 | 方法命题与条件于GBD点估计的经验发现分开；+2.26不能作为已确定高于参照的证据，58.5%不能写作疾病解释比例。继续说明无联合draws，不能拼边际UI或用国家bootstrap补造后验区间。 |
| P0 | 清理与投稿无关的制作历史 | 正文Methods里关于“同日独立editorial revision”的过程叙述转入复现说明/修改记录；保留实际统计方法、计算环境和AI使用披露。 |
| P1 | 让临床/公共卫生意义具体且适度 | 解释基准选择影响跨国监测解读，而非治疗有效性、服务公平因果判断或可避免病例。指出全女性分母与临床备孕人群不同；不为了提升意义加入本稿未估计的结局。 |
| P1 | 强化G20及年龄标准选择的理由 | 明确固定国家集的研究用途与外推边界。利用已有结果解释人口大国影响和15–49归一化；有必要时补PCOS本身的标准化口径对照，避免跨文献绝对率直接比较。此项是建议，不是本轮已计算的新结果。 |
| P1 | 精简不服务主线的内容 | 内异症仅是说明边界的次要例子，可保留在补充；主文优先展示估计目标、绝对分量和基准依赖，减少大段审计过程叙述。无须增加预测、MR或医院模型。 |
| P1 | 增加可推广的使用框架 | 可用既有数据/纯教学例子解释“何时固定年龄权重仍不足、何时份额项为零、固定基准与对称分解为何不同”；教学构造须明确标为说明，不混入真实研究观测。新增计算要另立版本并真实验证。 |

联合draws如果能合法取得，可改善推断，但不能把继续写作无限期卡在不可取得的新数据上。已有医院资料保持独立分支，不要求新增病例、活产或新标志物，也不将医院许可写成伦理审批。

## 已核查到的具体投稿适配缺口

本次只读检查：摘要约261词（TeX剥离命令后估计），主文3表5图，共8项，参考文献12条；仍有`Reproductive Health draft`页眉；没有`Alt text:`图像描述；仍用四段式摘要；v3目录内没有定向cover letter。编译、图表重现和视觉检查已完成，不能将它们重复列为未做。

**若投Human Reproduction：**

- 移除Reproductive Health页眉，按目标刊整理标题页、摘要/正文结构；不要把目前格式当作已经适配HR。
- [官网通用准备说明](https://academic.oup.com/humrep/pages/Manuscript_Preparation)要求主文图像提供alt text，置于相应图注下；v3目前缺少。
- 其通用说明要求连续行号、右上页码；v3行号已连续，但页码在底部，需调整。
- 写定向cover letter，说明研究问题、真正新增发现和对生殖医学领域的意义，并直接回应与该刊2024前作的区别。作者签字/贡献、通讯ORCID等在作者提交阶段完成；本轮不再次追问XX信息。
- [在线投稿说明](https://academic.oup.com/humrep/pages/Submission_Online)仍是Word导向，并提示LaTeX不自动转PDF、因而不推荐。应保留TeX档案，同时准备可编辑投稿文件并核查系统实际接受格式；该页面含旧Word细节，不能据此断言2026系统绝对拒绝TeX。
- Original Article专页多次timeout/403，本轮未确认当前精确字数、摘要和表图上限；不引用未核实的数字作硬性要求。定向版本前需在可访问的正式页面/提交系统补核。

**若投Fertility and Sterility：**已用ASRM官方页面确认范围，但作者指南端点返回403。摘要结构、长度、主文表图上限、声明附件及收费均未完成当前原文核验，不能套用网上旧指南。

**若转Reproductive Health：**[当前Research说明](https://link.springer.com/journal/12978/submission-guidelines/research)的350词摘要、250词通俗摘要及Declarations结构已有基本对应。仍须将数据可用性写成可执行的获取方式：公开汇总与代码的固定版本链接，许可原始数据的准确查询规范及访问限制。个人Drive/Galaxy档案不等于读者可公开获得数据；GitHub已提交代码也不自动等于所有输入可取得。永久归档标识是增强项，本轮未生成DOI，不宣称期刊强制要求某一新平台。

GATHER清单应随最终版本重新核对，尤其是派生定量不确定性仍不完整。伦理适用/豁免必须有责任作者据实确认；保持现有XX，不编造审批、无利益冲突或全体作者同意。

## 执行顺序

1. 先完成P0科学定位与实际使用场景补强，形成独立后续版本；暂不改v3。
2. 若仍坚持大类一区，定向适配Human Reproduction并核实未读取到的Original Article细则；Fertility and Sterility作为下一条件性冲刺。不得同时投稿。
3. 作者审阅是否接受“已有恒等式的有用应用、经验结论仅限点估计”的定位，再决定提交。预投稿咨询可以先准备，但发送须另获用户明确授权。
4. 若主要障碍仍是领域意义与推断证据，优先考虑受众更贴近的Reproductive Health；如果单位接受小类一区，可另讨论IJE的方法教育路线，不把它改叫医学大类一区。

本轮仅形成评估和修改建议，没有新统计结果、没有新投稿稿件、没有外部沟通。证据来源与访问失败记录见`EVIDENCE_SOURCES.json`，单元格证据见`CAS2025_CANDIDATE_ROWS.json`。本报告的评估判断不是编辑部预先意见或录用承诺。
'''
    (OUT/'REPORT_ZH.md').write_text(report)
    provenance=dict(at=datetime.now(ZoneInfo('Europe/Paris')).isoformat(timespec='seconds'),
         task='Targeted v3 novelty, competitiveness, CAS2025 journal and submission-readiness assessment',
         original_v3_unchanged=True,statistical_analysis_rerun=False,
         code_base_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
         assessed_published_commit=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip(),
         code_sha256=digest(Path(__file__)),
         input_sha256={str(p.relative_to(ROOT)):digest(p) for p in [V3/'manuscript/main.tex',V3/'docs/claim_audit.json',ROOT/'sources/journal_audit/CAS2025_NCEPU_public_archive.xlsx']},
         output_sha256={str(p.relative_to(ROOT)):digest(p) for p in OUT.iterdir() if p.is_file()})
    dump(OUT/'ASSESSMENT_PROVENANCE.json',provenance)
    print(json.dumps(dict(report=str(OUT/'REPORT_ZH.md'),files=len(list(OUT.iterdir())),manuscript_checks=checks),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
