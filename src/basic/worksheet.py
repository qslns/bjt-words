"""기본 카드 작성용 시트: worksheet.py a b > file"""
import json, re, sys, collections
A = json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8'))
K = A['kanji']; W = A['words']
byid = {w['id']: w for w in W}
def plain(j): return re.sub(r'[{}]', '', re.sub(r'\[([^|\]]+)\|[^\]]*\]', r'\1', j))
def kana(s): return re.sub(r'[〜~（）()・]', '', s)
a, b = int(sys.argv[1]), int(sys.argv[2])
# 덱 전체(본편+기본) 읽기 → 단어
byr = collections.defaultdict(list)
for w in W: byr[kana(w['r'])].append(w)
L = {o['bn']: o for o in json.load(open('/home/claude/work/basic/list.json', encoding='utf-8'))}
def tag(w): return f"No.{w['ord']+1}" if w.get('ord') is not None else f"기본{w['bn']}"
for w in sorted([w for w in W if w.get('bn') and w.get('ord') is None and a <= w['bn'] <= b], key=lambda w: w['bn']):
    o = L[w['bn']]
    print(f"#{w['bn']} {w['w']}({w['r']}) [{w['c']}] {w['m']} | ko={w['ko']} | lv{o.get('lv')} | en: {o.get('en','')[:70]}")
    if w.get('p'): print(f"  P: {w['p']}")
    for c in dict.fromkeys(w['kj']):
        k = K.get(c, {})
        print(f"  K {c}={k.get('h')} · {k.get('s')} · {k.get('x')}")
    for i, e in enumerate(w['e']):
        print(f"  {i+1}) {plain(e['j'])} | {e['k']}")
    hom = [x for x in byr[kana(w['r'])] if x['id'] != w['id']]
    if hom: print('  同音: ' + ', '.join(f"{x['w']}({tag(x)} {x['m']})" for x in hom))
    # 같은 첫 한자 + 비슷한 읽기(자·타동사 짝 후보)
    if w['kj']:
        c0 = w['kj'][0]
        sib = [x for x in W if x['id'] != w['id'] and x['kj'][:1] == [c0] and len(x['w']) <= 4 and re.search('[ぁ-ん]$', x['w']) and re.search('[ぁ-ん]$', w['w']) and x['r'][:1] == w['r'][:1]]
        if sib: print('  짝후보: ' + ', '.join(f"{x['w']}({tag(x)} {x['m']})" for x in sib[:6]))
