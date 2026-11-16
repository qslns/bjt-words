#!/usr/bin/env python3
"""N3·N2 칸 한 부의 새 음성 → 저장소(11/16): stage 파일을 audio/로 복사 + tools/voice_jobs.json(f v t jl jn)·voice_manifest.json 고침
- 옛 경로를 덮는 고침(jobs_fix)도 같은 방식(voice_jobs에 들어가면 앱이 ?v=해시로 새로 받음)
usage: python3 merge_voice.py JOBS.json STAGE_DIR ORDER.json [LVSET.json] [--dry]"""
import json, sys, os, shutil
R = '/home/claude/bjt-words'
jobs_f, stage, order_f = sys.argv[1:4]
extra = [a for a in sys.argv[4:] if not a.startswith('--')]
dry = '--dry' in sys.argv
pos = {}
for f in [order_f] + extra:
    for x in json.load(open(f, encoding='utf-8')): pos[x['id']] = (x['jl'], x['jn'])
J = json.load(open(jobs_f, encoding='utf-8'))
VJ = json.load(open(R + '/tools/voice_jobs.json', encoding='utf-8')); idx = {j['f']: i for i, j in enumerate(VJ)}
M = json.load(open(R + '/tools/voice_manifest.json', encoding='utf-8'))
def cid(f): return int(f.split('/')[-1].split('.')[0].split('-')[0])
n_new = n_upd = 0; miss = []
for j in J:
    src = os.path.join(stage, j['f'])
    if not os.path.exists(src): miss.append(j['f']); continue
    i = cid(j['f'])
    if i not in pos: miss.append('pos ' + j['f']); continue
    jl, jn = pos[i]
    e = {'f': j['f'], 'v': j['v'], 't': j['t'], 'jl': jl, 'jn': jn}
    if j.get('rate') and j['rate'] != '+0%': e['rate'] = j['rate']
    sig = 'edge:%s:%s' % (j['v'], j['t']) + (':' + e['rate'] if 'rate' in e else '')
    if not dry:
        dst = os.path.join(R, j['f']); os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copyfile(src, dst)
    if j['f'] in idx: VJ[idx[j['f']]] = e; n_upd += 1
    else: idx[j['f']] = len(VJ); VJ.append(e); n_new += 1
    M[j['f']] = sig
if miss: sys.exit('없음: %s' % miss[:10])
if not dry:
    json.dump(VJ, open(R + '/tools/voice_jobs.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump(M, open(R + '/tools/voice_manifest.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('음성', len(J), '· voice_jobs 새', n_new, '· 고침', n_upd, '· 전체', len(VJ), '(dry)' if dry else '')
