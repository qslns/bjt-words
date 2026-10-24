"""단어 음성 고친 것 저장소에 넣기: 기본 카드는 voice_jobs(t·v·rate)+manifest, 본편은 audio_versioned + voice_fix 기록
usage: python3 apply_w.py <cpick.json> <why_label>"""
import json, shutil, os, sys
R = '/home/claude/bjt-words'
P = {k: v for k, v in json.load(open(sys.argv[1], encoding='utf-8')).items() if not v.get('fail')}
WHY = sys.argv[2]
jobs = json.load(open(R + '/tools/voice_jobs.json', encoding='utf-8')); jidx = {j['f']: j for j in jobs}
man = json.load(open(R + '/tools/voice_manifest.json', encoding='utf-8'))
ver = json.load(open(R + '/tools/audio_versioned.json', encoding='utf-8')); vset = set(ver)
fix = json.load(open(R + '/tools/voice_fix.json', encoding='utf-8'))
os.makedirs('bak_audio_w', exist_ok=True); nb = nm = 0
for key, p in P.items():
    if p['tag'] == 'current': continue
    f = f'audio/{key}.mp3'; dst = f'{R}/{f}'
    shutil.copyfile(dst, 'bak_audio_w/' + key.replace('/', '_') + '.mp3')
    shutil.copyfile(p['file'], dst)
    rate = p.get('rate') or '+0%'
    if f in jidx:
        j = jidx[f]; was = j['t']; j['t'] = p['t']; j['v'] = p['v']
        if rate != '+0%': j['rate'] = rate
        else: j.pop('rate', None)
        man[f] = f"edge:{p['v']}:{p['t']}" + (f':{rate}' if rate != '+0%' else ''); nb += 1
    else:
        was = None
        if key not in vset: ver.append(key); vset.add(key)
        nm += 1
    rec = {'f': f, 'v': p['v'], 't': p['t'], 'why': WHY + ' (' + p['how'] + ')', 'date': '10/22'}
    if rate != '+0%': rec['rate'] = rate
    if was: rec['was'] = was
    fix.append(rec)
json.dump(jobs, open(R + '/tools/voice_jobs.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(man, open(R + '/tools/voice_manifest.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(ver, open(R + '/tools/audio_versioned.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(fix, open(R + '/tools/voice_fix.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('basic', nb, 'main', nm)
