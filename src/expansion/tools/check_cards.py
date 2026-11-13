#!/usr/bin/env python3
"""카드 검사기 (11/13, 확장 P2~ · HANDOFF 7절 · CARD_SPEC)
쓰기: python3 check_cards.py CARDS.jsonl [CARDS2.jsonl …] [--sheet SHEET.json] [--others 'GLOB'] [--json OUT.json] [--quiet]
  CARDS.jsonl  작성자가 넘긴 카드(한 줄에 하나, CARD_SPEC 1절 꼴)
  --sheet      작업 시트(id·w·r 확인). basic_final.json 꼴([{id,w,r,…}])이나 카드 시트([{id,w,r,…,"kanji":…}])
  --others     다른 묶음의 새 카드(같은 표제·비슷한 예문 확인용), 예: '/home/claude/agents/*/out/*.jsonl'
오류(E)는 고쳐야 넘김, 경고(W)는 사람·검수자가 판단. 끝 줄: '#SUMMARY 카드 n · 오류 n · 경고 n', 오류 있으면 종료 코드 1.
읽는 것: /home/claude/work/build/data_app.json(지금 덱·한자) · expansion/old_words_2312.json(복원 표제) · old_kanji_extra.json · p2/kanji_new*.json(새 한자, 있으면) · gloss_dict.json
"""
import sys, os, re, json, glob, argparse, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cardlib import is_kanji, hira, kj_of, make_hw, strip_ruby, ruby_reading, ruby_segments, RUBY, chunks, align_reading
import fugashi

WORK = '/home/claude/work'
E_DIR = WORK + '/expansion'
TIERS = {'S', 'A', 'B', 'K'}
CATS = set('org mtg sch tel doc deal money sales graph hr trouble verb formal kata keigo it gen'.split())
SCENES = set('tel mtg talk visit biz graph doc mail notice report news'.split())
NO_GLOSS = set('する いる この なる ある こと おる ござる そう よう その 私 いい よる 知る くる いう うち もの いつ ところ それ これ ほう なに 為る 居る 有る 成る 言う 来る 良い 事 物 内 所 方 何 御座る 御'.split())
COUNTERS = set('円 割 度 階 週間 か月 ヶ月 カ月 個 人 名 社 件 台 枚 冊 本 回 倍 歳 才 時 時間 分 秒 日 月 年 年間 日間 号 位 点 品 種 代 期 泊 着 軒 杯 匹 店 店舗 部 課 箱 通 便 個所 か所 箇所 カ所 ケ所 番 番目 次 名様 人分 円台 本目 年度 月末 日目 階建て 万 億 千 百 兆 キロ メートル グラム パーセント 時半 分間 年代 ドル ユーロ ウォン 元 字 行 ページ 枚目 回目 週 週目 週末 期目'.split())
DIGIT = re.compile(r'[0-9０-９]')
NUMK = re.compile(r'[0-9０-９〇一二三四五六七八九十百千万億兆]')
HANGUL = re.compile(r'[가-힣ㄱ-ㆎ]')
KATA = re.compile(r'[ァ-ヺ]')
HIRA_ONLY = re.compile(r'^[ぁ-ゖーー]+$')
KATA_ONLY = re.compile(r'^[ァ-ヺーー・]+$')

def load_json(p, default=None):
    try: return json.load(open(p, encoding='utf-8'))
    except FileNotFoundError: return default

DATA = load_json(WORK + '/build/data_app.json')
CUR = DATA['words']; K = dict(DATA['kanji'])
OLD = load_json(E_DIR + '/old_words_2312.json', [])
for c, v in (load_json(E_DIR + '/old_kanji_extra.json', {}) or {}).items(): K.setdefault(c, v)
for p in sorted(glob.glob(E_DIR + '/p*/kanji_new*.json')):
    for c, v in (load_json(p, {}) or {}).items(): K.setdefault(c, v)
GLOSS = load_json(E_DIR + '/gloss_dict.json', {})
KREF = load_json(E_DIR + '/kanji_ref_cache.json', {}) or {}   # KANJIDIC2 읽기(사전 항목에 빠진 훈독 보충용)
TG = fugashi.Tagger()

# ---------- 한국 한자음 ----------
def eums(c):
    """한자 c의 음(훈음 h의 마지막 음절, '/'로 여러 개)"""
    k = K.get(c)
    if not k or not k.get('h'): return None
    out = []
    for part in re.split(r'\s*/\s*', k['h'].replace('?', '').strip()):
        part = part.strip()
        if part: out.append(part.split()[-1][-1])
    return out or None
CHO = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
def dueum(s):
    """두음법칙 변형(첫 음절): ㄹ→ㄴ/ㅇ, ㄴ→ㅇ (ㅑㅕㅖㅛㅠㅣ 앞)"""
    o = ord(s) - 0xAC00
    if not 0 <= o < 11172: return {s}
    ch, ju, jo = o // 588, (o % 588) // 28, o % 28
    yv = ju in (2, 6, 7, 12, 17, 20)   # ㅑ ㅕ ㅖ ㅛ ㅠ ㅣ
    mk = lambda c: chr(0xAC00 + c * 588 + ju * 28 + jo)
    out = {s}
    if ch == 5: out.add(mk(11 if yv else 2))   # ㄹ
    if ch == 2 and yv: out.add(mk(11))         # ㄴ
    return out

# ---------- 일본 한자 읽기 ----------
VOICE = dict(zip('かきくけこさしすせそたちつてとはひふへほ', 'がぎぐげござじずぜぞだぢづでどばびぶべぼ'))
HPV = dict(zip('はひふへほ', 'ぱぴぷぺぽ'))
def reading_variants(c):
    k = K.get(c)
    kr_ = KREF.get(c) or {}
    if not k and not kr_: return None
    k = dict(k or {})
    k['on'] = list(k.get('on', []) or []) + [x for x in kr_.get('on', []) or []]
    k['kun'] = list(k.get('kun', []) or []) + [re.sub(r'^([^.]+)\.(.+)$', r'\1(\2)', x.strip('-')) for x in kr_.get('kun', []) or [] if x.strip('-')]
    base = set()
    for o in k.get('on', []) or []: base.add(hira(o.replace('-', '').replace('.', '')))
    I_ROW = dict(zip('うくぐすつぬぶむる', 'いきぎしちにびみり'))
    for o in k.get('kun', []) or []:
        o = re.sub(r'[()（）]', '|', o).replace('-', '')
        stem = o.split('|')[0].split('.')[0]
        whole = o.replace('|', '').replace('.', '')
        if stem: base.add(hira(stem))
        if whole: base.add(hira(whole))
        oku = hira(whole[len(stem):]) if whole.startswith(stem) else ''
        if stem and oku:
            base.add(hira(stem) + I_ROW.get(oku[0], oku[0]) if len(oku) == 1 else hira(stem) + oku[:-1] + I_ROW.get(oku[-1], oku[-1]))   # 연용형(合う→あい, 組む→くみ)
            base.add(hira(stem) + 'っ')
    out = set()
    for r in base:
        if not r: continue
        vs = {r}
        if r[0] in VOICE: vs.add(VOICE[r[0]])
        if r[0] in HPV: vs.add(HPV[r[0]] + r[1:])
        vs = {v if len(v) == len(r) else v for v in vs} | {VOICE[r[0]] + r[1:] if r[0] in VOICE else r}
        if r[0] in HPV: vs.add(HPV[r[0]] + r[1:])
        more = set()
        for v in vs:
            more.add(v)
            if len(v) >= 2 and v[-1] in 'くきちつ': more.add(v[:-1] + 'っ')
            if v.endswith('ち') or v.endswith('つ'): more.add(v[:-1])
        out |= more
    return out

# ---------- 문장 토큰 ----------
def toks(plain):
    out, pos = [], 0
    for t in TG(plain):
        s = t.surface; i = plain.find(s, pos)
        if i < 0: i = pos
        f = t.feature
        lem = (f.lemma or s).split('-')[0]
        lf = getattr(f, 'lForm', None)
        out.append(dict(s=s, a=i, b=i + len(s), kana=hira(f.kana) if f.kana and f.kana != '*' else None, lemma=lem, lread=hira(lf) if lf and lf != '*' else None, p1=f.pos1, p2=f.pos2))
        pos = i + len(s)
    return out

def bigrams(s):
    s = re.sub(r'[、。，．・「」『』（）()！？!?\s]', '', s)
    return {s[i:i + 2] for i in range(len(s) - 1)}
def jacc(a, b): return len(a & b) / max(1, len(a | b))

# 지금 덱·복원 예문(비슷한 문장 확인)
EXIST_SENT = []
for w in CUR: EXIST_SENT += [(strip_ruby(e['j']), 'No' + str(w['id']) + ' ' + w['w'], w['id']) for e in w['e']]
EXIST_BG = [(s, who, bigrams(s), wid) for s, who, wid in EXIST_SENT]
HEAD_ALL = {w['w']: ('지금 덱', w['id']) for w in CUR}
for w in OLD: HEAD_ALL.setdefault(w['w'], ('복원 목록', w['id']))

CTX_CH = r'[方何日中後上間人行通市場気明今一会社私]'
def read_spans(segs, plain, T):
    """루비 구간을 토큰 경계까지 넓혀 (구간 글, 루비 쪽 읽기, fugashi 읽기) 중 서로 다른 것"""
    def widen(a, z):
        for t in T:
            if t['a'] < z and t['b'] > a: a, z = min(a, t['a']), max(z, t['b'])
        return a, z
    spans = []
    for b0, rd0, a, z, tg0 in segs:
        a, z = widen(a, z)
        while True:
            na, nz = a, z
            for b2, rd2, a2, z2, tg2 in segs:
                if a2 < nz and z2 > na: na, nz = min(na, a2), max(nz, z2)
            na, nz = widen(na, nz)
            if (na, nz) == (a, z): break
            a, z = na, nz
        if [a, z] not in spans: spans.append([a, z])
    out = []
    for a, z in spans:
        frag = plain[a:z]
        if DIGIT.search(frag): continue
        rr, i2 = '', a
        while i2 < z:
            sg = next((x for x in segs if x[2] == i2), None)
            if sg: rr += sg[1]; i2 = sg[3]
            else:
                ch = plain[i2]
                if is_kanji(ch): rr = None; break
                rr += hira(ch); i2 += 1
        if rr is None: continue
        tk = [t for t in T if t['a'] >= a and t['b'] <= z]
        if not tk or any(t['kana'] is None for t in tk): continue
        fr = ''.join(t['kana'] for t in tk)
        if hira(fr) != hira(rr): out.append((frag, rr, fr))
    return out
def build_accept():
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.accept_cache.json')
    key = '%s:%d' % (WORK + '/build/data_app.json', int(os.path.getmtime(WORK + '/build/data_app.json')))
    try:
        c = json.load(open(cache, encoding='utf-8'))
        if c.get('key') == key: return {tuple(x) for x in c['pairs']}
    except Exception: pass
    pairs = set()
    for w in CUR:
        for e in w['e']:
            segs, plain = ruby_segments(e['j'])
            for frag, rr, fr in read_spans(segs, plain, toks(plain)): pairs.add((frag, rr))
    try: json.dump({'key': key, 'pairs': sorted(pairs)}, open(cache, 'w', encoding='utf-8'), ensure_ascii=False)
    except Exception: pass
    return pairs
ACCEPT = build_accept()

class Report:
    def __init__(s): s.items = []
    def add(s, lv, cid, w, msg): s.items.append((lv, cid, w, msg))

def check_card(c, R, sheet, seen_heads, new_bg):
    cid, w = c.get('id'), c.get('w', '?')
    E = lambda m: R.add('E', cid, w, m)
    Wn = lambda m: R.add('W', cid, w, m)
    need = 'id w r m t c ko kr p y o st e pr'.split()
    miss = [k for k in need if k not in c]
    if miss: E('칸 없음: ' + ','.join(miss)); return
    extra = [k for k in c if k not in need + ['note', 'src', 'bn', 'ord', 'tw']]
    if extra: Wn('모르는 칸: ' + ','.join(extra))
    for k in ('w', 'r', 'm', 't', 'c', 'ko', 'p', 'y', 'o', 'st'):
        if not isinstance(c[k], str): E(k + ' 가 글자가 아님'); return
    if not isinstance(c['kr'], list) or not isinstance(c['e'], list) or not isinstance(c['pr'], list): E('kr·e·pr는 목록'); return
    # 시트·중복
    if sheet is not None:
        sh = sheet.get(cid)
        if not sh: E('시트에 없는 id')
        else:
            if sh['w'] != w: E('시트 표제와 다름: 시트 ' + sh['w'])
            if hira(sh.get('r', '')) != hira(c['r']): Wn('시트 읽기와 다름: 시트 ' + sh.get('r', '') + ' → ' + c['r'])
    if w in HEAD_ALL and HEAD_ALL[w][1] != cid: E('같은 표제가 이미 있음: ' + HEAD_ALL[w][0] + ' ' + str(HEAD_ALL[w][1]))
    if w in seen_heads and seen_heads[w] != cid: E('새 카드끼리 표제 중복: ' + str(seen_heads[w]))
    seen_heads.setdefault(w, cid)
    # 기본 칸
    w0 = w.strip('〜～')
    r = c['r']
    if not r or not (HIRA_ONLY.match(r) or KATA_ONLY.match(r) or re.fullmatch(r'[ぁ-ゖァ-ヺーー]+', r)): E('읽기 r은 히라가나(가타카나어는 가타카나)만: ' + r)
    if '〜' in r or '～' in r: E('r에 〜를 넣지 않음')
    if c['t'] not in TIERS: E('t 값: ' + c['t'])
    if c['c'] not in CATS: E('c 값: ' + c['c'])
    if KATA_ONLY.match(w0) and c['c'] != 'kata' and not w0 in ('カタカナ',): Wn('가타카나어인데 c가 kata 아님')
    if c['c'] == 'kata' and not c['o']: Wn('가타카나어 o(영어 원어) 빈칸')
    if c['o'] and not KATA.search(w0): Wn('o는 가타카나어만')
    if not c['m'].strip(): E('m 빈칸')
    if len(c['m']) > 30: E('m 너무 김(%d자)' % len(c['m']))
    elif len(c['m']) > 22: Wn('m 22자 넘음(%d)' % len(c['m']))
    if len(c['p']) > 90: E('p 너무 김(%d자)' % len(c['p']))
    elif len(c['p']) > 70: Wn('p 70자 넘음(%d)' % len(c['p']))
    if len(c['st']) > 130: E('st 너무 김(%d자)' % len(c['st']))
    elif len(c['st']) > 100: Wn('st 100자 넘음(%d)' % len(c['st']))
    if not c['st'].strip(): Wn('st 빈칸')
    for k in ('m', 'p', 'st', 'y'):
        for q in re.findall(r'「([^」]*)」', c[k]):
            if HANGUL.search(q) and k == 'st': Wn(k + ': 「」 안에 한국어 — 한국어엔 「」 안 씀')
    if HANGUL.search(w) or HANGUL.search(r): E('표제·읽기에 한글')
    # 한자: kr · ko · 훈음
    kjs = [ch for ch in w0 if is_kanji(ch)]
    kr = c['kr']
    for it in kr:
        if not (isinstance(it, list) and len(it) == 2 and all(isinstance(x, str) for x in it)): E('kr 꼴: [[한자, 읽기], …]'); return
        if not HIRA_ONLY.match(it[1]): E('kr 읽기는 히라가나: ' + str(it))
    hw = make_hw(w, r, kr)
    if kjs:
        if hw is None: E('kr이 표제·읽기와 안 맞음(이어 붙이면 표제 한자 부분 읽기와 같아야 함): kr=' + json.dumps(kr, ensure_ascii=False))
        else:
            if hira(ruby_reading(hw).strip('〜～')) != hira(r): E('kr로 만든 읽기 ≠ r: ' + ruby_reading(hw) + ' / ' + r)
        for it in kr:
            if len(it[0]) == 1 and is_kanji(it[0]) and it[0] not in '々':
                v = reading_variants(it[0])
                if v is None: Wn('한자 정보 없음(새 한자): ' + it[0])
                elif it[1] not in v and not any(it[1].startswith(x) or x.startswith(it[1]) for x in v if len(x) >= 2 and len(it[1]) >= 2 and abs(len(x) - len(it[1])) <= 1):
                    Wn('kr 읽기가 그 한자 음·훈에 없음: %s=%s (사전: %s)' % (it[0], it[1], '・'.join(sorted(v))[:60]))
            elif len(it[0]) > 1:
                Wn('kr 덩어리(한자 하나씩 못 나눔): ' + it[0] + '=' + it[1])
        # ko
        ko = c['ko']
        syl = [ch for ch in ko if '가' <= ch <= '힣']
        if len(syl) != len(ko.replace(' ', '')): E('ko는 한글 음절만: ' + ko)
        nk = [ch for ch in w0 if is_kanji(ch)]
        if len(syl) != len(nk): E('ko 음절 수(%d) ≠ 표제 한자 수(%d): %s' % (len(syl), len(nk), ko))
        else:
            prev = None
            for i, (ch, sy) in enumerate(zip(nk, syl)):
                if ch in '々': ok_set = {prev} if prev else None
                else:
                    es = eums(ch)
                    ok_set = None if es is None else set(es)
                if ok_set is None: Wn('ko 확인 못 함(한자 정보 없음): ' + ch)
                else:
                    cand = set()
                    for x in ok_set: cand |= dueum(x) if (i == 0 and len(nk) > 1) else {x}   # 두음법칙은 2자 이상 단어의 첫 음절만(한 글자 단어는 来 래·量 량처럼 그대로 — 지금 덱 606장 중 598장)
                    if sy not in cand:
                        if ch in K and sy in K[ch].get('h', ''): Wn('ko %s: %s의 음은 %s (훈음 %s — 맞는지 확인)' % (sy, ch, '/'.join(sorted(ok_set)), K[ch]['h']))
                        else: E('ko %s: %s의 음은 %s' % (sy, ch, '/'.join(sorted(ok_set))))
                prev = sy
        # st 훈음
        for ch in dict.fromkeys(kjs):
            k = K.get(ch)
            if not k or ch in '々': continue
            h = k['h'].replace('?', '').strip()
            m = re.search(re.escape(ch) + r'\(([^)]*)\)', c['st'])
            if m and m.group(1).strip() != h and m.group(1).strip() not in [x.strip() for x in h.split('/')]:
                Wn('st 훈음 %s(%s) ≠ 한자 카드 h(%s)' % (ch, m.group(1), h))
    else:
        if c['ko']: E('가나 표제인데 ko가 있음')
        if kr: E('가나 표제인데 kr이 있음')
    # pr
    for x in c['pr']:
        if not isinstance(x, str): E('pr은 표제어 글자로'); continue
        if x not in HEAD_ALL and x not in seen_heads and not re.match(r'^(No\.|B)\d+$', x): Wn('pr 표제를 못 찾음(지금 덱·복원·새 카드): ' + x)
    # 예문
    es = c['e']
    if not 2 <= len(es) <= 3: E('예문은 2개(필요하면 3개): %d' % len(es))
    plains = []
    for n, e in enumerate(es):
        tag = 'e%d ' % n
        if not isinstance(e, dict) or any(k not in e for k in ('s', 'j', 'k', 'g')): E(tag + '칸 s j k g'); continue
        if e['s'] not in SCENES: E(tag + '장면 s 값: ' + str(e['s']))
        j = e['j']
        if j.count('{') != 1 or j.count('}') != 1 or j.index('{') > j.index('}'): E(tag + '{ }는 정확히 한 쌍'); continue
        bad_ruby = re.findall(r'\[[^\]]*\]', RUBY.sub('', j))
        if bad_ruby: E(tag + '루비 꼴 틀림: ' + ' '.join(bad_ruby[:3]))
        segs, plain = ruby_segments(j)
        plains.append(plain)
        if HANGUL.search(plain): E(tag + '예문에 한글')
        L = len(plain)
        if L < 10 or L > 45: E(tag + '예문 길이 %d자(12~35, 최대 45)' % L)
        elif L < 12 or L > 35: Wn(tag + '예문 길이 %d자' % L)
        if not e['k'].strip() or not HANGUL.search(e['k']): E(tag + '번역 k 없음')
        for b, rd, a, z, tg in segs:
            if not any(is_kanji(ch) for ch in b): E(tag + '루비 밑글에 한자가 없음: ' + b)
            if not HIRA_ONLY.match(rd):
                if KATA_ONLY.match(rd): Wn(tag + '루비 읽기가 가타카나(외국 이름일 때만): ' + b + '|' + rd)
                else: E(tag + '루비 읽기는 히라가나: ' + rd)
            if b and not is_kanji(b[-1]) and not b[-1] in '々': Wn(tag + '루비 밑글 끝이 가나(送り仮名는 밖에): ' + b)
        covered = set()
        for b, rd, a, z, tg in segs: covered |= set(range(a, z))
        # 루비 없는 한자: 숫자 바로 뒤 조수사만 허용
        i = 0
        while i < L:
            if is_kanji(plain[i]) and i not in covered:
                s0 = i
                while i < L and is_kanji(plain[i]) and i not in covered: i += 1
                bare = plain[s0:i]
                prev = plain[:s0].rstrip()
                if prev and DIGIT.match(prev[-1]) or (prev.endswith(('.', ',', '，')) and DIGIT.match(prev[-2:-1] or 'x')):
                    if bare not in COUNTERS and not any(bare.startswith(x) for x in COUNTERS): Wn(tag + '숫자 뒤 루비 없는 한자(조수사 맞나?): ' + bare)
                else: E(tag + '루비 없는 한자: ' + bare)
            else: i += 1
        for b, rd, a, z, tg in segs:
            pv = plain[:a].rstrip()
            if pv and DIGIT.match(pv[-1]) and (b in COUNTERS or b[:1] in COUNTERS): E(tag + '숫자 뒤 조수사에 루비를 달지 않음: ' + b + '|' + rd)
            if b == '明日' and rd != 'あす': E(tag + '明日는 あす로 통일: ' + rd)
            if '会社' in b and rd.endswith('かいしゃ') and (len(b) > 2 and b.endswith('会社') or (b == '会社' and a > 0 and is_kanji(plain[a - 1]))): E(tag + '○○会社는 がいしゃ: ' + b + '|' + rd)
        # 표제 {}
        ia, ib = j.index('{'), j.index('}')
        inner = strip_ruby(j[ia + 1:ib])
        if not inner: E(tag + '{ } 안이 빔'); continue
        rstem = hira(r)
        if re.search(r'[うくぐすつぬぶむるい]$', rstem) and len(rstem) >= 2 and not is_kanji(w0[-1]): rstem = rstem[:-1]   # 활용하는 말은 어간
        irr = {'する': ('し', 'さ', 'せ', 'す'), 'くる': ('き', 'こ', 'く'), '来る': ('き', 'こ', 'く')}
        inner_rd = hira(''.join(t['kana'] or t['s'] for t in toks(inner)))
        by_read = (rstem and (rstem in hira(inner) or rstem in inner_rd)) or any(inner_rd.startswith(x) or hira(inner).startswith(x) for x in irr.get(w0, ()))
        if kjs:
            pos = 0; okk = True
            for ch in kjs:
                f = inner.find(ch, pos)
                if f < 0: okk = False; break
                pos = f + 1
            numk = all(ch in '一二三四五六七八九十' for ch in kjs[:1]) and DIGIT.search(inner)
            if not okk and not numk:
                if by_read: Wn(tag + '{ }에 표제를 가나로 씀(보조동사 등이면 괜찮음): ' + inner)
                else: E(tag + '{ } 안에 표제 한자가 순서대로 없음: ' + inner)
            elif okk and not inner.startswith(w0[0]) and not inner.startswith(kjs[0]): Wn(tag + '{ }가 표제 첫 글자로 시작하지 않음: ' + inner)
        else:
            core = w0
            need = core[:max(1, min(len(core) - 1, 4))] if len(core) > 1 else core
            if not inner.startswith(need):
                if by_read: Wn(tag + '{ }에 표제를 다른 꼴로 씀: ' + inner)
                else: E(tag + '{ }가 표제(' + core + ')로 시작해야 함: ' + inner)
        # 읽기 대조(fugashi): 지금 덱에서 검수 끝난 (구간, 읽기)는 넘김. 문맥 글자(方·何·日…)는 늘 확인
        T = toks(plain)
        for frag, rr, fr in read_spans(segs, plain, T):
            ctx = re.search(CTX_CH, frag)
            if (frag, rr) in ACCEPT and not ctx: continue
            if frag == '明日' and rr == 'あす': continue
            if frag.startswith('私') and rr.startswith('わたくし'): continue
            Wn(tag + '루비 읽기 확인: %s = %s (fugashi %s)%s' % (frag, rr, fr, ' (문맥 읽기 주의 글자' + (', 지금 덱에도 있는 읽기' if (frag, rr) in ACCEPT else '') + ')' if ctx else ''))
        # 단어 풀이 g
        g = e['g']
        if not isinstance(g, list) or any(not (isinstance(x, list) and len(x) == 2 and all(isinstance(y, str) and y.strip() for y in x)) for x in g): E(tag + 'g 꼴: [[표제, 뜻], …]'); continue
        gk = [x[0] for x in g]
        if len(set(gk)) != len(gk): Wn(tag + 'g 표제 중복')
        ta, tb = len(strip_ruby(j[:ia])), len(strip_ruby(j[:ib]))
        def covered_by_g(t):
            cands = {t['lemma'], t['s']} | ({t['lread']} if t.get('lread') else set())
            for x in gk:
                if x in cands or t['s'] in x or t['lemma'] in x or (len(x) >= 2 and x in plain[max(0, t['a'] - 3):t['b'] + 3]): return True
            return False
        for t in T:
            if t['a'] >= ta and t['b'] <= tb: continue   # 표제
            if t['p1'] not in ('名詞', '動詞', '形容詞', '形状詞', '副詞', '連体詞', '感動詞'): continue
            if t['p2'] in ('数詞', '固有名詞'): continue
            if t['lemma'] in NO_GLOSS or t['s'] in NO_GLOSS or hira(t['s']) in NO_GLOSS: continue
            pv = plain[:t['a']].rstrip()
            if pv and NUMK.match(pv[-1]) and (t['s'] in COUNTERS or t['lemma'] in COUNTERS): continue
            if not any(is_kanji(ch) or KATA.search(ch) for ch in t['s']) and len(t['s']) <= 2: continue   # 짧은 가나 기능어
            if not covered_by_g(t): Wn(tag + '풀이 g에 없음: ' + t['s'] + ('(' + t['lemma'] + ')' if t['lemma'] != t['s'] else ''))
        for x, mean in g:
            if x == w or x == w0: Wn(tag + 'g에 표제어가 들어 있음: ' + x)
            core = re.sub(r'(する|る|う|く|ぐ|す|つ|ぬ|ぶ|む|い)$', '', x)
            rd_all = hira(ruby_reading(j))
            hcore = hira(core)
            if core and core not in plain and x not in plain and not any(t['lemma'] == x or t.get('lread') == hira(x) for t in T) and not (len(hcore) >= 2 and hcore in rd_all): Wn(tag + 'g 표제가 예문에 안 보임: ' + x)
            gd = GLOSS.get(x)
            if gd and isinstance(gd, list):
                ms = [m[0] if isinstance(m, list) else str(m) for m in gd]
                if mean not in ms and not any(m and (m in mean or mean in m) for m in ms): Wn(tag + 'g 뜻이 풀이 사전과 다름: %s=%s (사전 %s)' % (x, mean, ' / '.join(ms[:3])))
        # 비슷한 예문
        bg = bigrams(plain)
        best = max(((jacc(bg, b2), s2, who) for s2, who, b2, wid in EXIST_BG if wid != cid), default=(0, '', ''))
        if best[0] >= 0.6: Wn(tag + '지금 덱 예문과 비슷함(%.2f): %s [%s]' % (best[0], best[1], best[2]))
        for s2, who, b2 in new_bg:
            if who != cid and jacc(bg, b2) >= 0.6: Wn(tag + '새 카드 예문과 비슷함(%.2f): %s [%s]' % (jacc(bg, b2), s2, who))
    if len(plains) >= 2:
        for i in range(len(plains)):
            for k in range(i + 1, len(plains)):
                if jacc(bigrams(plains[i]), bigrams(plains[k])) >= 0.5: E('같은 카드 두 예문이 너무 비슷함: e%d e%d' % (i, k))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+'); ap.add_argument('--sheet'); ap.add_argument('--others'); ap.add_argument('--json'); ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()
    cards = []
    for f in a.files:
        for ln, line in enumerate(open(f, encoding='utf-8'), 1):
            line = line.strip()
            if not line: continue
            try: cards.append(json.loads(line))
            except Exception as ex: print('E\t-\t%s:%d\tJSON 아님: %s' % (f, ln, ex)); sys.exit(1)
    sheet = None
    if a.sheet:
        sj = json.load(open(a.sheet, encoding='utf-8'))
        if isinstance(sj, dict): sj = sj.get('cards') or list(sj.values())
        sheet = {x['id']: x for x in sj}
    seen = {}
    new_bg = []
    if a.others:
        own = {os.path.abspath(f) for f in a.files}
        for f in glob.glob(a.others):
            if os.path.abspath(f) in own: continue
            for line in open(f, encoding='utf-8'):
                line = line.strip()
                if not line: continue
                try: x = json.loads(line)
                except Exception: continue
                seen.setdefault(x.get('w'), x.get('id'))
                for e in x.get('e', []):
                    if isinstance(e, dict) and 'j' in e: new_bg.append((strip_ruby(e['j']), x.get('id'), bigrams(strip_ruby(e['j']))))
    for x in cards:
        for e in x.get('e', []):
            if isinstance(e, dict) and 'j' in e: new_bg.append((strip_ruby(e['j']), x.get('id'), bigrams(strip_ruby(e['j']))))
    ids = [x.get('id') for x in cards]
    R = Report()
    for i in set(i for i in ids if ids.count(i) > 1): R.add('E', i, '?', 'id 중복')
    for c in cards: check_card(c, R, sheet, seen, new_bg)
    ne = sum(1 for x in R.items if x[0] == 'E'); nw = len(R.items) - ne
    for lv, cid, w, m in R.items:
        if a.quiet and lv == 'W': continue
        print('%s\t%s\t%s\t%s' % (lv, cid, w, m))
    print('#SUMMARY 카드 %d · 오류 %d · 경고 %d' % (len(cards), ne, nw))
    if a.json: json.dump([dict(lv=lv, id=cid, w=w, msg=m) for lv, cid, w, m in R.items], open(a.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    sys.exit(1 if ne else 0)

if __name__ == '__main__':
    main()
