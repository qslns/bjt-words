"""예문 후리가나 → 기대 음소열(구간 표시 포함).
후리가나 구간 [漢字|かな]은 그 かな 그대로(음성이 읽어야 할 정답), 나머지(조사·가나·숫자·조수사·영문)는 pyopenjtalk로 읽기.
반환: units = [(kind, text, phonemes)]  kind = 'seg'(후리가나 구간) | 'txt'"""
import re, pyopenjtalk
from kana import to_ph, kata2hira
SEG = re.compile(r'\[([^|\]]+)\|([^\]]*)\]')
def hira2kata(s): return ''.join(chr(ord(c) + 0x60) if 'ぁ' <= c <= 'ゖ' else c for c in s)
PUNCT = set('、。！？「」『』（）()…・：:【】　 ,.!?-')
def units_of(j):
    j = j.replace('{', '').replace('}', '')
    parts = []; pos = 0
    for m in SEG.finditer(j):
        if m.start() > pos: parts.append(('txt', j[pos:m.start()]))
        parts.append(('seg', m.group(1), m.group(2))); pos = m.end()
    if pos < len(j): parts.append(('txt', j[pos:]))
    # 문맥을 살려 한 번에 읽기: 후리가나 구간은 가타카나로 바꿔 넣고, 토큰의 위치로 구간을 되찾음
    text = ''; spans = []
    for p in parts:
        s = hira2kata(p[2]) if p[0] == 'seg' else p[1]
        spans.append((len(text), len(text) + len(s))); text += s
    feats = pyopenjtalk.run_frontend(text)
    tok = []; c = 0
    for f in feats:
        s = f['string']; i = text.find(s, c) if s else -1
        if i < 0: i = c
        tok.append((i, i + len(s), f)); c = i + len(s)
    units = []; allph = []
    for p, (a, b) in zip(parts, spans):
        if p[0] == 'seg':
            units.append(('seg', p[1] + '|' + p[2], to_ph(p[2], allph[-3:]))); allph += units[-1][2]
        else:
            ph = []
            for (ta, tb, f) in tok:
                if tb <= a or ta >= b: continue
                if ta >= a and tb <= b:
                    pr = f['pron'].replace('’', '')
                    if not pr or pr == '*': continue   # 기호(、。)는 to_ph가 무시, 영문자(A→エー)는 읽기 살림
                    ph += to_ph(pr, (allph + ph)[-3:])
                else:   # 구간 경계에 걸친 토큰: 이 부분 글자만 그대로 가나로
                    ph += to_ph(text[max(a, ta):min(b, tb)], (allph + ph)[-3:])
            units.append(('txt', p[1], ph)); allph += ph
    return units
if __name__ == '__main__':
    import json, sys
    d = json.load(open('/home/claude/work/build/data_app.json', encoding='utf-8'))
    for w in d['words'][:3] + [x for x in d['words'] if x['id'] in (404, 38)]:
        for e in w['e'][:2]:
            U = units_of(e['j']); print(e['j']); print('   ', ' | '.join(f"{t}:{' '.join(p)}" for k, t, p in U))
            print('    g2p(t):', pyopenjtalk.g2p(e['t']))
