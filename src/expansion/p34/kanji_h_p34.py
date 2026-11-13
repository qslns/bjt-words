# P3+P4 새 한자(앱 950·옛 407·P2 99 밖) 훈음 h — 음은 KANJIDIC2 korean_h로 확인. 부분(4부~)마다 늘려 감
import json, sys, re
sys.path.insert(0, '/home/claude/work/expansion/tools')
from kanji_ref import ref
H = dict(x.split(':') for x in '''柵:울타리 책|桜:앵두나무 앵|粉:가루 분|胸:가슴 흉|腰:허리 요|裂:찢을 렬|銃:총 총'''.split('|'))
d = json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8')); K = d['kanji']
OK = json.load(open('/home/claude/work/expansion/old_kanji_extra.json', encoding='utf-8'))
radbn = {}
for src in (K, OK):
    for c, e in src.items():
        if e.get('b') and e.get('bn'): radbn.setdefault(e['b'], e['bn'])
def kun_fmt(k):
    k = k.strip('-')
    return re.sub(r'^([^.]+)\.(.+)$', r'\1(\2)', k)
out, bad = {}, []
for c, h in H.items():
    r = ref(c)
    if h.split()[-1] not in r['kh']: bad.append((c, h, r['kh']))
    out[c] = {'h': h, 'b': r['rad'], 'bn': radbn.get(r['rad'], ''), 's': '', 'x': '', 'on': r['on'], 'kun': list(dict.fromkeys(kun_fmt(k) for k in r['kun'] if k.strip('-'))), 'n': r['n']}
print('음이 KANJIDIC과 다름:', bad)
json.dump(out, open('/home/claude/work/expansion/p34/kanji_new_p34.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(out))
