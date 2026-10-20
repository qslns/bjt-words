"""한자 소리(10/21): audio/kr/<읽기 코드>.mp3 = 읽기 칩마다, audio/k/<한자 코드>.mp3 = 대표 소리(빨간 읽기들을 이어 붙인 것).
작업 목록 tools/kanji_voice_jobs.json: kr = [{key, t}] (t = 「읽기」 — 따옴표로 감싸야 한 박 소리가 깨끗함:
  그냥 'い'는 뒤에 짧은 잡음이 붙고, 'こ。'는 무음이 나옴), rep = {k/키: [kr/키...]}, gap = 읽기 사이 쉼(초).
다시 만들기: pip install edge-tts && python3 tools/kanji_voice.py   (같은 글은 audio/manifest_kanji.json 보고 건너뜀)
그다음 작업 폴더 make.py로 다시 빌드(av의 k/·kr/ 해시가 바뀌어 기기 저장본도 바뀜)."""
import os, sys, json, ssl, asyncio, subprocess, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = json.load(open(os.path.join(ROOT, 'tools/kanji_voice_jobs.json'), encoding='utf-8'))
VOICE, GAP = J['voice'], J['gap']
A = os.path.join(ROOT, 'audio')
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
    dst = os.path.join(A, j['key'] + '.mp3'); os.makedirs(os.path.dirname(dst), exist_ok=True)
    raw = dst + '.tmp.mp3'; sig = 'edge:' + VOICE + ':' + j['t']
    if man.get(j['key']) == sig and os.path.exists(dst): return
    async with sem:
        for k in range(5):
            try:
                await edge_tts.Communicate(j['t'], VOICE, proxy=PROXY).save(raw)
                if os.path.getsize(raw) > 800: break
            except Exception:
                await asyncio.sleep(1.5 * (k + 1))
        else:
            fails.append(j['key']); return
    await asyncio.to_thread(trim, raw, dst); man[j['key']] = sig
def concat(parts, dst):
    sil = dst + '.sil.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono', '-t', str(GAP), sil], check=True)
    ins = []
    for i, p in enumerate(parts):
        if i: ins += ['-i', sil]
        ins += ['-i', os.path.join(A, p + '.mp3')]
    n = len(parts) * 2 - 1
    fc = ''.join(f'[{i}:a]' for i in range(n)) + f'concat=n={n}:v=0:a=1[a]'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', fc, '-map', '[a]', '-c:a', 'libmp3lame', '-b:a', '48k', '-ar', '24000', '-ac', '1', dst], check=True)
    os.remove(sil)
async def main():
    manp = os.path.join(A, 'manifest_kanji.json')
    man = json.load(open(manp, encoding='utf-8')) if os.path.exists(manp) else {}
    sem = asyncio.Semaphore(5); fails = []
    await asyncio.gather(*(one(sem, j, man, fails) for j in J['kr']))
    for kk, parts in J['rep'].items():
        sig = 'concat:' + ','.join(man.get(p, p) for p in parts) + f':{GAP}'
        dst = os.path.join(A, kk + '.mp3')
        if man.get(kk) == sig and os.path.exists(dst): continue
        if len(parts) == 1: shutil.copyfile(os.path.join(A, parts[0] + '.mp3'), dst)
        else: concat(parts, dst)
        man[kk] = sig
    json.dump(man, open(manp, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('kr', len(J['kr']), 'rep', len(J['rep']), 'fails', fails)
asyncio.run(main())
