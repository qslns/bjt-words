"""카드 공통 함수 (11/13, 확장 P2~): 표제 루비 hw · 한자 목록 kj · 예문 글 t 만들기, 루비 읽기 파싱, 한자 판별
check_cards.py(검사)·append_cards.py(합치기)가 같이 씀. 지금 덱 2,331개에서 hw·kj·t 재현을 시험으로 확인함(make_hw_test)."""
import re, json
KANJI_RE = re.compile(r'[㐀-䶿一-鿿豈-﫿々〆]')
def is_kanji(c): return bool(KANJI_RE.match(c))
def hira(s): return ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in s)
def kata(s): return ''.join(chr(ord(c) + 0x60) if 'ぁ' <= c <= 'ゖ' else c for c in s)
def chunks(w):
    """표제어를 (한자 덩어리 여부, 글) 조각으로"""
    out = []
    for c in w:
        k = is_kanji(c)
        if out and out[-1][0] == k: out[-1][1] += c
        else: out.append([k, c])
    return [(k, s) for k, s in out]
def kj_of(w):
    out = []
    for c in w:
        if is_kanji(c) and c not in '々〆' and c not in out: out.append(c)
    return out
def align_reading(w, r):
    """w(한자+가나)와 읽기 r을 맞춰 한자 덩어리마다 읽기. 못 맞추면 None"""
    w0 = w.strip('〜～')
    segs = chunks(w0)
    pat = ''.join('(.+?)' if k else '(' + re.escape(hira(s)) + ')' for k, s in segs)
    m = re.fullmatch(pat, hira(r))
    if not m: return None
    return [(k, s, g) for (k, s), g in zip(segs, m.groups())]
def make_hw(w, r, kr):
    """표제 루비. 규칙(11/13 검증): 한자 덩어리마다 [덩어리|kr 읽기 이어 붙인 것], 가나는 그대로.
    kr가 비면(熟字訓) 덩어리 전체에 r의 해당 부분. 〜로 시작하면 〜는 앞에 그대로"""
    pre = suf = ''
    if w[:1] in '〜～': pre, w = w[0], w[1:]
    if w[-1:] in '〜～': suf, w = w[-1], w[:-1]
    segs = chunks(w)
    if kr:
        q = [list(x) for x in kr]; out = ''
        for k, s in segs:
            if not k: out += s; continue
            rd, i = '', 0
            while i < len(s):
                if not q: return None
                kk, rr = q[0]
                if s.startswith(kk, i): rd += rr; i += len(kk); q.pop(0)
                elif s[i] == '々' and kk != '々': rd += ''; i += 1   # 々는 kr에 따로 없을 수 있음(앞 읽기에 포함)
                else: return None
            out += '[' + s + '|' + rd + ']'
        if q: return None
        return pre + out + suf
    al = align_reading(w, r)
    if not al: return None
    return pre + ''.join('[' + s + '|' + g + ']' if k else s for k, s, g in al) + suf
RUBY = re.compile(r'\[([^\[\]|]+)\|([^\[\]|]+)\]')
def strip_ruby(j, braces=True):
    t = RUBY.sub(lambda m: m.group(1), j)
    return t.replace('{', '').replace('}', '') if braces else t
def ruby_reading(j):
    """루비 글 → 읽기(가나) 글: 한자 부분은 루비 읽기로"""
    return RUBY.sub(lambda m: m.group(2), j).replace('{', '').replace('}', '')
def ruby_segments(j):
    """(base, reading, start, end in plain text, in_target) 목록 — plain = strip_ruby(j)"""
    out, plain, i, tgt = [], '', 0, False
    while i < len(j):
        c = j[i]
        if c == '{': tgt = True; i += 1; continue
        if c == '}': tgt = False; i += 1; continue
        if c == '[':
            m = RUBY.match(j, i)
            if m:
                out.append((m.group(1), m.group(2), len(plain), len(plain) + len(m.group(1)), tgt))
                plain += m.group(1); i = m.end(); continue
        plain += c; i += 1
    return out, plain
