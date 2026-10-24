#!/usr/bin/env python3
"""전체 카드 자동 점검(사람이 볼 목록 뽑기): python3 review_scan.py > review/flags.txt"""
import json, glob, re, sys, collections, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import kzc
d = kzc.data(); K = d['K']
cards = {}
src = {}
for f in ['gold.json'] + sorted(glob.glob(os.path.join(HERE, 'batches/*.json'))):
    for e in json.load(open(f, encoding='utf-8')):
        cards[e['c']] = e; src[e['c']] = os.path.basename(f)
REF = kzc.REF()
def comps(c):
    """이 한자 안에 있는 부품 글자들(KanjiVG 이름·원래 글자 + MakeMeAHanzi 분해)"""
    out = {c}
    def walk(n):
        for k in n['kids']:
            if k['el']: out.add(k['el'])
            if k['orig']: out.add(k['orig'])
            walk(k)
    walk(kzc.kvg(c)['root'])
    dec = (REF.get(c) or {}).get('decomposition', '')
    for ch in dec:
        if ch not in '⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻？': out.add(ch)
    return out
CJK = re.compile(r'[⺀-⿟㐀-䶿一-鿿豈-﫿\U00020000-\U0002FFFF]')
flags = collections.defaultdict(list)
KANA = re.compile(r'[ぁ-ゖ]+')
on_all = {}
for c, e in cards.items():
    k = K[c]; hun = k['h'].lstrip('? ').strip(); eum = hun.split()[-1]
    cs = comps(c) | set(kzc.RADFIX_SRC) | set('辶阝彐犭爫亻氵扌忄艹罒')
    # 1) hook 괄호 속 한자가 실제 부품인지
    for m in re.finditer(r'\(([^)]*)\)', e['hook']):
        for ch in CJK.findall(m.group(1)):
            if ch not in cs and kzc.fixt(ch) not in cs: flags[c].append(f'hook 괄호 한자 {ch}가 부품 목록에 없음 (부품: {"".join(sorted(cs - set(kzc.RADFIX_SRC)))[:40]})')
    # 2) 소리 줄: 한국음 일치, 받침 규칙
    snd = e['snd']
    m = re.search(r'한국음\s*\*\*(.+?)\*\*', snd)
    if m and m.group(1) != eum: flags[c].append(f'snd 한국음 {m.group(1)} ≠ 앱 음 {eum}')
    rule = re.search(r'받침\s*([ㄱ-ㅎ])', snd)
    if rule:
        last = eum[-1]; code = ord(last) - 0xAC00
        jong = code % 28 if 0 <= code < 11172 else -1
        JONG = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
        if jong < 0 or JONG[jong] != rule.group(1): flags[c].append(f'snd 받침 규칙 {rule.group(1)} 인데 음 {eum}의 받침은 {JONG[jong] if jong >= 0 else "?"}')
    on_h = [kzc.to_hira(x) for x in k['on']]
    kun_h = [kzc.to_hira(re.sub(r'[()（）.\-]', '', x)) for x in k['kun']]
    # 3) 마지막 결과 읽기 · 소리 줄의 이 한자 읽기
    # 4) 이상한 한글 음차 의심(일본어 소리를 한글로)
    for fld in ('hook', 'bridge', 'snd', 'basic'):
        t = e.get(fld, '') or ''
        if re.search(r'(니치|지쓰|지츠|쓰우|츄우|쥬우|큐우|슈우|쇼우|토우|코우|오오|니혼|다나카|사마|상\b|데스|마스)', t): flags[c].append(f'{fld}에 일본어 음차 의심: {t[:50]}')
    for p in ('p1', 'p2', 'p3'):
        t = e[p]['cap']
        if re.search(r'(니치|지쓰|츄우|쥬우|큐우|슈우|쇼우|토우|코우|데스|마스)', t): flags[c].append(f'{p}.cap 음차 의심: {t}')
    # 5) 확장 A 한자(드문 글자) 화면 글
    txt = ' '.join([e['hook'], e.get('bridge', ''), e.get('basic', ''), e['snd']] + [e[p]['cap'] for p in ('p1', 'p2', 'p3')] + [json.dumps(e.get('tree', []), ensure_ascii=False)])
    rare = sorted({ch for ch in txt if 0x3400 <= ord(ch) <= 0x4DBF})
    if rare: flags[c].append('확장A 글자(아이패드 글꼴 확인): ' + ''.join(rare))
    # 6) 장면 그림 항목 수
    for p in ('p1', 'p3'):
        n = len(e[p].get('scene', []))
        if n > 9: flags[c].append(f'{p} 그림 항목 {n}개(복잡)')
    if len(e['hook']) > 52: flags[c].append(f'hook 김 {len(e["hook"])}자')
# 7) 같은 부품 다른 이름
names = collections.defaultdict(collections.Counter)
for c, e in cards.items():
    for st in e.get('tree') or []:
        for pt in st['parts']:
            el = kzc.last_el(pt['p'], c)
            if el: names[el][pt['n']] += 1
incons = {el: dict(cn) for el, cn in names.items() if len(cn) > 1}
# 8) 같은 hook
hooks = collections.Counter(e['hook'] for e in cards.values())
for c, e in cards.items():
    if hooks[e['hook']] > 1: flags[c].append('다른 카드와 hook 똑같음')
order = d['order']
for c in order:
    if flags.get(c): print(f'{c} ({src[c]}):', ' | '.join(flags[c]))
print()
print('== 같은 부품에 다른 이름 ==')
for el, cn in sorted(incons.items(), key=lambda x: -sum(x[1].values())):
    print(el, cn)
print(f'\n플래그 카드 {len(flags)} / {len(cards)}')
