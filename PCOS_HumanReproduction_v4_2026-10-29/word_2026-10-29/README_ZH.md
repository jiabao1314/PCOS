# Human Reproduction v4 完整 Word 版

2026-10-29。主稿和补充稿各20页（随附核查使用LibreOffice排版；不同Word版本可能自动重分页）。暂未投稿或发送邮件。旧TeX、PDF、附信、完整包及v3均保留。

- PCOS_HumanReproduction_v4_Manuscript.docx：完整主稿，含11栏摘要、正文、12条参考文献、3张可编辑表、5幅原图和Alt text。
- PCOS_HumanReproduction_v4_Supplement.docx：完整补充稿，含方法、GATHER表、S1—S9可编辑表及7幅原图；S9的书目信息与主稿参考文献对应，未凭空增加引文。
- 公式为Word原生OMML，可编辑；共56个数学对象，其中7个原编号公式。作者单位标记用普通上标，不再使用空基数学对象。
- 正文和参考文献双倍行距、连续行号、右上页码；图注/表注及表内文字按可读性设置较紧行距；保留原文措辞与XX。
- CONVERSION_QC.json、VISUAL_QA.json、内容映射及数学回读文件记录逐项核查；SOURCE_PRESERVATION.json记录转换前全部v4文件哈希。

本轮仅转换与排版：空白归一化后全部非数学正文一致；161个表数据行一致；12幅图的嵌入PNG与源文件逐字节一致。没有重新分析GBD、加入医院数据、补造不确定性、修改伦理或作者声明。

转换代码：scripts/convert_hr_v4_word_20261029.py。使用Codex bundled Python、python-docx/lxml及Pandoc 3.13；官方二进制来源与摘要见CONVERSION_PROVENANCE。可用 --pandoc 指定自己的Pandoc路径。build 会重建这个Word输出目录下的Word文件；如需再次制作日期版本，请先复制转换脚本并更换输出目录，保留已归档交付。原始TeX/PDF由脚本只读。

正式投稿时仍需作者完成既定XX、作者签字及真实声明；以投稿系统当日要求选择主文、补充文件、独立Tables.docx及单独图件。此处完整Word已解决前一轮所记的“完整Word未制作”事项，不代表已进入或完成投稿。
