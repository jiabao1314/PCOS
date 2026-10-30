#!/usr/bin/env python3
"""Verify a Galaxy raw-data collection without displaying restricted source cells."""
from pathlib import Path
import argparse,hashlib,json,zipfile
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check_collection(root):
    root=Path(root)
    manifest=json.loads((root/'docs/20261030_RAW_COLLECTION_MANIFEST.json').read_text(encoding='utf-8'))
    for r in manifest['files']:
        p=root/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
    inputs=json.loads((root/'docs/input_manifest.json').read_text(encoding='utf-8'))
    for rel,r in inputs.items():
        p=root/rel;assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],rel
    assert sha(root/'data/original_downloads/WPP2024_PopulationByAge5GroupSex_Medium.csv.gz')=='a04d7d1486a5eb2832cc812d599448f0a71e8ac9e1e7e6fa4066673d6a2487cd'
    assert sha(root/'history_pilot/IHME-GBD_2023_DATA-0daed0e5-1.zip')=='52c7b1a49ff3e352fa98c8cb7480bea4f5dc6c3826b7e5a3eeec414f902c7a8b'
    assert sha(root/'history_pilot/IHME-GBD_2023_DATA-0daed0e5-1.csv')=='ca88e5c17587e8812edd2e84b99166ebff3f705c0e42e5bd1bc6ba5c9c3865d0'
    return {'canonical_paper_inputs_verified':len(inputs),'collection_files_verified':len(manifest['files']),'original_UN_gzip_verified':True,'original_pilot_ZIP_and_CSV_verified':True}
def check_roundtrip(download,original,collection):
    download,original=Path(download),Path(original);assert download.read_bytes()==original.read_bytes()
    with zipfile.ZipFile(download) as z:
        assert z.testzip() is None
        for name in z.namelist():
            rel=Path(name);assert not rel.is_absolute() and '..' not in rel.parts and rel.parts[0]=='20261030_PCOS_Original_Data'
            assert z.read(name)==(Path(collection)/Path(*rel.parts[1:])).read_bytes(),name
        n=len(z.namelist())
    return {'Galaxy_download_bytes':download.stat().st_size,'Galaxy_download_sha256':sha(download),'archive_members_verified':n,**check_collection(collection)}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--collection',required=True);p.add_argument('--download');p.add_argument('--original');p.add_argument('--output')
    a=p.parse_args();r=check_roundtrip(a.download,a.original,a.collection) if a.download else check_collection(a.collection)
    if a.output:Path(a.output).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(r,ensure_ascii=False))

