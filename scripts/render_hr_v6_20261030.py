#!/usr/bin/env python3
"""Render every v6 Word and TeX page for manual inspection; never assert it occurred."""
from pathlib import Path
import concurrent.futures
import hashlib
import importlib.metadata
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT/'PCOS_HumanReproduction_v6_2026-10-30'
PRIVATE = ROOT/'.shared_context_runtime/v6'
SKILL = Path('/Users/wangjiajia/.codex/plugins/cache/openai-primary-runtime/documents/26.1026.10807/skills/documents')
BASE = '20261030_PCOS_HumanReproduction_v6_'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def word(kind):
    source = NEW/'word'/(BASE+kind+'.docx')
    out = PRIVATE/'qa'/('word_'+kind)
    command = [sys.executable,str(SKILL/'render_docx.py'),str(source),'--output_dir',str(out),'--dpi','120','--emit_pdf','--verbose']
    env=os.environ.copy()
    if kind=='CommentResponse':
        env['FONTCONFIG_FILE']=str(PRIVATE/'fontconfig.xml')
    r = subprocess.run(command,cwd=ROOT,capture_output=True,text=True,env=env)
    (PRIVATE/('render_word_'+kind+'.log')).write_text(r.stdout+'\n'+r.stderr)
    assert r.returncode == 0,(kind,r.stderr[-2000:])
    pages = sorted(out.glob('page-*.png'),key=lambda p:int(p.stem.split('-')[-1]))
    assert pages
    return 'word_'+kind,{'input':str(source.relative_to(ROOT)),'input_sha256':sha(source),'pages':len(pages),'pdf':str((out/(source.stem+'.pdf')).relative_to(ROOT)),'png_sha256':{p.name:sha(p) for p in pages},'all_pages_visually_inspected':False,'command':command}


def main():
    (PRIVATE/'qa').mkdir(exist_ok=True,parents=True)
    font=Path('/Users/wangjiajia/Library/Fonts/NotoSansCJKsc-Regular.otf')
    assert font.exists(),'Install or configure a CJK font before rendering the bilingual response'
    fontconfig='''<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig>
<dir>/System/Library/Fonts</dir>
<dir>/System/Library/Fonts/Supplemental</dir>
<dir>/Users/wangjiajia/Library/Fonts</dir>
<dir>/Users/wangjiajia/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/Resources/fonts/truetype</dir>
<cachedir>'''+str(PRIVATE/'fontcache')+'''</cachedir>
</fontconfig>'''
    (PRIVATE/'fontconfig.xml').write_text(fontconfig)
    kinds=['Manuscript','Supplement','CoverLetter','CommentResponse','Tables']
    records={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for name,data in pool.map(word,kinds):records[name]=data
    for kind in ['Manuscript','Supplement','CoverLetter']:
        source=NEW/'output'/(BASE+kind+'.pdf');out=PRIVATE/'qa'/('tex_'+kind);out.mkdir(exist_ok=True)
        doc=pdfium.PdfDocument(str(source));pages=[]
        for i in range(len(doc)):
            p=out/('page-'+str(i+1)+'.png');doc[i].render(scale=120/72).to_pil().save(p);pages.append(p)
        records['tex_'+kind]={'input':str(source.relative_to(ROOT)),'input_sha256':sha(source),'pages':len(pages),'png_sha256':{p.name:sha(p) for p in pages},'all_pages_visually_inspected':False}
    response=PRIVATE/'qa/word_CommentResponse'/(BASE+'CommentResponse.pdf')
    shutil.copy2(response,NEW/'output'/response.name)
    metadata={'rendered_at':datetime.now(ZoneInfo('Europe/Paris')).isoformat(timespec='seconds'),'documents':records,'total_pages_rendered':sum(r['pages'] for r in records.values()),'manual_visual_inspection':'pending','document_python':sys.version,'packages':{n:importlib.metadata.version(n) for n in ['python-docx','pypdf','pypdfium2','Pillow','lxml']}}
    (PRIVATE/'render_inventory.json').write_text(json.dumps(metadata,indent=2))
    (NEW/'docs/20261030_v6_document_environment.json').write_text(json.dumps({k:v for k,v in metadata.items() if k in ['document_python','packages','rendered_at']},indent=2))
    print(json.dumps({k:r['pages'] for k,r in records.items()}))
    print('Total pages rendered:',metadata['total_pages_rendered'])


if __name__=='__main__':main()
