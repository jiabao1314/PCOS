"""Normalize downloaded official CSVs; preserve all original dimensional IDs."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as E
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]

def prepare():
    bfile=next((ROOT/'data/raw/burden_total').glob('*.csv'))
    pfile=next((ROOT/'data/raw/population').glob('*.csv'))
    b=pd.read_csv(bfile).rename(columns={'age_id':'age_group_id','rei_id':'impairment_id','rei_name':'impairment_name'})
    b['gbd_version']='GBD 2023';b['infertility_type']='Total'
    b['age_name']=b.age_name.str.replace(' years','',regex=False)
    b['measure_name']=b.measure_name.replace({'YLDs (Years Lived with Disability)':'YLDs'})
    b.to_csv(ROOT/'data/processed/burden.csv',index=False)
    p=pd.read_csv(pfile).rename(columns={'age_id':'age_group_id','val':'population'})
    p['gbd_version']='GBD 2023';p['age_name']=p.age_name.str.replace(' years','',regex=False)
    p.to_csv(ROOT/'data/processed/population.csv',index=False)
    source=ROOT/'sources/GBD2023_world_standard_reproduced.docx'
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with zipfile.ZipFile(source) as z:
        doc=E.fromstring(z.read('word/document.xml'))
        rows=[[' '.join(t.text or '' for t in c.findall('.//w:t',ns)) for c in r.findall('w:tc',ns)] for r in doc.findall('.//w:tr',ns)]
    ages=json.loads((ROOT/'config/study.json').read_text())['ages']
    weights=pd.DataFrame([{'age_name':a.replace(' years',''),'weight':float(w)} for a,w in rows[1:] if a.replace(' years','') in ages])
    if len(weights)!=7:raise ValueError('Published weight table incomplete')
    weights.to_csv(ROOT/'data/processed/weights.csv',index=False)
    weights.to_csv(ROOT/'docs/standard_weights_used.csv',index=False)
    provenance={'source_type':'Published reproduction of GBD 2023 world standard weights, six decimal places',
      'publication':'Chen et al. PLOS One 2026; doi:10.1371/journal.pone.0351539',
      'table':'S1 Table, supplementary file s002',
      'url':'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0351539.s002&type=supplementary',
      'upstream_citation_reported_by_source':'Gil et al. Lancet Obstet Gynaecol Womens Health 2025;1:e96-e113; doi:10.1016/j.lanogw.2025.100031',
      'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
      'limitation':'Published weights are rounded; original machine-precision IHME weight file was not retrieved. Same published weights applied consistently and normalized within each age range.',
      'restriction_15_49_sum':float(weights.weight.sum())}
    (ROOT/'docs/weights_provenance.json').write_text(json.dumps(provenance,indent=2))
    print('Prepared',len(b),'burden rows,',len(p),'population rows,',len(weights),'published standard weights')

if __name__=='__main__':prepare()
