#!/usr/bin/env python3
"""0부 · 기본 카드 음성(임시 구글 음성 1,768개)을 본편과 같은 나나미·게이타 목소리로 다시 만든다.

이 저장소만 있으면 돌아가게 만든 스크립트(작업 폴더 없이). 필요한 것: python3, ffmpeg.
  Azure(같은 목소리, 공식):  AZURE_SPEECH_KEY=키 AZURE_SPEECH_REGION=japaneast python3 tools/regen_voice.py --engine az
  edge-tts(고쳐졌을 때):     pip install edge-tts && python3 tools/regen_voice.py --engine edge
작업 목록: tools/voice_jobs.json (f=파일, v=목소리, t=읽을 글). 단어·예문 0/2번=Nanami, 예문 1번=Keita.
이미 같은 엔진·목소리·글로 만든 파일은 tools/voice_manifest.json을 보고 건너뜀. 무료 Azure(F0)는 1분에 20건 → 약 90분.
무음 자르기·음질(24kHz 48kbps 모노 mp3)은 본편과 같음."""
import os, sys, json, ssl, time, argparse, subprocess, urllib.request, urllib.error
from xml.sax.saxutils import escape
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument('--engine', choices=['az', 'edge'], required=True)
ap.add_argument('--limit', type=int, default=0); ap.add_argument('--force', action='store_true')
A = ap.parse_args()
JOBS = json.load(open(os.path.join(ROOT, 'tools/voice_jobs.json'), encoding='utf-8'))
MANP = os.path.join(ROOT, 'tools/voice_manifest.json')
MAN = json.load(open(MANP, encoding='utf-8')) if os.path.exists(MANP) else {}
TMP = os.path.join(ROOT, 'tools/.tmp'); os.makedirs(TMP, exist_ok=True)
CA = os.environ.get('SSL_CERT_FILE') or ('/root/.ccr/ca-bundle.crt' if os.path.exists('/root/.ccr/ca-bundle.crt') else None)
CTX = ssl.create_default_context(cafile=CA) if CA else ssl.create_default_context()
PROXY = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
OPENER = urllib.request.build_opener(*([urllib.request.ProxyHandler({'https': PROXY})] if PROXY else []), urllib.request.HTTPSHandler(context=CTX))

def trim(src, dst):
    af = 'silenceremove=start_periods=1:start_silence=0.06:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_silence=0.15:start_threshold=-45dB,areverse'
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', af, '-c:a', 'libmp3lame', '-b:a', '48k', '-ar', '24000', '-ac', '1', dst], capture_output=True)
    if r.returncode != 0 or not os.path.exists(dst) or os.path.getsize(dst) < 1000: os.replace(src, dst)
    elif os.path.exists(src): os.remove(src)

last = [0.0]
def az(text, voice, raw):
    key, region = os.environ.get('AZURE_SPEECH_KEY'), (os.environ.get('AZURE_SPEECH_REGION') or '').replace(' ', '').lower()
    if not key or not region: sys.exit('AZURE_SPEECH_KEY / AZURE_SPEECH_REGION 필요')
    ssml = ("<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='ja-JP'>"
            f"<voice name='{voice}'><prosody pitch='+0Hz' rate='+0%' volume='+0%'>{escape(text)}</prosody></voice></speak>")
    for k in range(8):
        wait = 3.1 - (time.time() - last[0])
        if wait > 0: time.sleep(wait)
        last[0] = time.time()
        req = urllib.request.Request(f'https://{region}.tts.speech.microsoft.com/cognitiveservices/v1', data=ssml.encode('utf-8'), method='POST',
                                     headers={'Ocp-Apim-Subscription-Key': key, 'Content-Type': 'application/ssml+xml',
                                              'X-Microsoft-OutputFormat': 'audio-24khz-48kbitrate-mono-mp3', 'User-Agent': 'bjt-words'})
        try:
            with OPENER.open(req, timeout=60) as r: data = r.read()
            if len(data) < 1000: raise RuntimeError('short')
            open(raw, 'wb').write(data); return
        except urllib.error.HTTPError as e:
            if e.code in (401, 403): sys.exit(f'Azure 인증 실패({e.code}): 키·지역 확인')
            time.sleep(10 if e.code == 429 else 3 * (k + 1))
        except Exception:
            time.sleep(3 * (k + 1))
    raise RuntimeError('azure failed')

def edge(text, voice, raw):
    import asyncio, edge_tts
    if CA:
        import edge_tts.communicate as C
        for n in dir(C):
            if isinstance(getattr(C, n), ssl.SSLContext): setattr(C, n, CTX)
    for k in range(4):
        try:
            asyncio.run(edge_tts.Communicate(text, voice, proxy=PROXY).save(raw))
            if os.path.getsize(raw) > 1000: return
        except Exception:
            time.sleep(1.5 * (k + 1))
    raise RuntimeError('edge failed')

FETCH = az if A.engine == 'az' else edge
todo = [j for j in JOBS if A.force or MAN.get(j['f']) != f"{A.engine}:{j['v']}:{j['t']}" or not os.path.exists(os.path.join(ROOT, j['f']))]
if A.limit: todo = todo[:A.limit]
print('jobs', len(JOBS), 'todo', len(todo), flush=True)
ok, fail, t0 = 0, [], time.time()
for n, j in enumerate(todo, 1):
    dst = os.path.join(ROOT, j['f']); raw = os.path.join(TMP, os.path.basename(dst))
    try:
        FETCH(j['t'], j['v'], raw); trim(raw, dst)
        if os.path.getsize(dst) < 1000: raise RuntimeError('small')
        MAN[j['f']] = f"{A.engine}:{j['v']}:{j['t']}"; ok += 1
    except Exception as e:
        fail.append((j['f'], str(e)))
    if n % 25 == 0 or n == len(todo):
        json.dump(MAN, open(MANP, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print(time.strftime('%H:%M:%S'), f'{n}/{len(todo)} ok {ok} fail {len(fail)}', flush=True)
for f in fail: print('FAIL', *f)
print('DONE ok', ok, 'fail', len(fail), 'sec', int(time.time() - t0))
