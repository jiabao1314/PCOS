#!/usr/bin/env python3
"""PCOS shared records: conflict-safe desktop sync and auditable command runner.

No credentials, patient records, Git staging or automatic claims of cloud success.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / '00_Shared_Context'
RUNTIME = ROOT / '.shared_context_runtime'
NAMES = ['PROJECT_OVERVIEW.md', 'PROJECT_STATUS.md', 'CHATGPT_HANDOFF.md',
         'CODEX_RUN_LOG.md', 'DATA_CATALOG.csv', 'RESULTS_INDEX.csv', 'DECISIONS.md',
         'NEXT_ACTIONS.md', 'CHATGPT_PROJECT_INSTRUCTIONS.txt', 'SYNC_CHECK.md']

def now():
    return datetime.now(ZoneInfo('Europe/Paris')).isoformat(timespec='seconds')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

def atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.' + path.name)
    try:
        options = {} if isinstance(value, bytes) else {'encoding': 'utf-8', 'newline': ''}
        with os.fdopen(fd, 'wb' if isinstance(value, bytes) else 'w', **options) as f:
            f.write(value)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)

def config():
    return json.loads((ROOT / 'config/shared_context.json').read_text())

def protect_runtime():
    RUNTIME.mkdir(parents=True, exist_ok=True)
    atomic(RUNTIME / '.gitignore', '*\n')

def sync(direction):
    """Preflight every file before any copy. Desktop bytes != cloud verification."""
    remote = Path(config()['desktop_shared_path']).expanduser()
    protect_runtime()
    if not remote.is_dir():
        raise RuntimeError('Verified desktop folder unavailable; use Drive connector, do not create a new project.')
    basepath = RUNTIME / 'baseline.json'
    base = json.loads(basepath.read_text()) if basepath.exists() else {}
    actions = []
    for name in NAMES:
        left, right = SHARED / name, remote / name
        lh, rh, bh = digest(left), digest(right), base.get(name)
        if lh == rh:
            continue
        if name not in base and lh and rh:
            raise RuntimeError('No baseline and divergent copies: ' + name)
        if lh != bh and rh != bh and lh and rh:
            raise RuntimeError('Both copies changed; reconcile manually: ' + name)
        src, dst = (right, left) if direction == 'pull' else (left, right)
        sh, dh = digest(src), digest(dst)
        if not sh:
            raise RuntimeError('Missing source; never propagate deletions: ' + str(src))
        if dh != bh and dh is not None:
            raise RuntimeError('Destination has newer changes; run opposite sync first: ' + name)
        actions.append((src, dst))
    stamp = now().replace(':', '-')
    for src, dst in actions:
        if dst.exists():
            backup = RUNTIME / 'archive' / stamp / direction / dst.name
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst, backup)
        atomic(dst, src.read_bytes())
        if digest(dst) != digest(src):
            raise RuntimeError('Desktop byte comparison failed: ' + dst.name)
    hashes = {n: digest(SHARED / n) for n in NAMES}
    atomic(basepath, json.dumps(hashes, indent=2))
    print(json.dumps({'at': now(), 'direction': direction, 'copied': len(actions),
                      'desktop_bytes_equal': True, 'cloud_verified': False,
                      'next': 'Drive connector readback and GitHub blob verification required.'}))

def run(specfile):
    spec = json.loads(Path(specfile).read_text())
    # Public metadata must be deliberately prepared; raw stdout remains private.
    required = ['id', 'task', 'command', 'inputs', 'code', 'outputs', 'next_actions']
    if any(k not in spec for k in required):
        raise ValueError('Missing required event fields: ' + ', '.join(required))
    if not isinstance(spec['command'], list) or not spec['command']:
        raise ValueError('command must be an argument array; no shell interpolation')
    if not spec.get('public_metadata_reviewed'):
        raise ValueError('Review metadata for identifiers/secrets before public logging.')
    for k in ['id', 'task']:
        if '\n' in spec[k] or not spec[k].strip():
            raise ValueError('Invalid single-line metadata: ' + k)
    if not all(c.isalnum() or c in '-_' for c in spec['id']):
        raise ValueError('Run ID must use letters, digits, hyphen or underscore.')
    eventpath = RUNTIME / 'runs' / (spec['id'] + '.json')
    if eventpath.exists():
        raise ValueError('Run ID exists; preserve previous record.')
    sync('pull')
    def paths(items):
        out = []
        for item in items:
            p = (ROOT / item).resolve()
            p.relative_to(ROOT)
            out.append(p)
        return out
    inputs, code, outputs = (paths(spec[k]) for k in ['inputs', 'code', 'outputs'])
    if not outputs or not code or any(not p.is_file() for p in inputs + code):
        raise ValueError('Require existing inputs/code and declared output paths.')
    before = {str(p.relative_to(ROOT)): digest(p) for p in inputs + code}
    # Require dated/new outputs; never overwrite original inputs or older results.
    if any(p.exists() for p in outputs) or set(inputs + code) & set(outputs):
        raise ValueError('Outputs must be new paths; do not overwrite prior files.')
    started = now()
    protect_runtime()
    rawlog = RUNTIME / (spec['id'] + '.log')
    with rawlog.open('w') as f:
        result = subprocess.run(spec['command'], cwd=ROOT, stdout=f, stderr=subprocess.STDOUT)
        checks = []
        if result.returncode == 0:
            for cmd in spec.get('verify_commands', []):
                checks.append(subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT).returncode)
    unchanged = all(digest(ROOT / p) == h for p, h in before.items())
    state = ('verified' if result.returncode == 0 and checks and all(x == 0 for x in checks)
             and unchanged and all(p.is_file() and p.stat().st_size for p in outputs)
             else 'failed' if result.returncode or not unchanged or any(checks) else 'unverified')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip())
    event = {**spec, 'started_at': started, 'ended_at': now(), 'exit_code': result.returncode,
             'verification_exit_codes': checks, 'state': state, 'code_base_commit': commit,
             'working_tree_dirty': dirty, 'inputs_and_code_unchanged': unchanged,
             'input_code_sha256': before,
             'output_sha256': {str(p.relative_to(ROOT)): digest(p) for p in outputs},
             'publication_commit': 'pending', 'cloud_sync': 'pending'}
    atomic(eventpath, json.dumps(event, ensure_ascii=False, indent=2))
    text = (SHARED / 'CODEX_RUN_LOG.md').read_text()
    text += (f"\n## {started} — {spec['id']}\n\n任务：{spec['task']}\n\n"
             f"实际命令：`{shlex.join(spec['command'])}`\n\n"
             f"状态：{state}；exit={result.returncode}；验证退出码={checks}。\n\n"
             f"代码基线：{commit}；工作树有修改={dirty}。实际代码/输入 SHA-256："
             f"`{json.dumps(before, ensure_ascii=False)}`。\n\n"
             f"输出 SHA-256：`{json.dumps(event['output_sha256'], ensure_ascii=False)}`。\n\n"
             f"错误/解决办法：{spec.get('error_resolution', '参见私人运行日志；尚无解决结论')}。"
             "最终发布提交与云端同步：pending；须完成连接器核验。\n")
    atomic(SHARED / 'CODEX_RUN_LOG.md', text)
    for filename, content in [('PROJECT_STATUS.md', f"{spec['task']}：{state}；结果发布待核验。"),
                              ('NEXT_ACTIONS.md', str(spec['next_actions']))]:
        atomic(SHARED / filename, (SHARED / filename).read_text() + f"\n- {now()} [{spec['id']}] {content}\n")
    index = SHARED / 'RESULTS_INDEX.csv'
    with index.open(newline='') as f:
        reader = csv.DictReader(f)
        fields, rows = reader.fieldnames, list(reader)
    for p in outputs:
        row = {k: '' for k in fields}
        row.update(name=p.name, path=str(p.relative_to(ROOT)), code=';'.join(spec['code']),
                   verification=state, sha256=digest(p) or '', version=started,
                   evidence=f"CODEX_RUN_LOG.md#{spec['id']}")
        rows.append(row)
    import io
    buf = io.StringIO(newline='')
    writer = csv.DictWriter(buf, fields); writer.writeheader(); writer.writerows(rows)
    atomic(index, buf.getvalue())
    # No clinical inference or success claims are made by this bookkeeping step.
    sync('push')
    print(json.dumps({'run_id': spec['id'], 'state': state, 'publication': 'pending'}, ensure_ascii=False))
    return 0 if state == 'verified' else 1

def plan():
    cfg = config()
    paths = ['00_Shared_Context/' + n for n in NAMES] + cfg['support_files']
    entries = []
    for rel in paths:
        p = ROOT / rel
        if not p.is_file():
            raise RuntimeError('Missing public allowlisted file: ' + rel)
        entries.append({'path': rel, 'sha256': digest(p), 'bytes': p.stat().st_size})
    print(json.dumps({'generated_at': now(), 'drive_folder_id': cfg['drive_folder_id'],
                      'repository': cfg['repository'], 'files': entries,
                      'note': 'Only these files; no recursive upload or git add -A.'}, indent=2))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['pull', 'push', 'plan', 'run'])
    p.add_argument('--spec')
    args = p.parse_args()
    if args.action in ['pull', 'push']:
        sync(args.action)
    elif args.action == 'plan':
        plan()
    else:
        if not args.spec:
            p.error('run requires --spec')
        return run(args.spec)
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, OSError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)
