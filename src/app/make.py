#!/usr/bin/env python3
"""Fill the app template. usage: make.py data.json outdir mode app_url audio_mb"""
import sys, os, json, hashlib, shutil
data_path, outdir, mode, app_url, audio_mb = sys.argv[1:6]
tpl = open('/home/claude/work/app/app2.tpl.html', encoding='utf-8').read()
data = json.load(open(data_path, encoding='utf-8'))
# 10/16 한자 단원·한자 카드: 한자 순서(많이 쓰는 순, 950자) → data.kzo · 한자 카드(kzc.py compile 결과) → data.kc = {한자: 카드}
# 기존 data.kanji(b·bn·s·x 포함)는 그대로 둠 — 카드 없는 한자는 옛 자료로 그림
KZ_SRC, KZ_CARDS = '/home/claude/work/kanji_mn/kanji_src.json', '/home/claude/work/kz/kz_cards.json'
if os.path.exists(KZ_SRC) and data.get('kanji'):
    data['kzo'] = [k['c'] for k in json.load(open(KZ_SRC, encoding='utf-8')) if k.get('c') in data['kanji']]
    if os.path.exists(KZ_CARDS):
        kc, bad = {}, []
        need = {'c': str, 'h': str, 'on': list, 'kun': list, 'hook': str, 'S': list, 'p': list, 't': list, 'snd': str}
        for c in json.load(open(KZ_CARDS, encoding='utf-8')):
            if isinstance(c, dict) and c.get('c') in data['kanji'] and all(isinstance(c.get(f), t) for f, t in need.items()): kc[c['c']] = c
            else: bad.append(c.get('c') if isinstance(c, dict) else '?')
        # 10/20 읽기 중요도(kz/kz_imp.py): 음독·훈독을 BJT 중요 순으로 다시 놓고 순위(①②…)·흘려보기·대표 소리를 붙임
        KZ_IMP = '/home/claude/work/kz/kz_imp.json'
        if os.path.exists(KZ_IMP):
            imp = json.load(open(KZ_IMP, encoding='utf-8')); n_imp = 0
            for c, card in kc.items():
                x = imp.get(c)
                if not x: continue
                on_set, kun_set = set(card['on']), set(card['kun'])
                if not all(r in on_set for r, _, _ in x['on']) or not all(r in kun_set for r, _, _ in x['kun']): continue
                card['on'] = [r for r, _, _ in x['on']]; card['onr'] = [n for _, n, _ in x['on']]; card['ons'] = [s_ for _, _, s_ in x['on']]
                card['kun'] = [r for r, _, _ in x['kun']]; card['kunr'] = [n for _, n, _ in x['kun']]; card['kuns'] = [s_ for _, _, s_ in x['kun']]
                card['rep'] = x['rep']; n_imp += 1
            print('kanji reading importance', n_imp)
        data['kc'] = kc
        if bad: print('kanji cards skipped (shape):', ''.join(map(str, bad[:40])))
    print('kanji order', len(data['kzo']), 'cards', len(data.get('kc', {})))
# 다시 녹음하는 음성(기본 카드)의 파일 내용 해시 → 앱이 주소에 ?v= 를 붙여 기기에 저장된 옛 음성 대신 새 음성을 받음
REPO = '/home/claude/bjt-words'
if os.path.exists(REPO + '/tools/voice_jobs.json'):
    av = {}
    for j in json.load(open(REPO + '/tools/voice_jobs.json', encoding='utf-8')):
        f = os.path.join(REPO, j['f'])
        if os.path.exists(f): av[j['f'][6:-4]] = hashlib.md5(open(f, 'rb').read()).hexdigest()[:8]
    # 10/15: 본편 음성 중 내용이 바뀐 파일(10/4 교체 53개 + 오독 다시 녹음)도 주소에 해시를 붙여 기기의 옛 저장본을 바꿈
    xv = REPO + '/tools/audio_versioned.json'
    if os.path.exists(xv):
        for k in json.load(open(xv, encoding='utf-8')):
            f = REPO + '/audio/' + k + '.mp3'
            assert os.path.exists(f), f
            av[k] = hashlib.md5(open(f, 'rb').read()).hexdigest()[:8]
    # 10/20 한자 음성: audio/k/<한자 코드>.mp3(대표 소리) · audio/kr/<읽기 코드>.mp3(읽기마다) — 처음부터 ?v=해시
    for sub in ('k', 'kr'):
        dd = REPO + '/audio/' + sub
        if os.path.isdir(dd):
            for fn in sorted(os.listdir(dd)):
                if fn.endswith('.mp3'): av[sub + '/' + fn[:-4]] = hashlib.md5(open(dd + '/' + fn, 'rb').read()).hexdigest()[:8]
    data['av'] = av; data['avh'] = hashlib.md5(json.dumps(av, sort_keys=True).encode()).hexdigest()[:8]
    print('audio versions', len(av), data['avh'])
js = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
html = tpl.replace('__BJT_DATA__', js).replace("'__APP_MODE__'", repr(mode)).replace('__APP_URL__', app_url).replace('__AUDIO_MB__', audio_mb)
import datetime
build = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime('%m/%d %H:%M')
html = html.replace('__BUILD__', build)
assert '__BJT_DATA__' not in html and '__APP_MODE__' not in html and '__BUILD__' not in html
os.makedirs(outdir, exist_ok=True)
open(os.path.join(outdir, 'index.html'), 'w', encoding='utf-8').write(html)
ver = hashlib.sha1(html.encode('utf-8')).hexdigest()[:10]
sw = open('/home/claude/work/app/sw.tpl.js', encoding='utf-8').read().replace('__SW_VERSION__', ver)
open(os.path.join(outdir, 'sw.js'), 'w', encoding='utf-8').write(sw)
print('built', outdir, len(html), 'sw', ver)
