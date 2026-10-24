"""한자 소리 고친 것(라운드 N) 저장소에 넣기 + 작업 목록·기록 고치기
usage: python3 apply_kx.py <picks.json> <kpicks.json> <plan.json>"""
import json, shutil, os, sys
R = '/home/claude/bjt-words'; NA = 'ja-JP-NanamiNeural'
J = json.load(open(R + '/tools/kanji_voice_jobs.json', encoding='utf-8'))
man = json.load(open(R + '/audio/manifest_kanji.json', encoding='utf-8'))
P = {k: v for k, v in json.load(open(sys.argv[1], encoding='utf-8')).items() if not v.get('fail')}
KP = {k: v for k, v in json.load(open(sys.argv[2], encoding='utf-8')).items() if not v.get('fail')}
plan = json.load(open(sys.argv[3], encoding='utf-8'))['plan']
idx = {j['key']: j for j in J['kr']}
def sig(v, t, rate): return 'edge:' + v + ':' + t + ('' if (rate or '+0%') == '+0%' else ':' + rate)
os.makedirs('bak_audio_r', exist_ok=True)
for k, p in list(P.items()) + list(KP.items()):
    dst = f'{R}/audio/{k}.mp3'; os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst): shutil.copyfile(dst, 'bak_audio_r/' + k.replace('/', '_') + '.mp3')
    shutil.copyfile(p['file'], dst)
    e = idx.get(k)
    if e is None: e = {'key': k}; J['kr'].append(e); idx[k] = e
    e['t'] = p['t']
    if p['v'] != NA: e['v'] = p['v']
    else: e.pop('v', None)
    if p.get('rate') and p['rate'] != '+0%': e['rate'] = p['rate']
    else: e.pop('rate', None)
    man[k] = sig(p['v'], p['t'], p.get('rate'))
for kk, v in plan.items():
    if 'out' not in v: continue
    # 게이타 판 부품(krk)을 썼으면 작업 목록의 rep도 그 키로
    parts = []
    for p, f in zip(v['parts'], v['files']):
        kkp = 'krk/' + p.split('/', 1)[1]
        parts.append(kkp if kkp in KP and KP[kkp]['file'] == f else p)
    J['rep'][kk] = parts
    dst = f'{R}/audio/{kk}.mp3'
    shutil.copyfile(dst, 'bak_audio_r/' + kk.replace('/', '_') + '.mp3')
    shutil.copyfile(v['out'], dst)
    man[kk] = 'concat:' + ','.join(man.get(p, p) for p in parts) + f":{J['gap']}"
json.dump(J, open(R + '/tools/kanji_voice_jobs.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(man, open(R + '/audio/manifest_kanji.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('kr/krk', len(P) + len(KP), 'reps', sum(1 for v in plan.values() if 'out' in v))
