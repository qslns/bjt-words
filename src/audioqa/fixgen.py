"""다시 녹음 후보 만들기 + 고르기(한자 읽기·단어 공용)
usage: python3 fixgen.py <jobs.json> <outdir> [--all]
jobs: [{name, read(기대 가나), trim: 'k'|'w', cands: [[tag, voice, text, rate], ...]}]
후보를 우선순위대로 받아쓰기(これは…です 사이) + 소리 모양 검사 → 처음 통과한 것을 고름. --all이면 전부 평가.
결과 <outdir>/pick.json: {name: {tag, v, t, rate, file, got, ...} | {fail, tried}}"""
import sys, os, json, ssl, asyncio, subprocess
from kana import to_ph
from qa_ctx import judge
CA = '/root/.ccr/ca-bundle.crt'; CTX = ssl.create_default_context(cafile=CA)
PROXY = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
import edge_tts, edge_tts.communicate as Cm
for n in dir(Cm):
    if isinstance(getattr(Cm, n), ssl.SSLContext): setattr(Cm, n, CTX)
AF = {'k': 'silenceremove=start_periods=1:start_silence=0.1:start_threshold=-55dB,areverse,silenceremove=start_periods=1:start_silence=0.15:start_threshold=-55dB,areverse',
      'w': 'silenceremove=start_periods=1:start_silence=0.06:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_silence=0.15:start_threshold=-45dB,areverse'}
def trim(src, dst, kind):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', AF[kind], '-c:a', 'libmp3lame', '-b:a', '48k', '-ar', '24000', '-ac', '1', dst], check=True)
async def syn(sem, text, voice, rate, raw):
    async with sem:
        for k in range(6):
            try:
                await edge_tts.Communicate(text, voice, rate=rate or '+0%', proxy=PROXY).save(raw)
                if os.path.getsize(raw) > 800: return True
            except Exception:
                await asyncio.sleep(1.5 * (k + 1))
    return False
def safe(s): return s.replace('/', '_')
def sem_new(): return asyncio.Semaphore(6)
async def main(jobs, out, all_):
    os.makedirs(out, exist_ok=True); sem = asyncio.Semaphore(6)
    tasks = []
    for j in jobs:
        for tag, v, t, rate in j['cands']:
            raw = f"{out}/{safe(j['name'])}.{tag}.raw.mp3"
            if not os.path.exists(raw): tasks.append(syn(sem, t, v, rate, raw))
    await asyncio.gather(*tasks)
    pickp = f'{out}/pick.json'
    pick = json.load(open(pickp, encoding='utf-8')) if os.path.exists(pickp) else {}
    for j in jobs:
        exp = to_ph(j['read']); tried = []; best = None
        for tag, v, t, rate in j['cands']:
            raw = f"{out}/{safe(j['name'])}.{tag}.raw.mp3"; fn = raw.replace('.raw.mp3', '.mp3')
            if not os.path.exists(raw): continue
            if not os.path.exists(fn): trim(raw, fn, j['trim'])
            r = judge(fn, exp, car='k' if 'Keita' in v else 'n'); r.update(tag=tag, v=v, t=t, rate=rate, file=fn); tried.append(r)
            if r['d'] == 0 and r['ctx_ok'] and not r['why'] and not best:
                best = r
                if not all_: break
        pick[j['name']] = dict(best, tried=tried if all_ else None) if best else {'fail': True, 'tried': tried}
        print(j['name'], j['read'], '->', (best['tag'] + ' ' + best['got']) if best else 'FAIL ' + ' / '.join(x['tag'] + ':' + x['got'] + ('' if not x['why'] else str(x['why'])) for x in tried), flush=True)
    json.dump(pick, open(pickp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
if __name__ == '__main__':
    asyncio.run(main(json.load(open(sys.argv[1], encoding='utf-8')), sys.argv[2], '--all' in sys.argv))
