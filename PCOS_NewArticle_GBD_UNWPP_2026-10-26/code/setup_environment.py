"""安装复现环境，适用于从完整研究包解压后的目录。来源为PyPI及CRAN。"""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import venv

root=Path(__file__).resolve().parents[1]
env=root/'.venv'
if not env.exists(): venv.EnvBuilder(with_pip=True).create(env)
bindir=env/('Scripts' if os.name=='nt' else 'bin')
python=bindir/('python.exe' if os.name=='nt' else 'python')
subprocess.run([str(python),'-m','pip','install','-r',str(root/'requirements.txt')],check=True)
subprocess.run([str(python),'-m','ipykernel','install','--prefix',str(env),'--name','pcos-newarticle-py','--display-name','PCOS New Article Python'],check=True)
r=shutil.which('Rscript')
if r:
    config=os.environ.copy();config['PATH']=str(bindir)+os.pathsep+config.get('PATH','')
    script="if(!requireNamespace('IRkernel',quietly=TRUE)) install.packages('IRkernel',repos='https://cloud.r-project.org');IRkernel::installspec(prefix=normalizePath('.venv'),name='pcos-newarticle-r',displayname='PCOS New Article R')"
    subprocess.run([r,'-e',script],cwd=root,env=config,check=True)
else:
    print('Rscript尚未安装。Python及Jupyter已就绪；如需R内核，请先从https://cran.r-project.org/安装R，再运行本安装程序。')
print('打开JupyterLab：',bindir/'jupyter','lab',flush=True)
