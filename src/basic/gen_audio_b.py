#!/usr/bin/env python3
"""기본 카드(id>=9000) 음성: 단어는 새로 녹음, 예문은 1500 카드에서 가져온 것은 파일 복사, 새 예문만 녹음."""
import certifi
certifi.where = lambda: '/root/.ccr/ca-bundle.crt'
import asyncio, os, sys, json, shutil, time
sys.argv = [sys.argv[0]]
src = open('/home/claude/work/gen_audio.py', encoding='utf-8').read().split('async def main():')[0]
NS = {'__name__': 'ga'}; exec(compile(src, 'gen_audio_defs', 'exec'), NS)
one, word_text, AUD = NS['one'], NS['word_text'], NS['AUD']
D = json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8'))
AM = json.load(open('/home/claude/work/basic/audio_map.json', encoding='utf-8'))
async def main():
    ws = sorted([w for w in D['words'] if w['id'] >= 9000], key=lambda w: w['bn'])
    jobs, cp = [], 0
    for w in ws:
        jobs.append((word_text(w), 'ja-JP-NanamiNeural', f"{AUD}/w/{w['id']}.mp3"))
        for i, e in enumerate(w['e']):
            dst = f"{AUD}/s/{w['id']}-{i}.mp3"
            k = f"{w['id']}-{i}"
            if k in AM:
                s = f"{AUD}/s/{AM[k][0]}-{AM[k][1]}.mp3"
                if not os.path.exists(s): print('MISSING SRC', s); continue
                if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(s): shutil.copyfile(s, dst); cp += 1
            else:
                jobs.append((e['t'], 'ja-JP-KeitaNeural' if i == 1 else 'ja-JP-NanamiNeural', dst))
    stats = {'ok': 0, 'skip': 0, 'fail': []}
    sem = asyncio.Semaphore(10); t = time.time()
    print('copied', cp, 'tts jobs', len(jobs), flush=True)
    await asyncio.gather(*(one(sem, *j, stats) for j in jobs))
    print('DONE ok', stats['ok'], 'skip', stats['skip'], 'fail', len(stats['fail']), 'sec', int(time.time() - t), flush=True)
    for f in stats['fail']: print('FAIL', f)
asyncio.run(main())
