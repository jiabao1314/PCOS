"""Read-only OOXML consistency audit; never edits manuscripts or reruns estimates."""
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime
from zoneinfo import ZoneInfo
from lxml import etree as E

ROOT = Path(__file__).resolve().parents[1]
V4 = ROOT / 'PCOS_HumanReproduction_v4_2026-10-29'
OUT = V4 / 'preflight_2026-10-29'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def text(el):
    return ''.join(el.xpath('.//w:t/text() | .//m:t/text()', namespaces=NS))

def read_doc(p):
    with ZipFile(p) as z:
        r = E.fromstring(z.read('word/document.xml'))
        paras = [text(p) for p in r.xpath('//w:body/w:p', namespaces=NS)]
        tables = [[[text(c) for c in row.xpath('./w:tc', namespaces=NS)]
                   for row in t.xpath('./w:tr', namespaces=NS)]
                  for t in r.xpath('//w:tbl', namespaces=NS)]
        headers = [text(E.fromstring(z.read(n))) for n in z.namelist()
                   if re.fullmatch(r'word/header\d+\.xml', n)]
        return dict(path=str(p.relative_to(ROOT)), sha256=sha(p),
                    text='\n'.join(paras), tables=tables, header_text=headers,
                    math_objects=len(r.xpath('//m:oMath', namespaces=NS)),
                    tracked_changes=len(r.xpath('//w:ins|//w:del', namespaces=NS)),
                    comments=len(r.xpath('//w:commentRangeStart', namespaces=NS)))

def main():
    OUT.mkdir(exist_ok=True)
    docs = {k: read_doc(V4 / p) for k, p in {
        'main': 'word_2026-10-29/PCOS_HumanReproduction_v4_Manuscript.docx',
        'supplement': 'word_2026-10-29/PCOS_HumanReproduction_v4_Supplement.docx',
        'cover': 'submission/Cover_Letter.docx',
        'tables': 'submission/Tables.docx'}.items()}
    assert docs['main']['math_objects'] == 52
    assert docs['supplement']['math_objects'] == 4
    assert len(docs['main']['tables']) == 3
    assert len(docs['supplement']['tables']) == 10
    assert all(not d['tracked_changes'] and not d['comments'] for d in docs.values())
    normalize = lambda s: re.sub(r'\s+', '', s)
    for a, b in zip(docs['main']['tables'], docs['tables']['tables']):
        assert [[normalize(c) for c in row] for row in a] == [[normalize(c) for c in row] for row in b]
    for val in ['151.54', '88.65', '271.51', '208.62', '86.76']:
        assert val in docs['main']['text'] and val in docs['cover']['text'], val
    title = docs['main']['text'].splitlines()[0]
    assert title in docs['cover']['text']
    assert len(title.split()) == 13
    assert 'PCOS infertility and reference composition' not in docs['main']['text'] + ''.join(docs['main']['header_text'])
    qc = json.loads((V4 / 'word_2026-10-29/FINAL_CONVERSION_QC.json').read_text())
    for k, name in [('main','main'), ('supplement','supplement')]:
        assert docs[k]['sha256'] == qc['documents'][name]['sha256']
    preserved = json.loads((V4 / 'word_2026-10-29/SOURCE_PRESERVATION.json').read_text())
    assert all(sha(ROOT / p) == h for p, h in preserved.items())
    result = dict(checked_at=datetime.now(ZoneInfo('Europe/Paris')).isoformat(timespec='seconds'),
        task='Final consistency and journal-requirements audit; no manuscript edits; no submission',
        scientific_analysis_rerun=False, source_v4_files_unchanged=len(preserved),
        numerical_claims_consistent=True, separate_main_tables_match_including_math=True,
        title_words=13, missing_running_title_in_word=True,
        native_math_objects=56, prior_all_40_page_visual_qa_reused_after_hash_verification=True,
        visual_recheck_this_turn={'main':[1,5,6,14], 'supplement':[20], 'cover':[1]},
        documents={k:{kk:vv for kk,vv in d.items() if kk not in ['text','tables']} for k,d in docs.items()},
        source_cloud_verification=json.loads((ROOT/'.shared_context_runtime/hr_v4_preflight/source_cloud.json').read_text()),
        assessment='Content consistent; not ready to submit before technical corrections and author declarations',
        corrections=['Add the 42-character running title to Word title page',
          'Expand AI disclosure with real tool names/versions, purposes and human oversight; cover letter and Acknowledgements',
          'Complete dataset citations and explicit immutable code/results URL',
          'Remove internal production and user-request wording from supplementary submission copy'],
        portal_upload_and_consolidated_proof_checked=False, submitted=False)
    (OUT/'AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'audit':'passed consistency checks; corrections remain','source_v4_files_unchanged':len(preserved),'submitted':False}))

if __name__ == '__main__':
    main()
