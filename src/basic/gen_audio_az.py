#!/usr/bin/env python3
"""기본 카드(id>=9000) 음성을 본편과 같은 목소리로 다시 만든다.
단어·예문 0/2번 = ja-JP-NanamiNeural, 예문 1번 = ja-JP-KeitaNeural (본편 gen_audio.py와 같은 규칙, 같은 무음 자르기).
본편에서 가져온 예문(audio_map.json)은 본편 파일을 그대로 복사.

엔진: --engine az   → Azure Speech REST (키: 환경변수 AZURE_SPEECH_KEY/AZURE_SPEECH_REGION 또는 /home/claude/work/.azure_speech 두 줄)
      --engine edge → edge-tts (10/10부터 마이크로소프트 쪽 변경으로 403, 고쳐지면 이걸로)
--only w|s|all, --limit N(시험용), --force(이미 같은 엔진으로 만든 것도 다시)"""
import os, sys, json, ssl, time, shutil, subprocess, argparse, urllib.request, urllib.error
from xml.sax.saxutils import escape
src = open('/home/claude/work/gen_audio.py', encoding='utf-8').read().split('async def main():')[0]
NS = {'__name__': 'ga'}; exec(compile(src, 'gen_audio_defs', 'exec'), NS)
word_text, trim, AUD = NS['word_text'], NS['trim'], NS['AUD']
ap = argparse.ArgumentParser()
ap.add_argument('--engine', default='az'); ap.add_argument('--only', default='all')
ap.add_argument('--limit', type=int, default=0); ap.add_argument('--force', action='store_true')
ap.add_argument('--data', default='/home/claude/work/build/data_app.json'); ap.add_argument('--dry', action='store_true')
A = ap.parse_args()
D = json.load(open(A.data, encoding='utf-8'))
AM = json.load(open('/home/claude/work/basic/audio_map.json', encoding='utf-8'))
TMP = '/home/claude/work/tts_raw'; os.makedirs(TMP, exist_ok=True)
MANP = '/home/claude/work/basic/audio_manifest.json'
MAN = json.load(open(MANP, encoding='utf-8')) if os.path.exists(MANP) else {}
CTX = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({'https': os.environ['HTTPS_PROXY']}), urllib.request.HTTPSHandler(context=CTX))

def az_cred():
    k, r = os.environ.get('AZURE_SPEECH_KEY'), os.environ.get('AZURE_SPEECH_REGION')
    if not k and os.path.exists('/home/claude/work/.azure_speech'):
        k, r = [x.strip() for x in open('/home/claude/work/.azure_speech', encoding='utf-8').read().split('\n')[:2]]
    if not k or not r: sys.exit('Azure 키/지역이 없어요 (AZURE_SPEECH_KEY, AZURE_SPEECH_REGION)')
    return k, r.replace(' ', '').lower()
last = [0.0]
def az_fetch(text, voice, raw):
    key, region = CRED
    ssml = ("<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='ja-JP'>"
            f"<voice name='{voice}'><prosody pitch='+0Hz' rate='+0%' volume='+0%'>{escape(text)}</prosody></voice></speak>")
    for k in range(8):
        wait = 3.1 - (time.time() - last[0])   # 무료(F0) 한도: 60초에 20건
        if wait > 0: time.sleep(wait)
        last[0] = time.time()
        req = urllib.request.Request(f'https://{region}.tts.speech.microsoft.com/cognitiveservices/v1', data=ssml.encode('utf-8'), method='POST',
                                     headers={'Ocp-Apim-Subscription-Key': key, 'Content-Type': 'application/ssml+xml',
                                              'X-Microsoft-OutputFormat': 'audio-24khz-48kbitrate-mono-mp3', 'User-Agent': 'bjt-words'})
        try:
            with OPENER.open(req, timeout=60) as r: data = r.read()
            if len(data) < 1000: raise RuntimeError('short audio')
            open(raw, 'wb').write(data); return
        except urllib.error.HTTPError as e:
            if e.code in (401, 403): sys.exit(f'Azure 인증 실패 {e.code}: 키·지역 확인 필요')
            time.sleep(10 if e.code == 429 else 3 * (k + 1))
        except Exception:
            time.sleep(3 * (k + 1))
    raise RuntimeError('azure failed')
def edge_fetch(text, voice, raw):
    import asyncio, certifi
    certifi.where = lambda: '/root/.ccr/ca-bundle.crt'
    import edge_tts, edge_tts.communicate as C
    for n in dir(C):
        if isinstance(getattr(C, n), ssl.SSLContext): setattr(C, n, CTX)
    for k in range(4):
        try:
            asyncio.run(edge_tts.Communicate(text, voice, proxy=os.environ.get('HTTPS_PROXY')).save(raw))
            if os.path.getsize(raw) > 1000: return
        except Exception:
            time.sleep(1.5 * (k + 1))
    raise RuntimeError('edge failed')
FETCH = {'az': az_fetch, 'edge': edge_fetch}[A.engine]
CRED = az_cred() if (A.engine == 'az' and not A.dry) else None

ws = sorted([w for w in D['words'] if w['id'] >= 9000], key=lambda w: w['bn'])
jobs, cp = [], 0
for w in ws:
    if A.only in ('all', 'w'): jobs.append((word_text(w), 'ja-JP-NanamiNeural', f"{AUD}/w/{w['id']}.mp3"))
    for i, e in enumerate(w['e']):
        dst = f"{AUD}/s/{w['id']}-{i}.mp3"; k = f"{w['id']}-{i}"
        if k in AM:   # 본편 예문: 본편 녹음 복사
            s = f"{AUD}/s/{AM[k][0]}-{AM[k][1]}.mp3"
            if not os.path.exists(s): print('MISSING SRC', s); continue
            if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(s) or MAN.get(dst) != 'copy:' + s:
                shutil.copyfile(s, dst); MAN[dst] = 'copy:' + s; cp += 1
        elif A.only in ('all', 's'):
            jobs.append((e['t'], 'ja-JP-KeitaNeural' if i == 1 else 'ja-JP-NanamiNeural', dst))
todo = [j for j in jobs if A.force or not (os.path.exists(j[2]) and MAN.get(j[2]) == f'{A.engine}:{j[1]}:{j[0]}')]
if A.limit: todo = todo[:A.limit]
print('copied', cp, 'jobs', len(jobs), 'todo', len(todo), 'chars', sum(len(j[0]) for j in todo), flush=True)
if A.dry: sys.exit(0)
t0 = time.time(); ok = 0; fail = []
for n, (text, voice, dst) in enumerate(todo, 1):
    raw = os.path.join(TMP, 'az_' + os.path.basename(dst))
    try:
        FETCH(text, voice, raw); trim(raw, dst)
        if not os.path.exists(dst) or os.path.getsize(dst) < 1000: raise RuntimeError('trim')
        MAN[dst] = f'{A.engine}:{voice}:{text}'; ok += 1
    except Exception as e:
        fail.append((dst, text, str(e)))
    if n % 25 == 0 or n == len(todo):
        json.dump(MAN, open(MANP, 'w', encoding='utf-8'), ensure_ascii=False)
        print(time.strftime('%H:%M:%S'), f'{n}/{len(todo)} ok {ok} fail {len(fail)} ({int(time.time() - t0)}s)', flush=True)
json.dump(MAN, open(MANP, 'w', encoding='utf-8'), ensure_ascii=False)
for f in fail: print('FAIL', *f)
print('DONE ok', ok, 'fail', len(fail), 'sec', int(time.time() - t0))
