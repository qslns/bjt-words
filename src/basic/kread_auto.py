"""pick_readings2.py를 새 한자(기본 카드)용으로 돌린다: 덱 = 1500 + 기본 카드, 대상 = 새 한자만. 결과는 basic/kread_auto.json"""
import json, re, sys
src = open('/home/claude/work/kanji/pick_readings2.py', encoding='utf-8').read()
L = json.load(open('/home/claude/work/basic/list.json', encoding='utf-8'))
H = json.load(open('/home/claude/work/basic/headinfo.json', encoding='utf-8'))
NEWK = [c for c in json.load(open('/home/claude/work/basic/newkanji.json', encoding='utf-8')) if c != '々']
D0 = json.load(open('/home/claude/work/build/data1500g.json', encoding='utf-8'))
from jamdict import Jamdict
jam = Jamdict()
def k2h(s): return ''.join(chr(ord(ch) - 0x60) if 'ァ' <= ch <= 'ヶ' else ch for ch in s)
words = list(D0['words'])
for o in L:
    if 'share' in o: continue
    h = H[str(o['bn'])]
    words.append({'w': o['w'].replace('〜', ''), 'kr': h['kr'], 'ord': 5000 + o['bn']})
kanji = {}
for c in NEWK:
    r = jam.lookup(c).chars
    on, kun = [], []
    if r and r[0].rm_groups:
        rg = r[0].rm_groups[0]
        on = [x.value for x in rg.readings if x.r_type == 'ja_on' and not x.value.startswith('-') and not x.value.endswith('-')]
        for x in rg.readings:
            if x.r_type != 'ja_kun': continue
            v = x.value.strip('-'); st, _, ok = v.partition('.')
            f = f'{st}({ok})' if ok else st
            if f not in kun: kun.append(f)
    kanji[c] = {'on': on, 'kun': kun}
NS = {'__name__': 'kr_b'}
src = src.replace("D = json.load(open('/home/claude/work/build/data1500g.json', encoding='utf-8'))", "D = __D__")
src = src.replace("open('/home/claude/work/kanji/readings_new.json', 'w', encoding='utf-8')", "open('/home/claude/work/basic/kread_auto.json', 'w', encoding='utf-8')")
src = src.replace("open('/home/claude/work/kanji/readings_diff.txt', 'w', encoding='utf-8')", "open('/home/claude/work/basic/kread_diff.txt', 'w', encoding='utf-8')")
src = src.replace("open('/home/claude/work/kanji/readings_scores.json', 'w', encoding='utf-8')", "open('/home/claude/work/basic/kread_scores.json', 'w', encoding='utf-8')")
src = src.replace("for line in open('/home/claude/work/kanji/readings_manual.tsv', encoding='utf-8'):", "for line in []:")
NS['__D__'] = {'words': words, 'kanji': kanji}
exec(compile(src, 'pick_readings_b', 'exec'), NS)
