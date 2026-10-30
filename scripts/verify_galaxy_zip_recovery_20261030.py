#!/usr/bin/env python3
"""Verify Galaxy recovery of the unchanged historical pilot ZIP.

No source rows or temporary transfer credentials are written to the public report.
"""
from pathlib import Path
from datetime import datetime
import argparse,csv,hashlib,io,json,zipfile
ZIP_SHA='52c7b1a49ff3e352fa98c8cb7480bea4f5dc6c3826b7e5a3eeec414f902c7a8b'
CSV_SHA='ca88e5c17587e8812edd2e84b99166ebff3f705c0e42e5bd1bc6ba5c9c3865d0'
def verify(download,ui_record,output):
    b=Path(download).read_bytes();ui=json.loads(Path(ui_record).read_text())
    assert len(b)==1034 and hashlib.sha256(b).hexdigest()==ZIP_SHA
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        assert z.testzip() is None
        assert set(z.namelist())=={'IHME-GBD_2023_DATA-0daed0e5-1.csv','citation.txt'}
        c=z.read('IHME-GBD_2023_DATA-0daed0e5-1.csv')
        assert len(c)==1654 and hashlib.sha256(c).hexdigest()==CSV_SHA
        rows=list(csv.DictReader(io.StringIO(c.decode('utf-8-sig'))))
        assert len(rows)==8 and {r['location_name'] for r in rows}=={'China'}
        assert {r['age_name'] for r in rows}=={'35-39 years'} and {r['year'] for r in rows}=={'2023'}
    assert ui['original_failed_hid']==8 and ui['original_failed_state']=='error'
    assert ui['original_failed_dataset_id']=='40160950115d555edbcb7f0cbb270400'
    assert ui['new_state']=='ok' and ui['new_hid']>30 and ui['original_failed_record_preserved']
    public_ui={k:v for k,v in ui.items() if k!='downloaded_path'}
    report={'verified_at':datetime.now().astimezone().isoformat(timespec='seconds'),'task':'Recover the original item-8 pilot ZIP as a new Galaxy PCOS dataset, preserving the old failure','official_IHME_redownload_succeeded':False,'official_HTTP_status':403,'method':'Recovery of a previously downloaded original archive, not a new IHME download; private temporary file reference used for Galaxy import','ZIP_bytes':len(b),'ZIP_sha256':ZIP_SHA,'Galaxy_download_full_bytes_match_original_archive':True,'zip_CRC_passed':True,'members':['IHME-GBD_2023_DATA-0daed0e5-1.csv','citation.txt'],'CSV_bytes':len(c),'CSV_sha256':CSV_SHA,'CSV_rows':len(rows),'Galaxy':public_ui,'scientific_inputs_or_manuscript_modified':False,'new_joint_draws':False,'raw_data_published_to_GitHub':False,'submitted':False}
    out=Path(output);assert not out.exists(),'Preserve older verification reports'
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['ZIP_bytes','CSV_rows','Galaxy_download_full_bytes_match_original_archive','official_IHME_redownload_succeeded']}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--download',required=True);p.add_argument('--ui-record',required=True);p.add_argument('--output',required=True);a=p.parse_args();verify(a.download,a.ui_record,a.output)

