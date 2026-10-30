#!/usr/bin/env python3
"""Read-only input and revision preflight; publish aggregate checks, never source cells."""
import argparse
import ast
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from xml.etree import ElementTree as ET
import zipfile

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCI = ROOT / 'PCOS_Revision_2026-10-29'
V5 = ROOT / 'PCOS_HumanReproduction_v5_2026-10-29'
OUT = ROOT / 'PCOS_Revision_Preflight_2026-10-30'
PRIVATE = ROOT / '.shared_context_runtime/preflight_20261030'
PREFIX = '20261030_'
SNAPSHOT = '1abf337d9f23cc69292e03cd581b6a1557e6effe'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, value):
    (OUT / (PREFIX + name)).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def audit():
    assert not OUT.exists(), 'Use a new revision path; preserve previous outputs'
    OUT.mkdir()
    PRIVATE.mkdir(parents=True, exist_ok=True)
    baseline = {str(p.relative_to(ROOT)): sha(p) for p in V5.rglob('*') if p.is_file()}
    assert baseline
    # Editable working copy is private and is not represented as a finished v6.
    shutil.copytree(V5 / 'manuscript', PRIVATE / 'isolated_v5_manuscript')
    expected = json.loads((SCI / 'docs/input_manifest.json').read_text())
    inputs = {}
    for rel, record in expected.items():
        p = SCI / rel
        assert sha(p) == record['sha256'] and p.stat().st_size == record['bytes'], rel
        inputs[str(p.relative_to(ROOT))] = record
    remote = git('rev-parse', 'origin/main')
    shared = {}
    for p in (ROOT / '00_Shared_Context').iterdir():
        if not p.is_file():
            continue
        committed = subprocess.check_output(['git', 'show', remote + ':' + str(p.relative_to(ROOT))], cwd=ROOT)
        assert committed == p.read_bytes(), p.name
        shared[p.name] = sha(p)
    tracked_v5 = git('ls-tree', '-r', '--name-only', remote, V5.name).splitlines()
    for rel in tracked_v5:
        assert subprocess.check_output(['git', 'show', remote + ':' + rel], cwd=ROOT) == (ROOT / rel).read_bytes(), rel
    save('baseline_manifest.json', {
        'created_at': datetime.now(ZoneInfo('Europe/Paris')).isoformat(timespec='seconds'),
        'scope': 'T00 baseline; T01 source/input audit; T02 bounded access audit; T04 reuse of annual aggregate results',
        'local_head': git('rev-parse', 'HEAD'), 'remote_head_before_work': remote,
        'remote_tree_before_work': git('rev-parse', 'origin/main^{tree}'),
        'scientific_snapshot': SNAPSHOT, 'review_artifact_commit': '38a7e08580e806220c815e9a5ac1e4d62d3871ea',
        'working_tree_dirty': bool(git('status', '--porcelain')),
        'tracked_dirty_paths': git('diff', '--name-only').splitlines(),
        'untracked_files_present': True,
        'v5_all_file_sha256': baseline, 'v5_committed_paths_compared': len(tracked_v5),
        'verified_input_manifest_entries': inputs, 'shared_files_matched_to_remote_commit': shared,
        'private_editable_isolation_created': True, 'v6_created': False,
        'note': 'Local HEAD and existing dirty files retained. Isolation is not a revised manuscript.'})

    source = SCI / 'data/input'
    population = pd.read_csv(source / 'IHME-GBD_2023_DATA-916826fb-1.csv')
    un = pd.read_csv(source / 'UN_WPP2024_G20_female_15_49_1990_2023.csv')
    core = SCI / 'code/PCOS_NewArticle_complete.py'
    tree = ast.parse(core.read_text())
    countries = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'COUNTRIES' for t in n.targets))
    assert len(countries) == len(set(countries)) == 19
    refs = sorted(set(countries) - {'China'})
    assert len(refs) == 18 and 'China' not in refs
    assert set(population.location_name) == set(un.gbd_country) == set(countries)
    pkeys = ['location_name', 'year', 'age_id']
    ukeys = ['gbd_country', 'year', 'age_start']
    assert len(population) == len(un) == 4522
    assert not population.duplicated(pkeys).any() and not un.duplicated(ukeys).any()
    assert set(population.year) == set(un.year) == set(range(1990, 2024))
    assert set(population.age_id) == set(range(8, 15)) and set(un.age_start) == set(range(15, 50, 5))
    assert set(population.sex_id) == {2} and set(population.metric_id) == {1}
    assert (population.val > 0).all() and (un.un_female_pop > 0).all()
    assert np.isfinite(population.val).all() and np.isfinite(un.un_female_pop).all()
    assert np.max(abs(un.un_female_pop - 1000 * un.PopFemale)) < 1e-6
    mapping = un[['gbd_country', 'ISO3_code']].drop_duplicates().sort_values('ISO3_code')
    assert len(mapping) == 19 and mapping.ISO3_code.nunique() == 19
    mapping.assign(reference=mapping.gbd_country.ne('China')).to_csv(OUT / (PREFIX + 'country_reference_mapping.csv'), index=False)

    schemas = []
    frames = {}
    for name in ['1b13e337', '416daf73', '76c5523c']:
        p = source / ('IHME-GBD_2023_DATA-' + name + '-1.csv')
        d = pd.read_csv(p)
        assert not any('draw' in c.lower() for c in d.columns)
        schemas.append({'file': p.name, 'rows': len(d), 'columns': list(d.columns), 'draw_columns': 0, 'sha256': sha(p)})
        frames[name] = d
    total = frames['1b13e337'].query('measure_id == 5 and metric_id == 1 and rei_id == 198 and sex_id == 2').copy()
    total['subtype'] = 'Total'
    strata = frames['416daf73'].query('measure_id == 5 and metric_id == 1 and rei_id in [220,221] and sex_id == 2').copy()
    strata['subtype'] = strata.rei_id.map({220: 'Primary', 221: 'Secondary'})
    d = pd.concat([total, strata])
    keys = pkeys + ['cause_id', 'subtype']
    assert len(d) == 27132 and not d.duplicated(keys).any()
    assert set(d.cause_id) == {605, 607} and (d.val >= 0).all() and np.isfinite(d.val).all()
    pivot = d.pivot(index=pkeys + ['cause_id'], columns='subtype', values='val')
    add_error = float(abs(pivot.Total - pivot.Primary - pivot.Secondary).max())
    assert add_error < 1e-6
    rates = d.merge(population[pkeys + ['val']].rename(columns={'val': 'population'}), on=pkeys, validate='m:1')
    rates['reconstructed_rate'] = rates.val / rates.population * 100000
    endpoint = frames['76c5523c'].query('measure_id == 5 and metric_id == 3 and sex_id == 2 and rei_id in [220,221]').copy()
    endpoint['subtype'] = endpoint.rei_id.map({220: 'Primary', 221: 'Secondary'})
    check = endpoint.merge(rates[keys + ['reconstructed_rate']], on=keys, validate='1:1')
    rate_error = float(abs(check.val - check.reconstructed_rate).max())
    assert len(check) == 1064 and rate_error < 1e-8
    w = pd.read_csv(source / 'weights.csv')
    assert list(w.age_name) == [f'{a}-{a+4}' for a in range(15, 50, 5)] and (w.weight > 0).all()
    doc = ROOT / 'sources/GBD2023_world_standard_reproduced.docx'
    text = ' '.join(ET.fromstring(zipfile.ZipFile(doc).read('word/document.xml')).itertext())
    assert all(f'{x:.6f}' in text for x in w.weight)
    old_qc = json.loads((SCI / 'results/python/qc_summary.json').read_text())
    actual = {n: importlib.metadata.version(n) for n in ['numpy', 'pandas', 'matplotlib']}
    save('source_definition_audit.json', {
        'status': 'input and definition checks verified; original full-precision official age-weight vector not established',
        'countries': 19, 'reference_countries': 18, 'population_cells_each_source': 4522,
        'prevalence_cells_two_causes_three_types': len(d), 'pcos_prevalence_cells': int((d.cause_id == 605).sum()),
        'subtype_cases_additivity_max_absolute_error': add_error,
        'official_endpoint_rate_rows': len(check), 'official_endpoint_rate_max_absolute_error': rate_error,
        'reference_definition': 'Fixed sovereign-country set applied retrospectively to 1990-2023; China excluded; EU and AU not added as countries.',
        'g20_official_evidence': 'https://www.dfat.gov.au/trade/organisations/g20',
        'g20_evidence_accessed': '2026-10-30; official page lists members and establishment in 1999',
        'appendix': {'path': 'sources/GBD2023_methods_appendix1.pdf', 'sha256': sha(ROOT / 'sources/GBD2023_methods_appendix1.pdf'),
                    'article': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC12535840/',
                    'pdf_pages_read': [590,591,592,593,594,685,686,687,688,689,690,691,692,693,694],
                    'pdf_pages_visually_checked': [591,685,686,691],
                    'printed_page_number_offset': 'printed page = one-based PDF page minus 1',
                    'remote_pdf_download_this_run': False,
                    'local_existing_copy_used': True},
        'definitions': [
            {'quantity': 'survey primary infertility', 'definition': 'No livebirth, desire for a child, union at least five years, and no current contraception.', 'pdf_pages': [685,686]},
            {'quantity': 'survey secondary infertility', 'definition': 'Last livebirth more than five years ago, desire for another child, union at least five years, and no current contraception.', 'pdf_pages': [685,686]},
            {'quantity': 'modeled denominator', 'definition': 'Infertility expressed among all females of reproductive age in the general population after sex attribution and exposure modeling.', 'pdf_pages': [686,687]},
            {'quantity': 'clinical input definition', 'definition': 'Clinic case series use twelve months without pregnancy; the appendix separately describes household-survey and clinic definitions.', 'pdf_pages': [685,686,687]},
            {'quantity': 'PCOS model and infertility attribution', 'definition': 'NIH reference definition with crosswalks for alternatives; disease sequela proportions applied to PCOS prevalence, split by primary/secondary envelope proportions, then reconciled with infertility envelopes.', 'pdf_pages': [591,592,691,692,693]}],
        'weights': {'raw': dict(zip(w.age_name, w.weight)), 'raw_sum': float(w.weight.sum()),
                    'normalized_sum': float((w.weight / w.weight.sum()).sum()),
                    'reproduced_docx_sha256': sha(doc), 'seven_values_match_existing_reproduction': True,
                    'provenance': 'Six-decimal published reproduction cited to Chen et al. 2026, DOI 10.1371/journal.pone.0351539 in v5. Not an independently verified full-precision IHME vector.',
                    'decision': 'Retain baseline and existing 128-corner rounding sensitivity; no weight upgrade performed.'},
        'environment': {'original_python_record': old_qc['python'], 'original_R_record': 'R 4.6.1 (2026-06-24), aarch64-apple-darwin23; results/R/R_session_info.txt',
                        'current_audit_python': sys.version, 'current_audit_packages': actual,
                        'original_environment_evidence': ['PCOS_NewArticle_GBD_UNWPP_2026-10-26/docs/software_environment.json', 'PCOS_Revision_2026-10-29/requirements.lock.txt'],
                        'upstream_GBD_fit_reproduced': False},
        'un_role': 'Replace within-age reference shares only; disease rates retain matched GBD population denominators.',
        'un_unit_conversion_verified': True, 'full_UN_Galaxy_archive_status': 'not rechecked; historical running status not promoted to complete',
        'new_research_downloads': False, 'source_data_changed': False})

    annual = pd.read_csv(SCI / 'results/python/all_annual_benchmark_aspr.csv')
    idx = ['cause', 'source', 'benchmark', 'year']
    wide = annual.pivot(index=idx, columns='subtype', values='gap').reset_index()
    assert len(annual) == 1224 and len(wide) == 408 and not wide.isna().any().any()
    assert set(wide.year) == set(range(1990, 2024))
    wide['subtype_sum_residual'] = wide.Total - wide.Primary - wide.Secondary
    annual_error = float(abs(wide.subtype_sum_residual).max())
    assert annual_error < 1e-8
    wide.to_csv(OUT / (PREFIX + 'annual_endpoint_check.csv'), index=False)
    endpoint_rows = wide.query("cause == 'Endometriosis' and benchmark == 'dynamic' and year >= 2021")
    save('annual_endpoint_qc.json', {'input': 'PCOS_Revision_2026-10-29/results/python/all_annual_benchmark_aspr.csv',
        'input_sha256': sha(SCI / 'results/python/all_annual_benchmark_aspr.csv'), 'annual_input_rows': len(annual),
        'aggregate_output_rows': len(wide), 'annual_subtype_gap_sum_max_absolute_error': annual_error,
        'endometriosis_dynamic_endpoints': endpoint_rows.to_dict(orient='records'),
        'interpretation': 'Annual and endpoint point-estimate cancellation can be described. No correlation P value or posterior interval was computed.',
        'new_model_fitted': False})
    access = json.loads((PRIVATE / 'access_evidence.json').read_text())
    save('joint_draws_access_audit.json', {
        'status': 'bounded access audit completed; qualified joint posterior draws not obtained',
        'source_summary_schemas': schemas, 'matched_population_has_draw_columns': any('draw' in x.lower() for x in population.columns),
        'existing_audit': 'PCOS_Revision_2026-10-29/docs/uncertainty_access_audit_2026-10-29.json',
        'current_access_evidence': access,
        'interpretation': '403 errors and unsuccessful bounded discovery do not prove provider unavailability.',
        'provider_alignment_verified': False, 'posterior_intervals_generated': False,
        'comment_51_status': 'access audit verified; statistical uncertainty propagation remains blocked by missing qualified draws',
        'eligible_product_requires': ['GBD2023 version and required cause/impairment/sex/location/age/year coverage', 'Provider evidence of joint draw pairing across required dimensions; matching column names alone insufficient', 'Compatible denominators and weight specification', 'Reconstruction of product summaries, per-draw identities, independent verification'],
        'point_branch': 'Continue editorial correction using existing estimates and sensitivity results; do not substitute marginal bounds, independent simulations or country bootstrap for posterior propagation.'})
    assert all(sha(ROOT / p) == h for p, h in baseline.items())
    save('preflight_verification.json', {'input_hashes_verified': len(inputs), 'old_v5_files_unchanged': len(baseline),
        'source_checks_passed': True, 'annual_subtype_sum_check_passed': True,
        'scope': 'Preflight and reuse checks only, not completed manuscript revision',
        'T00': 'verified', 'T01': 'audit verified; full-precision weight provenance unresolved',
        'T02': 'access audit verified; no qualified draws', 'T04': 'annual aggregate table and additivity verified; manuscript incorporation pending',
        'T03_T05_T07': 'pending; no v6 created', 'joint_uncertainty_resolved': False,
        'cloud_sync': 'pending until connector readback and committed-blob verification'})
    report = '''PCOS修稿前置核验，2026-10-30

本轮接续最新17条批注方案，完成T00基线与私有隔离、T01输入/定义/环境审计、T02联合draws访问审计，以及T04全年亚型汇总核查。未生成v6、未重拟合GBD模型、未投稿。

七项输入SHA256及大小与旧manifest一致；19国/18参照、两套各4522人口单元、两病因三亚型27132病例单元检查通过。端点原始Rate与病例/GBD人口重构率核对通过。国家映射单列CSV；原始GBD单元不在交付目录。

已读现存GBD2023 Appendix 1：PDF685-687页区分调查五年定义与临床12个月来源，并说明模型分母为全部育龄女性；PDF591-592及691-693页给出PCOS定义调整和不孕归因流程。四个相关页面已渲染目视检查。附录官方链接本轮下载挑战，使用原有82,917,810字节副本，哈希另列。

Python历史输出记录3.12.14，R会话记录4.6.1；本轮使用原有Python环境核查并另记当前库版本。七年龄组权重与既有六位复刻表一致，但尚未独立核实官方全精度向量，保持原值和既有舍入敏感性。

官方GBD入口本次403；Drive文件名限定搜索仅找到3份既有说明/计划及2个无关drawing目录，未识别抽样数据。4份GBD研究输入含val/lower/upper而无draw列；没有取得提供方联合配对证据。批注51仍未统计解决，不能制造联合区间。

年度表复用已有1224行汇总结果，整理成408行同病因/人口源/基准/年份的原发、继发和总率差，亚型加和核查通过。可描述2021-2023抵消变化，没有进行把平滑年份当独立样本的相关检验。

下一项具体工作：T03在独立v6中统一N/CHN及年度D与期间ΔD、修订主要结果/贡献和摘要，再完成T05文献/临床定义对照与T07文档构建。验收：17条逐项回应，数值变更有真实来源，Word/TeX/PDF一致并逐页检查，原v5不变，双云内容核验。无draws分支仍可执行；不得把本轮前置审计称作全部修稿完成。
'''
    (OUT / (PREFIX + 'README_ZH.txt')).write_text(report)
    print(json.dumps({'outputs': len(list(OUT.iterdir())), 'inputs_verified': len(inputs), 'old_v5_files_preserved': len(baseline), 'source_cell_additivity_error': add_error, 'endpoint_rate_error': rate_error, 'annual_sum_error': annual_error}))


def verify():
    b = json.loads((OUT / (PREFIX + 'baseline_manifest.json')).read_text())
    assert all(sha(ROOT / p) == h for p, h in b['v5_all_file_sha256'].items())
    assert all(sha(ROOT / p) == v['sha256'] for p, v in b['verified_input_manifest_entries'].items())
    # Independent scalar check of every exported annual aggregate against original rows.
    import csv
    with (SCI / 'results/python/all_annual_benchmark_aspr.csv').open() as f:
        original = {(r['cause'],r['source'],r['benchmark'],r['year'],r['subtype']): float(r['gap']) for r in csv.DictReader(f)}
    with (OUT / (PREFIX + 'annual_endpoint_check.csv')).open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 408
    for r in rows:
        k = tuple(r[x] for x in ['cause','source','benchmark','year'])
        for subtype in ['Primary','Secondary','Total']:
            assert abs(float(r[subtype]) - original[k+(subtype,)]) < 1e-10
        assert abs(float(r['Total'])-float(r['Primary'])-float(r['Secondary'])) < 1e-8
    assert git('rev-parse','HEAD') == b['local_head']
    print('Verified: baseline preservation, input hashes, 408 exported annual rows against source, local HEAD unchanged.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['audit','verify'])
    args = parser.parse_args()
    audit() if args.mode == 'audit' else verify()
