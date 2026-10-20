"""한자 소리(10/20): audio/k/<한자 코드>.mp3 = 대표 소리, audio/kr/<읽기 코드>.mp3 = 읽기 칩마다.
작업 목록 tools/kanji_voice_jobs.json ({key, t}: t = 읽을 가나, 한 박은 가타카나로 넣어 は→わ 같은 조사 읽기 방지).
다시 만들기: pip install edge-tts && python3 tools/kanji_voice.py audio tools/kanji_voice_jobs.json  (같은 글은 audio/manifest_kanji.json 보고 건너뜀)
그다음 작업 폴더에서 make.py로 다시 빌드(av의 k/·kr/ 해시가 바뀌어 기기 저장본도 바뀜)."""
import os, sys, json, ssl, time, asyncio, subprocess
OUT, JOBS = sys.argv[1], sys.argv[2]
VOICE = 'ja-JP-NanamiNeural'
CA = os.environ.get('SSL_CERT_FILE') or ('/root/.ccr/ca-bundle.crt' if os.path.exists('/root/.ccr/ca-bundle.crt') else None)
CTX = ssl.create_default_context(cafile=CA) if CA else ssl.create_default_context()
PROXY = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
import edge_tts, edge_tts.communicate as Cm
for n in dir(Cm):
    if isinstance(getattr(Cm, n), ssl.SSLContext): setattr(Cm, n, CTX)
def trim(src, dst):
    af = 'silenceremove=start_periods=1:start_silence=0.1:start_threshold=-55dB,areverse,silenceremove=start_periods=1:start_silence=0.15:start_threshold=-55dB,areverse'
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', af, '-c:a', 'libmp3lame', '-b:a', '48k', '-ar', '24000', '-ac', '1', dst], capture_output=True)
    if r.returncode != 0 or not os.path.exists(dst) or os.path.getsize(dst) < 800: os.replace(src, dst)
    elif os.path.exists(src): os.remove(src)
async def one(sem, j, man, fails):
    key, text = j['key'], j['t']
    dst = os.path.join(OUT, key + '.mp3'); os.makedirs(os.path.dirname(dst), exist_ok=True)
    raw = dst + '.tmp.mp3'; sig = 'edge:' + VOICE + ':' + text
    if man.get(key) == sig and os.path.exists(dst): return
    async with sem:
        for k in range(5):
            try:
                await edge_tts.Communicate(text, VOICE, proxy=PROXY).save(raw)
                if os.path.getsize(raw) > 800: break
            except Exception:
                await asyncio.sleep(1.5 * (k + 1))
        else:
            fails.append(j); return
    await asyncio.to_thread(trim, raw, dst)
    man[key] = sig
async def main():
    jobs = json.load(open(JOBS, encoding='utf-8'))
    manp = os.path.join(OUT, 'manifest_kanji.json')
    man = json.load(open(manp, encoding='utf-8')) if os.path.exists(manp) else {}
    sem = asyncio.Semaphore(5); fails = []; t0 = time.time()
    for i in range(0, len(jobs), 100):
        await asyncio.gather(*(one(sem, j, man, fails) for j in jobs[i:i + 100]))
        json.dump(man, open(manp, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print(time.strftime('%H:%M:%S'), min(i + 100, len(jobs)), '/', len(jobs), 'fails', len(fails), flush=True)
    print('DONE', len(man), 'fails', len(fails), [f['key'] for f in fails][:20], 'sec', int(time.time() - t0), flush=True)
asyncio.run(main())
