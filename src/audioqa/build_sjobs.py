"""예문: 받아쓰기에서 걸린 후리가나 구간(seg)을 가나로 바꿔 넣은 후보 만들기 → sfix 작업 목록
숫자 구간(txt)은 사람(Claude)이 직접 보고 고칠 것만 OVERRIDE에 넣음
usage: python3 build_sjobs.py <out_jobs.json> <jsonl...>"""
import sys, json, re
from triage_s import benign
NA, KE = 'ja-JP-NanamiNeural', 'ja-JP-KeitaNeural'
R = '/home/claude/bjt-words'
W = {w['id']: w for w in json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8'))['words']}
FIX = {}
for f in json.load(open(R + '/tools/voice_fix.json', encoding='utf-8')): FIX[f['f']] = f   # 마지막 기록이 현재
JOBS = {j['f']: j for j in json.load(open(R + '/tools/voice_jobs.json', encoding='utf-8'))}
def kata(s): return ''.join(chr(ord(c) + 0x60) if 'ぁ' <= c <= 'ゖ' else c for c in s)
def current(wid, i):
    f = f'audio/s/{wid}-{i}.mp3'
    if f in FIX: return FIX[f]['t'], FIX[f]['v']
    if f in JOBS: return JOBS[f]['t'], JOBS[f]['v']
    return W[wid]['e'][i]['t'], (KE if i == 1 else NA)
OVERRIDE = json.load(open('s_override.json', encoding='utf-8')) if __import__('os').path.exists('s_override.json') else {}
if __name__ == '__main__':
    out = sys.argv[1]; jobs = []; manual = []
    for p in sys.argv[2:]:
        for l in open(p, encoding='utf-8'):
            r = json.loads(l); key = f"s/{r['id']}-{r['i']}"
            segs = [f for f in r['fl'] if f['k'] == 'seg' and f['mg'] > 2 and not benign(f)]
            digs = [f for f in r['fl'] if f['k'] == 'txt' and re.search(r'[0-9０-９]', f['u']) and f['mg'] > 0.5 and not benign(f)]
            others = [f for f in r['fl'] if f['k'] == 'txt' and not re.search(r'[0-9０-９]', f['u']) and f['mg'] > 5 and not benign(f)]
            if not (segs or digs or others or key in OVERRIDE): continue
            t, v = current(r['id'], r['i'])
            if key in OVERRIDE:
                jobs.append({'name': key, 'target': 'override', 'cands': [[f'o{k}', v, x, ''] for k, x in enumerate(OVERRIDE[key])]}); continue
            if digs or others: manual.append((key, t, [(f['u'], f['exp'], f['heard'], f['mg']) for f in digs + others], r['got']))
            if not segs: continue
            c1, c2 = t, t; ok = True
            for f in segs:
                base, rd = f['u'].split('|')
                if base in c1: c1 = c1.replace(base, rd, 1); c2 = c2.replace(base, kata(rd), 1)
                else: ok = False
            if not ok and c1 == t: manual.append((key, t, [(f['u'], f['exp'], f['heard'], f['mg']) for f in segs], r['got'])); continue
            jobs.append({'name': key, 'target': ' / '.join(f['u'] for f in segs), 'cands': [['h', v, c1, ''], ['k', v, c2, ''], ['h2', v, c1, '-10%']]})
    json.dump(jobs, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump(manual, open(out.replace('.json', '_manual.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('jobs', len(jobs), 'manual', len(manual))
