"""대표 소리(audio/k) 다시 잇기: 고친 읽기 소리(pick)를 반영. 한 한자의 대표 소리 안에서는 목소리를 하나로(게이타 읽기가 끼면 나머지도 게이타 판)
usage: python3 krep.py <kanji_voice_jobs.json> <audio_dir> <picks.json[,picks2.json]> <keita_picks.json> <stage_dir> <out_plan.json>
- picks: 다시 만든 kr 읽기 {key: {v, t, rate, file}} (fixgen pick.json 합친 것)
- keita_picks: 게이타 판 읽기 {krk/<hex>: {...}} (없으면 빈 파일)
결과: stage_dir/k/*.mp3 + plan(어느 대표 소리를 어떤 부품으로 만들었는지)"""
import sys, os, json, shutil, subprocess
J = json.load(open(sys.argv[1], encoding='utf-8')); A = sys.argv[2]
P = {}
for p in sys.argv[3].split(','): P.update({k: v for k, v in json.load(open(p, encoding='utf-8')).items() if not v.get('fail')})
KP = {k: v for k, v in json.load(open(sys.argv[4], encoding='utf-8')).items() if not v.get('fail')} if os.path.exists(sys.argv[4]) else {}
ST = sys.argv[5]; os.makedirs(ST + '/k', exist_ok=True)
GAP = J['gap']
def part_file(p, keita):
    """부품 p의 파일과 목소리: keita면 게이타 판(krk) 우선"""
    if keita:
        if p in P and 'Keita' in P[p]['v']: return P[p]['file'], 'k'
        kk = 'krk/' + p[3:]
        if kk in KP: return KP[kk]['file'], 'k'
        return None, None
    if p in P: return P[p]['file'], ('k' if 'Keita' in P[p]['v'] else 'n')
    return f'{A}/{p}.mp3', 'n'
def concat(files, dst):
    if len(files) == 1: shutil.copyfile(files[0], dst); return
    sil = dst + '.sil.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono', '-t', str(GAP), sil], check=True)
    ins = []
    for i, f in enumerate(files):
        if i: ins += ['-i', sil]
        ins += ['-i', f]
    n = len(files) * 2 - 1
    fc = ''.join(f'[{i}:a]' for i in range(n)) + f'concat=n={n}:v=0:a=1[a]'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', fc, '-map', '[a]', '-c:a', 'libmp3lame', '-b:a', '48k', '-ar', '24000', '-ac', '1', dst], check=True)
    os.remove(sil)
plan = {}; need_k = set()
force = set(json.load(open(ST + '/force_rep.json', encoding='utf-8'))) if os.path.exists(ST + '/force_rep.json') else set()
for kk, parts in J['rep'].items():
    changed = any(p in P for p in parts) or kk in force
    if not changed: continue
    keita = any(p in P and 'Keita' in P[p]['v'] for p in parts)
    files, voices = [], []
    for p in parts:
        f, v = part_file(p, keita)
        if f is None: need_k.add(p); files = None; break
        files.append(f); voices.append(v)
    if files is None: plan[kk] = {'parts': parts, 'need_keita': True}; continue
    dst = f'{ST}/{kk}.mp3'; concat(files, dst)
    plan[kk] = {'parts': parts, 'files': files, 'voices': voices, 'out': dst}
json.dump({'plan': plan, 'need_keita_parts': sorted(need_k)}, open(sys.argv[6], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('reps rebuilt', sum(1 for v in plan.values() if 'out' in v), 'need keita parts', len(need_k))
