#!/usr/bin/env python3
"""새 한자 항목의 음·훈 걸러내기 (11/13) — KANJIDIC에서 온 드문 읽기(米 メエトル·涼 まことに·姉 はは 등) 빼기
남기는 읽기: ① 덱 단어 kr에 쓰인 읽기 ② JMdict 흔한 말(우선순위 표시 있는 표기)에 그 읽기로 쓰인 것
  훈 'すず(しい)': 그 한자로 시작하고 뒤가 送り仮名로 이어지는 흔한 말의 읽기가 すず로 시작 / 훈 'どろ': 그 한자로 시작하는 흔한 말 읽기가 どろ로 시작
  음 'ベイ': 그 한자가 든 흔한 한자어(전부 한자) 읽기에 べい(또는 촉음·탁음 바뀐 꼴)가 들어 있음
더하는 읽기: 덱 kr에 있는데 목록에 없는 훈(捕まえる → つか(まえる))
남는 게 없으면 음은 첫 음 하나를 남김.
usage: python3 kanji_readings_filter.py KANJI_IN.json KANJI_OUT.json DATA.json [더 볼 카드 jsonl …] → 바뀐 것 출력"""
import sys, json, sqlite3, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cardlib import is_kanji, hira
DB = '/usr/local/lib/python3.13/site-packages/jamdict_data/jamdict.db'
c = sqlite3.connect(DB)
def common_pairs(ch):
    q = """select distinct k.text, n.text from Kanji k join KJP p on p.kid = k.ID join Kana n on n.idseq = k.idseq
           where k.text like ?"""
    return c.execute(q, ('%' + ch + '%',)).fetchall()
# 이 방법으로 못 잡는 常用 읽기(흔한 표시가 다른 표기에 붙어 있음) — 손으로 남김
KEEP = {'弾': {'たま'}, '笑': {'え(む)'}}
VOICE = str.maketrans('かきくけこさしすせそたちつてとはひふへほ', 'がぎぐげござじずぜぞだぢづでどばびぶべぼ')
HP = str.maketrans('はひふへほ', 'ぱぴぷぺぽ')
def on_forms(on, sib=()):
    """sib: 같은 한자의 다른 음(히라가나) — 탁음으로 바꾼 꼴이 다른 음과 같으면 그 꼴은 안 씀(タン→だん은 ダン 몫)"""
    h = hira(on); fs = {h}
    for v in (h.translate(VOICE), h.translate(HP)):
        if v not in sib: fs.add(v)
    if len(h) >= 2 and h[-1] in 'つちくき': fs |= {x[:-1] + 'っ' for x in list(fs)}
    return fs
def kun_parts(k):
    m = re.fullmatch(r'([^()]+)\(([^()]+)\)', k)
    return (m.group(1), m.group(2)) if m else (k, '')
def main():
    kin, kout, data = sys.argv[1:4]; extra = sys.argv[4:]
    K = json.load(open(kin, encoding='utf-8'))
    D = json.load(open(data, encoding='utf-8'))
    words = list(D['words'])
    for f in extra:
        for l in open(f, encoding='utf-8'):
            if l.strip(): words.append(json.loads(l))
    used = {}   # 한자 → {(읽기, 뒤 送り仮名)}
    for w in words:
        kr = w.get('kr') or []; pos = 0; ww = w['w'].replace('〜', '')
        for chunk, r in kr:
            i = ww.find(chunk, pos)
            if i < 0: continue
            pos = i + len(chunk)
            if len(chunk) == 1:
                ok = ''
                j = pos
                while j < len(ww) and not is_kanji(ww[j]) and ww[j] not in '々': ok += ww[j]; j += 1
                used.setdefault(chunk, set()).add((r, ok))
    log = []
    for ch, e in K.items():
        P = common_pairs(ch)
        uk = used.get(ch, set()); urd = {r for r, _ in uk}
        on2 = []
        ons = e.get('on', []); sibh = {hira(o) for o in ons}
        for on in ons:
            fs = on_forms(on, sibh - {hira(on)})
            # 더 긴 다른 음(デ ⊂ デイ)의 꼴이 들어 있는 읽기는 이 음의 증거로 안 셈
            longer = [f2 for o2 in ons if o2 != on for f2 in on_forms(o2, sibh - {hira(o2)}) if any(f in f2 and f != f2 for f in fs)]
            def ev(kn):
                kh = hira(kn)
                for f2 in longer: kh = kh.replace(f2, '\u3000')
                return any(f in kh for f in fs)
            att = any(all(is_kanji(x) or x == '々' for x in kt) and len(kt) > 1 and ev(kn) for kt, kn in P) or any(kt == ch and hira(kn) in fs for kt, kn in P)
            if att or hira(on) in urd or any(f in urd for f in fs): on2.append(on)
        if not on2 and e.get('on'): on2 = e['on'][:1]
        kun2 = []
        for k in e.get('kun', []):
            st, ok = kun_parts(k)
            if ok: att = any((kt.startswith(ch + ok[0]) and hira(kn).startswith(st)) or (kt.startswith(ch) and len(kt) > 1 and is_kanji(kt[1]) and hira(kn).startswith(st + ok)) for kt, kn in P)
            else: att = any(kt.startswith(ch) and (len(kt) == 1 or is_kanji(kt[1]) or kt[1] in '々') and hira(kn).startswith(st) for kt, kn in P)
            if att or st in urd or k in KEEP.get(ch, ()): kun2.append(k)
        have = {kun_parts(k)[0] for k in kun2} | {kun_parts(k)[0] for k in e.get('kun', [])}
        for r, ok in sorted(uk):
            if r in have or any(r in on_forms(o) or r == hira(o) for o in e.get('on', [])): continue
            # 더하는 건 送り仮名 있는 훈만(捕まえる → つか(まえる)). 送り仮名 없는 것(灰皿 ざら·お腹 なか)·兄さん 같은 특별 읽기는 안 더함
            if not ok or not re.fullmatch(r'[ぁ-ゖ]+', ok) or ok == 'さん': continue
            if any(r == kun_parts(x)[0].translate(VOICE) for x in e.get('kun', [])): continue
            nk = f'{r}({ok})' if ok else r
            if not any(kun_parts(x)[0] == r for x in kun2): kun2.append(nk); have.add(r)
        if on2 != e.get('on', []) or kun2 != e.get('kun', []):
            log.append({'c': ch, 'on': [e.get('on', []), on2], 'kun': [e.get('kun', []), kun2]})
        e['on'], e['kun'] = on2, kun2
    json.dump(K, open(kout, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    for x in log:
        ro = [o for o in x['on'][0] if o not in x['on'][1]]; rk = [k for k in x['kun'][0] if k not in x['kun'][1]]; ak = [k for k in x['kun'][1] if k not in x['kun'][0]]
        print(x['c'], ('뺀 음 ' + '·'.join(ro)) if ro else '', ('뺀 훈 ' + '·'.join(rk)) if rk else '', ('더한 훈 ' + '·'.join(ak)) if ak else '')
    print('바뀐 한자', len(log), '/', len(K))
if __name__ == '__main__':
    main()
