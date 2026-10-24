"""예문 음성 고친 것 저장소에 넣기(기본: voice_jobs+manifest / 본편: audio_versioned) + voice_fix 기록
usage: python3 apply_s.py <spick.json> [<spick2.json> ...]  (환경변수 SKIP=키,키 로 제외)"""
import json, shutil, os, sys
from build_sjobs import current
R = '/home/claude/bjt-words'
SKIP = set(filter(None, os.environ.get('SKIP', '').split(',')))
P = {}
for p in sys.argv[1:]:
    for k, v in json.load(open(p, encoding='utf-8')).items():
        if not v.get('fail') and v.get('tag') != 'current' and k not in SKIP: P[k] = v
jobs = json.load(open(R + '/tools/voice_jobs.json', encoding='utf-8')); jidx = {j['f']: j for j in jobs}
man = json.load(open(R + '/tools/voice_manifest.json', encoding='utf-8'))
ver = json.load(open(R + '/tools/audio_versioned.json', encoding='utf-8')); vset = set(ver)
fix = json.load(open(R + '/tools/voice_fix.json', encoding='utf-8'))
os.makedirs('bak_audio_s', exist_ok=True); nb = nm = 0
for key, p in P.items():
    wid, i = map(int, key[2:].split('-')); was, _ = current(wid, i)
    f = f'audio/{key}.mp3'; dst = f'{R}/{f}'
    if not os.path.exists('bak_audio_s/' + key.replace('/', '_') + '.mp3'): shutil.copyfile(dst, 'bak_audio_s/' + key.replace('/', '_') + '.mp3')
    shutil.copyfile(p['file'], dst)
    rate = p.get('rate') or '+0%'
    if f in jidx:
        j = jidx[f]; j['t'] = p['t']; j['v'] = p['v']
        if rate != '+0%': j['rate'] = rate
        else: j.pop('rate', None)
        man[f] = f"edge:{p['v']}:{p['t']}" + (f':{rate}' if rate != '+0%' else ''); nb += 1
    else:
        if key not in vset: ver.append(key); vset.add(key)
        nm += 1
    rec = {'f': f, 'v': p['v'], 't': p['t'], 'was': was, 'why': '예문 받아쓰기 전수 검사(음소 인식기): ' + ', '.join(b['u'] + ' → ' + b['heard'] for b in p.get('cur_bad', [])), 'date': '10/22'}
    if rate != '+0%': rec['rate'] = rate
    fix.append(rec)
json.dump(jobs, open(R + '/tools/voice_jobs.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(man, open(R + '/tools/voice_manifest.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(ver, open(R + '/tools/audio_versioned.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(fix, open(R + '/tools/voice_fix.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('basic', nb, 'main', nm)
