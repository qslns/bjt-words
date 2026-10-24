#!/usr/bin/env python3
# 사용 중지(10/13): edge-tts 7.3.1로 복구됨 → 기본 카드 음성은 gen_audio_az.py --engine edge 로 만든다.
import sys; sys.exit("gen_audio_g.py 사용 중지: gen_audio_az.py --engine edge 를 쓰세요")
"""Edge TTS가 10/10부터 막혀서(마이크로소프트 엔드포인트 변경) 새 기본 카드 음성은 Google 번역 TTS로 만든다.
1500 카드에서 가져온 예문은 원래 녹음 파일을 복사. 이미 있는 파일은 건너뜀."""
import os, sys, json, ssl, time, shutil, subprocess, urllib.request, urllib.parse, concurrent.futures as cf
src = open('/home/claude/work/gen_audio.py', encoding='utf-8').read().split('async def main():')[0]
NS = {'__name__': 'ga'}; exec(compile(src, 'gen_audio_defs', 'exec'), NS)
word_text, AUD = NS['word_text'], NS['AUD']
D = json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8'))
AM = json.load(open('/home/claude/work/basic/audio_map.json', encoding='utf-8'))
TMP = '/home/claude/work/tts_raw'; os.makedirs(TMP, exist_ok=True)
CTX = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({'https': os.environ['HTTPS_PROXY']}), urllib.request.HTTPSHandler(context=CTX))
def fetch(text, raw):
    url = 'https://translate.google.com/translate_tts?' + urllib.parse.urlencode({'ie': 'UTF-8', 'client': 'tw-ob', 'tl': 'ja', 'q': text})
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36', 'Referer': 'https://translate.google.com/'})
    with OPENER.open(req, timeout=30) as r: data = r.read()
    if len(data) < 1000: raise RuntimeError('short')
    open(raw, 'wb').write(data)
def finish(raw, dst):
    af = ('silenceremove=start_periods=1:start_silence=0.06:start_threshold=-45dB,areverse,'
          'silenceremove=start_periods=1:start_silence=0.15:start_threshold=-45dB,areverse,volume=3dB,alimiter=limit=0.9')
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', af, '-c:a', 'libmp3lame', '-b:a', '48k', '-ar', '24000', '-ac', '1', dst], capture_output=True)
    if r.returncode != 0 or not os.path.exists(dst) or os.path.getsize(dst) < 1000: raise RuntimeError('ffmpeg ' + r.stderr.decode()[:200])
    os.remove(raw)
MANP = '/home/claude/work/basic/audio_manifest.json'
MAN = json.load(open(MANP, encoding='utf-8')) if os.path.exists(MANP) else {}
def job(text, dst):
    if os.path.exists(dst) and os.path.getsize(dst) > 1000 and MAN.get(dst) == 'tts:' + text: return 'skip'
    raw = os.path.join(TMP, os.path.basename(dst))
    for k in range(5):
        try:
            fetch(text, raw); finish(raw, dst); MAN[dst] = 'tts:' + text; time.sleep(0.25); return 'ok'
        except Exception as e:
            err = str(e); time.sleep(2 + 3 * k)
    return 'fail ' + err
ws = sorted([w for w in D['words'] if w['id'] >= 9000], key=lambda w: w['bn'])
jobs, cp = [], 0
for w in ws:
    jobs.append((word_text(w), f"{AUD}/w/{w['id']}.mp3"))
    for i, e in enumerate(w['e']):
        dst = f"{AUD}/s/{w['id']}-{i}.mp3"; k = f"{w['id']}-{i}"
        if k in AM:
            s = f"{AUD}/s/{AM[k][0]}-{AM[k][1]}.mp3"
            if not os.path.exists(s): print('MISSING SRC', s); continue
            if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(s) or MAN.get(dst) != 'copy:' + s: shutil.copyfile(s, dst); MAN[dst] = 'copy:' + s; cp += 1
        else:
            jobs.append((e['t'], dst))
print('copied', cp, 'tts jobs', len(jobs), flush=True)
t0 = time.time(); res = {}
with cf.ThreadPoolExecutor(3) as ex:
    for (text, dst), r in zip(jobs, ex.map(lambda j: job(*j), jobs)):
        res[r.split()[0]] = res.get(r.split()[0], 0) + 1
        if r.startswith('fail'): print('FAIL', dst, text, r)
json.dump(MAN, open(MANP, 'w', encoding='utf-8'), ensure_ascii=False)
print('DONE', res, 'sec', int(time.time() - t0))
