#!/usr/bin/env python3
"""새 카드 음성 만들기 (11/13, 확장 P2~ · HANDOFF 8절)
쓰기: python3 make_audio.py JOBS.json OUT_ROOT [--conc 4] [--force]
  JOBS.json  [{"f": "audio/w/9886.mp3", "v": "ja-JP-NanamiNeural", "t": "読む글", "rate": "+0%"(선택)}]
  OUT_ROOT   파일을 만들 뿌리 폴더(예: /home/claude/aqa/stage) — 저장소 audio/에 바로 쓰지 않음(검사 뒤 복사)
edge-tts(나나미·게이타만) → 앞뒤 무음 자르기 → 24kHz 48kbps 모노 mp3 (tools/regen_voice.py의 trim과 같은 필터)
OUT_ROOT/manifest.json에 (목소리·글·속도) 서명을 적어 같은 일은 건너뜀. 컨테이너는 HTTPS_PROXY + ~/.ccr/ca-bundle.crt로만 밖에 나감."""
import os, sys, json, ssl, asyncio, subprocess, argparse, time
CA = '/root/.ccr/ca-bundle.crt' if os.path.exists('/root/.ccr/ca-bundle.crt') else None
PROXY = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
VOICES = {'ja-JP-NanamiNeural', 'ja-JP-KeitaNeural'}
AF = 'silenceremove=start_periods=1:start_silence=0.06:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_silence=0.15:start_threshold=-45dB,areverse'

def trim(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', AF, '-c:a', 'libmp3lame', '-b:a', '48k', '-ar', '24000', '-ac', '1', dst], capture_output=True)
    if r.returncode != 0 or not os.path.exists(dst) or os.path.getsize(dst) < 1000: os.replace(src, dst)
    elif os.path.exists(src): os.remove(src)

def sig(j): return '%s:%s:%s' % (j['v'], j['t'], j.get('rate', '+0%'))

async def one(j, root, tmp, sem, man, done, fails):
    import edge_tts
    async with sem:
        dst = os.path.join(root, j['f']); raw = os.path.join(tmp, j['f'].replace('/', '_'))
        for k in range(5):
            try:
                await edge_tts.Communicate(j['t'], j['v'], rate=j.get('rate', '+0%'), proxy=PROXY).save(raw)
                if os.path.getsize(raw) > 1000: break
            except Exception as ex:
                err = str(ex)[:80]
            await asyncio.sleep(1.5 * (k + 1))
        else:
            fails.append((j['f'], err if 'err' in dir() else 'fail')); return
        await asyncio.get_running_loop().run_in_executor(None, trim, raw, dst)
        man[j['f']] = sig(j); done.append(j['f'])

async def main_async(jobs, root, conc):
    import edge_tts.communicate as C
    if CA:
        ctx = ssl.create_default_context(cafile=CA)
        for n in dir(C):
            if isinstance(getattr(C, n), ssl.SSLContext): setattr(C, n, ctx)
    mp = os.path.join(root, 'manifest.json')
    man = json.load(open(mp, encoding='utf-8')) if os.path.exists(mp) else {}
    tmp = os.path.join(root, '.tmp'); os.makedirs(tmp, exist_ok=True)
    todo = [j for j in jobs if A.force or man.get(j['f']) != sig(j) or not os.path.exists(os.path.join(root, j['f']))]
    print('jobs', len(jobs), 'todo', len(todo), flush=True)
    sem = asyncio.Semaphore(conc); done, fails = [], []
    t0 = time.time()
    tasks = [one(j, root, tmp, sem, man, done, fails) for j in todo]
    for i in range(0, len(tasks), 50):
        await asyncio.gather(*tasks[i:i + 50])
        json.dump(man, open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print('  %d/%d  %ds' % (min(i + 50, len(tasks)), len(tasks), time.time() - t0), flush=True)
    print('done', len(done), 'fail', len(fails), fails[:5])
    return fails

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('jobs'); ap.add_argument('root'); ap.add_argument('--conc', type=int, default=4); ap.add_argument('--force', action='store_true')
    A = ap.parse_args()
    J = json.load(open(A.jobs, encoding='utf-8'))
    bad = [j for j in J if j['v'] not in VOICES]
    if bad: sys.exit('나나미·게이타만: %s' % bad[:3])
    fails = asyncio.run(main_async(J, A.root, A.conc))
    sys.exit(1 if fails else 0)
