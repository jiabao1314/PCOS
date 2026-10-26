from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'sources/external_validation';out.mkdir(exist_ok=True)
items=[('NSFG2022_2023_FemResp.zip','https://ftp.cdc.gov/pub/Health_Statistics/NCHS/NSFG/NSFG-2022-2023-FemRespPUFData.zip'),('NSFG2022_2023_codebook.pdf','https://www.cdc.gov/nchs/data/nsfg/codebooks/2022-2023-NSFG-FemRespPUFCodebook.pdf'),('NSFG2022_2023_recode.pdf','https://www.cdc.gov/nchs/data/nsfg/recodespecs/2022-2023-NSFG-FemResp-RecodeSpecs.pdf'),('NSFG2022_2023_variance.pdf','https://www.cdc.gov/nchs/data/nsfg/varest/2022-2023-NSFG-VarEst-all.pdf'),('NSFG2022_2023_design_variables.pdf','https://www.cdc.gov/nchs/data/nsfg/varest/2022-2023-NSFG-DesignandWeightVariables.pdf'),('NSFG2022_2023_userguide.pdf','https://www.cdc.gov/nchs/data/nsfg/guidefaqs/NSFG-2022-2023-UsersGuide-revJuly2025.pdf'),('CDC_Health_Estat121.pdf','https://www.cdc.gov/nchs/data/hestat/hestat121.pdf'),('GBD2023_results_userguide.pdf','https://www.healthdata.org/sites/default/files/2025-10/GBD_Results_Tool_User_Guide_2023.pdf')]
def get(item):
 name,url=item;p=out/name
 try:
  if p.exists():
   b=p.read_bytes()
  else:
   r=requests.get(url,timeout=60);r.raise_for_status();b=r.content
  expected=b'PK' if name.endswith('.zip') else b'%PDF'
  if not b.startswith(expected):raise ValueError('Unexpected content type')
  p.write_bytes(b)
  return dict(file=str(p.relative_to(ROOT)),url=url,date='2026-10-25',bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),status='downloaded')
 except Exception as e:return dict(file=name,url=url,status='failed',error=type(e).__name__)
with ThreadPoolExecutor(max_workers=4) as pool:result=list(pool.map(get,items))
(out/'download_manifest.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
p=out/'NSFG2022_2023_FemResp.zip'
if p.exists():
 with zipfile.ZipFile(p) as z:
  print(z.namelist());z.extractall(ROOT/'data/raw/nsfg_2022_2023')
