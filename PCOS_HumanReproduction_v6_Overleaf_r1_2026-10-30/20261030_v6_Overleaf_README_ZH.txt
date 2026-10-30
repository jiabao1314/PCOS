Overleaf v6技术编译修复r1，2026-10-30

两份论文.tex为可单独编译、自包含的普通源文档；原v5、原v6、原Overleaf导入版均保留。只对编译依赖与S11跨页标签作技术修复，正文、7个编号公式、表值、XX、无合格draws限制均保留。12幅图复用固定科研快照中的汇总CSV与原figures函数，输出原生PGF路径/文字并直接内联论文TeX；不含位图/PDF编码、占位图或外部资源依赖。图形字体随TeX后端有技术性差异，绘图数据不变。

Overleaf项目：https://www.overleaf.com/project/6adda2876e26d2e60e482e89 。新增仅两份.tex，通过New file及源码编辑器写入，而非不可作本项目主文档候选的URL导入blob。XeLaTeX/TeX Live 2026：主稿19页，补充21页，均Errors 0、Warnings 0；仍有4/23条Underfull排版Info，目视无裁切。两份TeX通过Download回下载逐字节和SHA256一致。默认主文档及最终打开项为主稿；补充稿可打开单独编译。

本地Tectonic交叉编译两稿通过；40页已渲染，29个变化页逐页查看、11个像素相同页沿用先前完整目检，另核对S11续页。云端全部页正文机器比较，主稿排除左侧行号后逐页同文，补充逐页全文同文；云端12幅图及S11两页均逐页检查。保留本地与云端PDF，output的Cloud.pdf为实际Overleaf下载副本。

本轮无新科学分析、无新数据、无投稿。Overleaf只写两份论文.tex，其他输出仅存Drive/GitHub。构建代码位于scripts/build_hr_v6_overleaf_tex_20261030.py，实际前期命令/错误及最终runner核验在共享CODEX_RUN_LOG中区分记录。

归档兼容说明：GitHub的base64二进制blob接口本轮返回Internal error，UTF-8接口可用。分发PDF采用PDF规范ASCIIHexDecode对原PDF流无损重编码（文件仍为有效PDF），文件名带_ASCII；所有页文本和72dpi像素逐页一致。ASCII-PDF和论文TeX/代码/核验记录均存Drive与GitHub；原始Tectonic输出及Overleaf下载的二进制PDF另保留本机和Drive档案，其原始SHA256仍在核验记录。未将PDF或图片内容嵌入TeX；Overleaf只有两份正常论文.tex。
