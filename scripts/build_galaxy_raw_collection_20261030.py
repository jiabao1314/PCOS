#!/usr/bin/env python3
"""Audit Galaxy downloads and build a private, byte-preserving raw-data collection."""
from pathlib import Path
import argparse,csv,gzip,hashlib,io,json,shutil,zipfile
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'.shared_context_runtime/galaxy_all_raw_20261030'
SCI=ROOT/'PCOS_Revision_2026-10-29'
DESK=Path.home()/'Desktop/20261030_PCOS论文复现包'
BUNDLE=P/'20261030_PCOS_Original_Data'
DELIVERY=DESK/'20261030_论文全部原始数据_已核验'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cp(s,d):
    d.parent.mkdir(parents=True,exist_ok=True)
    if d.exists():assert d.read_bytes()==s.read_bytes(),str(d)
    else:shutil.copyfile(s,d)
def dump(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def build():
    rs=json.loads((P/'readbacks_private.json').read_text());by={r['hid']:r for r in rs};assert len(by)==14
    inputs=json.loads((SCI/'docs/input_manifest.json').read_text());rows=[]
    # Capture old desktop files before adding the new dated folder.
    old={str(p.relative_to(DESK)):sha(p) for p in DESK.rglob('*') if p.is_file() and p.name!='.DS_Store' and DELIVERY.name not in p.parts}
    dump(P/'desktop_baseline.json',old)
    for r in rs:
        p=Path(r['download_path']);b=p.read_bytes();assert 'alert-success' in r['UI_class']
        row={k:r[k] for k in ['hid','id','name','role','state']};row.update(bytes=len(b),sha256=sha(p))
        if r['role']=='core_input':
            e=inputs['data/input/'+r['name']]
            if r['hid']==28:
                original=(SCI/'data/input'/r['name']).read_bytes();assert b==original+b'\n' and json.loads(b)==json.loads(original)
                out=BUNDLE/'data/input'/r['name'];out.parent.mkdir(parents=True,exist_ok=True)
                if out.exists():assert out.read_bytes()==original
                else:out.write_bytes(original)
                row['comparison']='JSON identical; Galaxy appended one terminal LF. Canonical input restores the original 970 bytes; unmodified Galaxy copy retained separately.'
            else:
                assert len(b)==e['bytes'] and sha(p)==e['sha256'];cp(p,BUNDLE/'data/input'/r['name']);row['comparison']='byte-identical paper input'
        rows.append(row)
    for rel,e in inputs.items():assert (BUNDLE/rel).stat().st_size==e['bytes'] and sha(BUNDLE/rel)==e['sha256']
    # Original UN gzip is compared with the full Galaxy table after exactly the
    # decompression/CRLF-to-LF transformation performed by Galaxy.
    gz=SCI/'private/WPP2024_PopulationByAge5GroupSex_Medium.csv.gz'
    source=json.loads((SCI/'data/input/UN_WPP2024_source_manifest.json').read_text())
    assert gz.stat().st_size==source['source_bytes'] and sha(gz)==source['source_sha256']
    h=hashlib.sha256();n=0;carry=b''
    with gzip.open(gz,'rb') as f:
        while True:
            b=f.read(1024*1024)
            if not b:break
            b=carry+b;carry=b'\r' if b.endswith(b'\r') else b'';b=b[:-1] if carry else b;b=b.replace(b'\r\n',b'\n');h.update(b);n+=len(b)
        if carry:h.update(carry);n+=len(carry)
    g=Path(by[26]['download_path']);assert n==g.stat().st_size and h.hexdigest()==sha(g)
    cp(gz,BUNDLE/'data/original_downloads'/gz.name)
    for row in rows:
        if row['hid']==26:row['comparison']='Exact full original UN source after gzip decompression and CRLF-to-LF conversion; original gzip preserved byte-for-byte in the new collection.'
    # Restore all four original official GBD ZIPs as well as their CSVs.
    raw_manifest=json.loads((ROOT/'docs/raw_manifest.json').read_text())['files']
    for e in raw_manifest:
        p=ROOT/e['path']
        if p.suffix!='.zip' or '0daed0e5' in p.name:continue
        assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
        with zipfile.ZipFile(p) as z:
            assert z.testzip() is None
            data=[x for x in z.namelist() if x.endswith('.csv')];assert len(data)==1
            assert z.read(data[0])==(BUNDLE/'data/input'/Path(data[0]).name).read_bytes()
        cp(p,BUNDLE/'data/original_downloads'/p.name)
    for hid in [13,31]:
        cp(Path(by[hid]['download_path']),BUNDLE/'history_pilot'/by[hid]['name'])
    for hid in [28,29,30]:
        cp(Path(by[hid]['download_path']),BUNDLE/'Galaxy_preserved_variants'/('Galaxy'+str(hid)+'_'+by[hid]['name']))
    cp(SCI/'docs/input_manifest.json',BUNDLE/'docs/input_manifest.json')
    cp(SCI/'docs/DATA_ACQUISITION.md',BUNDLE/'docs/DATA_ACQUISITION.md')
    cp(SCI/'code/extract_wpp2024.py',BUNDLE/'code/extract_wpp2024.py')
    re=json.loads((P/'UN_subset_reextraction.json').read_text())
    assert re['subset_sha256']==inputs['data/input/UN_WPP2024_G20_female_15_49_1990_2023.csv']['sha256']
    dump(BUNDLE/'docs/20261030_UN_source_reextraction.json',re)
    note="""PCOS论文完整原始数据 — 2026-10-30

data/input为论文直接使用的7个输入，文件名和字节符合原input_manifest。
data/original_downloads包含4份原始IHME下载ZIP和完整UN WPP2024原始csv.gz。
history_pilot为历史8行试下载的CSV和原ZIP，非正式主分析输入。
Galaxy_preserved_variants保留Galaxy原样的来源JSON和重复UN子集。

Galaxy第26条完整UN表已回读核对，内容与原始gzip一致；Galaxy自动解压并将CRLF转换成LF，因此存储字节不同。本合集同时保留未经重压缩的原始gzip。
Galaxy第28/30条来源JSON只比论文原文件多一个末尾换行，JSON内容相同。data/input提供原970字节输入以通过论文严格SHA256检查，原样971字节副本另外保留；没有改变任何人口或疾病数值。
完整UN原源已重新抽取出4522行，与论文UN子集SHA256一致。
这是既有原始数据的核验/恢复合集，不是新IHME导出；不改变论文、XX、draws限制或投稿状态。
将data/input内7个文件用于既有复现包的data/input。许可GBD原始数据仅供合法研究复现，不上传公开GitHub。
Galaxy核验及红色失败条目处理以随附最终核验记录为准；不把queued/running当成功。
"""
    (BUNDLE/'20261030_先看这里.txt').write_text(note,encoding='utf-8')
    filelist=[{'path':str(p.relative_to(BUNDLE)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(BUNDLE.rglob('*')) if p.is_file() and p.name!='20261030_RAW_COLLECTION_MANIFEST.json']
    dump(BUNDLE/'docs/20261030_RAW_COLLECTION_MANIFEST.json',{'files':filelist,'raw_GBD_publication_allowed':False,'source_data_unmodified':True,'format_restorations_explicitly_documented':True})
    archive=P/'20261030_PCOS_Original_Data_COMPLETE_PRIVATE.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(BUNDLE.rglob('*')):
            if p.is_file():z.write(p,str(Path(BUNDLE.name)/p.relative_to(BUNDLE)))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for f in filelist:assert hashlib.sha256(z.read(BUNDLE.name+'/'+f['path'])).hexdigest()==f['sha256']
    for p in BUNDLE.rglob('*'):
        if p.is_file():cp(p,DELIVERY/p.relative_to(BUNDLE))
    for hid,source_file in [(14,ROOT/'sources/GBD2023_world_standard_reproduced.docx'),(17,ROOT/'sources/GBD2023_methods_appendix1.pdf')]:
        p=Path(by[hid]['download_path']);assert p.read_bytes()==source_file.read_bytes();cp(p,DELIVERY/'sources'/by[hid]['name'])
    cp(archive,DESK/archive.name)
    assert all(sha(DESK/p)==s for p,s in old.items())
    report={'checked_at':datetime.now().astimezone().isoformat(timespec='seconds'),'Galaxy_history_id':'11ac94870d0bb33ad5abd2b59708ab6e','Galaxy_successful_records_downloaded':14,'files':rows,'numerical_core_inputs_byte_identical':6,'metadata_JSON_content_identical':True,'all_seven_canonical_input_hashes_verified':True,'UN_full_source_original_gzip_sha256':sha(gz),'UN_full_source_original_gzip_bytes':gz.stat().st_size,'Galaxy26_full_source_CSV_bytes':n,'Galaxy26_full_source_CSV_sha256':h.hexdigest(),'UN_subset_reextraction_matches':True,'UN_subset_rows':4522,'original_GBD_provider_ZIPs_preserved':4,'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'archive_members':len(filelist)+1,'collection_Galaxy_roundtrip':'pending','old_failed_hid8_action':'pending complete collection verification; user subsequently authorized recoverable deletion only','original_records_overwritten':False,'old_desktop_file_hashes_preserved':len(old),'scientific_analysis_rerun':False,'paper_changed':False,'submitted':False}
    dump(P/'preupload_audit.json',report)
    print(json.dumps({k:report[k] for k in ['Galaxy_successful_records_downloaded','all_seven_canonical_input_hashes_verified','UN_subset_reextraction_matches','archive_bytes','archive_sha256','archive_members','old_desktop_file_hashes_preserved']},ensure_ascii=False))
if __name__=='__main__':build()

