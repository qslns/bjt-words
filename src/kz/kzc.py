#!/usr/bin/env python3
"""한자 카드(샘플 3 틀) 도구 — 자료 보기 · 검사 · 컴파일

  python3 kzc.py info 認 確          # 앱 자료 + KanjiVG 부품 트리(경로·획 번호) + 참고(어원·부품 읽기)
  python3 kzc.py validate batches/b01.json [...]   # 카드 검사 (오류 = 꼭 고칠 것, 주의 = 확인할 것)
  python3 kzc.py compile -o out.json batches/*.json  # 앱/미리보기용으로 컴파일

카드(작성 형식)는 KANJI_SPEC.md 참고."""
import json, re, sys, os, unicodedata, glob

HERE = os.path.dirname(os.path.abspath(__file__))
SP = '/tmp/claude-0/-home-claude-bjt-words/4ecb1043-4c6e-5d36-a7b6-577be7533edc/scratchpad'
# 11/14: 컨테이너가 바뀌어 옛 임시 폴더가 없으면 /home/claude/kzdata/sp(KanjiVG·libhangul·makemeahanzi·kanji-data를 같은 배치로 받아 둔 곳)
if not os.path.isdir(SP + '/kvg_all'): SP = os.environ.get('KZ_SP', '/home/claude/kzdata/sp')
KV = SP + '/kvg_all/'
DATA = '/home/claude/work/build/data_app.json'
SRC = '/home/claude/work/kanji_mn/kanji_src.json'

PALETTE = {'blue': '#2E6BD8', 'green': '#2E8B57', 'orange': '#D9822B', 'purple': '#7B4FC9', 'red': '#C0392B',
           'gray': '#5A6478', 'brown': '#8A5A2B', 'teal': '#138D90', 'pink': '#C2185B', 'ink': '#1A2133',
           'yellow': '#F2A900', 'sky': '#4FA3E0', 'white': '#FFFFFF', 'black': '#1A2133'}
AUTO = ['blue', 'green', 'orange', 'purple', 'teal', 'brown', 'pink', 'gray']
INK = PALETTE['ink']

_data = None
def data():
    global _data
    if _data is None:
        D = json.load(open(DATA, encoding='utf-8'))
        src = json.load(open(SRC, encoding='utf-8'))
        _data = {'K': D['kanji'], 'W': {w['id']: w for w in D['words']}, 'order': [k['c'] for k in src], 'src': {k['c']: k for k in src}}
    return _data

def to_hira(s):
    return ''.join(chr(ord(ch) - 0x60) if 'ァ' <= ch <= 'ヶ' else ch for ch in s)

# ---------------- KanjiVG ----------------
_kv = {}
def kvg(c):
    """→ {'strokes': [d...](획순), 'root': node}; node = {el, orig, part, phon, pos, kids, s: [획 번호 0-based]}"""
    if c in _kv: return _kv[c]
    s = open(KV + '%05x.svg' % ord(c), encoding='utf-8').read()
    s = s[s.index('<g id="kvg:StrokePaths'):s.index('<g id="kvg:StrokeNumbers')]
    strokes = {}; root = None; stack = []
    for m in re.finditer(r'<g ([^>]*)>|</g>|<path ([^>]*)/>', s):
        t = m.group(0)
        if t.startswith('<g'):
            a = dict(re.findall(r'([\w:]+)="([^"]*)"', m.group(1)))
            n = {'el': a.get('kvg:element'), 'orig': a.get('kvg:original'), 'part': a.get('kvg:part'), 'phon': a.get('kvg:phon'),
                 'pos': a.get('kvg:position'), 'rad': a.get('kvg:radical'), 'kids': [], 's': []}
            if stack: stack[-1]['kids'].append(n)
            stack.append(n)
            if root is None: root = n
        elif t == '</g>':
            stack.pop()
        else:
            a = dict(re.findall(r'([\w:]+)="([^"]*)"', m.group(2)))
            k = int(re.search(r'-s(\d+)$', a['id']).group(1)) - 1
            strokes[k] = a['d']
            for n in stack: n['s'].append(k)
    if root['el'] is None and root['kids']: root = root['kids'][0]
    out = {'strokes': [strokes[i] for i in range(len(strokes))], 'root': root}
    _kv[c] = out
    return out

def resolve(c, path):
    """경로 → 획 번호(0-based) 목록. '' = 한자 전체 · '言' · '忍/刃/刀' · '木#2'(같은 부품 두 번째) · 's:1-3,5'(획 번호 1부터)"""
    K = kvg(c); n_all = len(K['strokes'])
    path = (path or '').strip()
    if path == '': return list(range(n_all))
    if path.startswith('s:'):
        out = []
        for seg in path[2:].split(','):
            seg = seg.strip()
            if '-' in seg:
                a, b = seg.split('-'); out += list(range(int(a) - 1, int(b)))
            else: out.append(int(seg) - 1)
        if not out or min(out) < 0 or max(out) >= n_all: raise ValueError(f'{c}: 획 번호 범위 밖 {path} (총 {n_all}획)')
        return sorted(set(out))
    nodes = [K['root']]
    for seg in path.split('/'):
        m = re.match(r'^(.+?)(?:#(\d+))?$', seg); el, idx = m.group(1), m.group(2)
        nxt = []
        for n in nodes:
            cands = [k for k in n['kids'] if k['el'] == el]
            if not cands: continue
            if idx:
                if int(idx) > len(cands): raise ValueError(f'{c}: {path} — {el}#{idx} 없음')
                nxt.append(cands[int(idx) - 1])
            elif len(cands) == 1 or all(k['part'] for k in cands): nxt += cands
            else: raise ValueError(f'{c}: {path} — {el}가 {len(cands)}개 → {el}#1, {el}#2 처럼 골라 주세요')
        if not nxt: raise ValueError(f'{c}: 경로 {path} 에서 {seg} 를 못 찾음 (kzc.py info {c} 로 트리 확인)')
        nodes = nxt
    out = sorted(set(i for n in nodes for i in n['s']))
    if not out: raise ValueError(f'{c}: {path} 에 획이 없음')
    return out

NUM = re.compile(r'-?\d*\.?\d+(?:e-?\d+)?')
def compact(d):
    def r(m):
        v = round(float(m.group(0)), 1)
        s = ('%.1f' % v).rstrip('0').rstrip('.')
        if s in ('', '-'): s = '0'
        return s   # '-0'은 그대로 둔다: 앞 숫자와 사이를 가르는 빼기 기호라서 없애면 숫자가 붙어 버림
    d = NUM.sub(r, d)
    d = re.sub(r'\s*,\s*', ',', d); d = re.sub(r'\s+', ' ', d).strip()
    d = re.sub(r',-', '-', d)
    return d

def bbox(c, idxs):
    import kvgbox
    return kvgbox.bbox([kvg(c)['strokes'][i] for i in idxs])

# ---------------- 검사 ----------------
try:
    import emoji as _emoji
except Exception:
    _emoji = None
KATA = re.compile(r'[ァ-ヺ]')
CJK = re.compile(r'[㐀-鿿豈-﫿\U00020000-\U0002ffff⺀-⿟㇀-㇯]')
KANA = re.compile(r'[ぁ-ゖー]+')

def color_of(v):
    if v is None: return None
    if isinstance(v, str) and v.startswith('#'): return v
    if v in PALETTE: return PALETTE[v]
    raise ValueError(f'색 이름 {v!r} 없음 (쓸 수 있는 색: {", ".join(PALETTE)})')

def check_emoji(e, where, errs, warns):
    if _emoji is None: return
    if e not in _emoji.EMOJI_DATA:
        # 피부색/변형 선택자 없이도 확인
        base = e.replace('️', '')
        if base not in _emoji.EMOJI_DATA and (base + '️') not in _emoji.EMOJI_DATA:
            errs.append(f'{where}: 이모지 아님/여러 개 {e!r} (한 칸에 이모지 하나씩)'); return
        info = _emoji.EMOJI_DATA.get(base) or _emoji.EMOJI_DATA.get(base + '️')
    else:
        info = _emoji.EMOJI_DATA[e]
    if info.get('E', 0) > 13.1:
        errs.append(f'{where}: 너무 새 이모지 {e} (Emoji {info.get("E")}, 13.1 이하만 — 옛 아이패드에서 네모로 나옴)')

SCENE_KEYS = {'e', 't', 'plus', 'arrow', 'knife', 'rect', 'circle', 'line', 'path', 'k'}
def check_scene(c, items, where, errs, warns):
    if not isinstance(items, list) or not items: errs.append(f'{where}: scene 비었음'); return
    for i, it in enumerate(items):
        w = f'{where}[{i}]'
        kind = [k for k in it if k in SCENE_KEYS]
        if len(kind) != 1: errs.append(f'{w}: 종류 키가 하나여야 함 {list(it)}'); continue
        k = kind[0]
        for key in ('x', 'y', 's') + (('w',) if k == 'k' else ()):   # 글자 항목의 w는 굵기(400~900)
            if key in it and not (isinstance(it[key], (int, float)) and -10 <= it[key] <= 110): errs.append(f'{w}: {key}={it[key]} 범위 밖(0~100)')
        if k == 't' and 'w' in it and it['w'] not in (400, 500, 600, 700, 800, 900): errs.append(f'{w}: 글자 굵기 w는 400~900')
        if k == 'e': check_emoji(it['e'], w, errs, warns)
        if k == 't':
            if KATA.search(it['t']): errs.append(f'{w}: 가타카나 금지 {it["t"]}')
            if len(it['t']) > 8: warns.append(f'{w}: 그림 속 글자가 김 {it["t"]!r}')
        if k == 'k':
            try:
                resolve(c, it['k'])
                if isinstance(it.get('color'), dict):
                    for p, col in it['color'].items(): resolve(c, p); color_of(col)
            except ValueError as ex: errs.append(f'{w}: {ex}')
        for ck in ('c', 'fill', 'stroke'):
            if ck in it and isinstance(it[ck], str) and it[ck] != 'none':
                try: color_of(it[ck])
                except ValueError as ex: errs.append(f'{w}: {ex}')

def validate(e):
    errs, warns = [], []
    d = data(); c = e.get('c')
    if c not in d['K']: return [f'{c}: 앱 한자 목록에 없음'], []
    k = d['K'][c]; hun = k['h'].lstrip('? ').strip()
    try: kvg(c)
    except Exception as ex: return [f'{c}: KanjiVG 없음 {ex}'], []
    # 장면 한 줄
    hook = e.get('hook', '')
    if not hook: errs.append(f'{c}: hook 없음')
    if hook and not hook.endswith('모습'): errs.append(f'{c}: hook은 "~모습"으로 끝내기: {hook}')
    if len(hook) > 60: warns.append(f'{c}: hook이 김({len(hook)}자) — 45자 안팎 권장')
    if KATA.search(hook + e.get('bridge', '')): errs.append(f'{c}: hook/bridge 가타카나 금지')
    for lab, txt in [('hook', hook), ('bridge', e.get('bridge', '')), ('basic', e.get('basic', '')), ('snd', e.get('snd', ''))] + [(pk + '.cap', (e.get(pk) or {}).get('cap', '')) for pk in ('p1', 'p2', 'p3')] + [(f'tree[{i}]', json.dumps(st, ensure_ascii=False)) for i, st in enumerate(e.get('tree') or [])]:
        if lab.startswith('tree'):
            try:
                st = json.loads(txt); txt = ' '.join([p.get('n', '') + ' ' + p.get('note', '') for p in st.get('parts', [])] + [st.get('res', {}).get('n', ''), st.get('mini', '')])
            except Exception: pass
        text_warn(c, lab, txt, warns)
    # 그림 3칸
    for pk in ('p1', 'p2', 'p3'):
        p = e.get(pk)
        if not isinstance(p, dict): errs.append(f'{c}: {pk} 없음'); continue
        cap = p.get('cap', '')
        if not cap: errs.append(f'{c}: {pk}.cap 없음')
        if len(cap) > 34: warns.append(f'{c}: {pk}.cap 김({len(cap)}자): {cap}')
        if KATA.search(cap): errs.append(f'{c}: {pk}.cap 가타카나 금지')
        if 'scene' in p: check_scene(c, p['scene'], f'{c}.{pk}.scene', errs, warns)
        if 'under' in p: check_scene(c, p['under'], f'{c}.{pk}.under', errs, warns)
        if 'color' in p:
            if pk != 'p2': errs.append(f'{c}: color는 p2에서만')
            try:
                for path, col in p['color'].items(): resolve(c, path); color_of(col)
            except ValueError as ex: errs.append(f'{c}.p2.color: {ex}')
        if pk in ('p1', 'p3') and 'scene' not in p: errs.append(f'{c}: {pk}는 scene 필요')
        if pk == 'p2' and 'scene' not in p and 'color' not in p: errs.append(f'{c}: p2는 color(색칠한 한자) 또는 scene')
    p3 = e.get('p3') or {}
    if p3.get('cap') and not p3['cap'].replace(' ', '').endswith(('→' + hun).replace(' ', '')):
        errs.append(f'{c}: p3.cap 끝은 "→ {hun}": {p3.get("cap")}')
    # 부수로 쪼개기
    tree = e.get('tree') or []
    if not tree and not e.get('basic'): errs.append(f'{c}: tree 또는 basic 필요')
    if tree and e.get('basic'): warns.append(f'{c}: tree와 basic 둘 다 있음(basic은 안 쪼개지는 글자만)')
    on_h = [to_hira(x) for x in k['on']]
    prev_res = set()
    for si, st in enumerate(tree):
        w = f'{c}.tree[{si}]'
        parts = st.get('parts') or []
        if len(parts) < 2: errs.append(f'{w}: 부품 2개 이상')
        res = st.get('res') or {}
        try:
            rs = set(resolve(c, res.get('p', '')))
            ps = []
            for pi, pt in enumerate(parts):
                s_ = set(resolve(c, pt.get('p', '')))
                for q in ps:
                    if q & s_: errs.append(f'{w}: 부품 {pi + 1}이 다른 부품과 획이 겹침 ({pt.get("p")})')
                ps.append(s_)
                if not pt.get('n'): errs.append(f'{w}: 부품 {pi + 1} 이름(n) 없음')
                ex_n = expected_name(last_el(pt.get('p', ''), c))
                if ex_n and pt.get('n') and pt['n'].replace(' ', '') != ex_n.replace(' ', ''): warns.append(f'{w}: 부품 이름 {pt["n"]!r} ≠ 이름표 {ex_n!r} (다르게 쓴 이유가 없으면 이름표대로)')
                if KATA.search(pt.get('n', '') + pt.get('note', '')): errs.append(f'{w}: 부품 이름 가타카나 금지')
                if pt.get('r') and not re.fullmatch(r'[ぁ-ゖー・]+', pt['r']): errs.append(f'{w}: 부품 읽기는 히라가나만 {pt["r"]}')
                if 'col' in pt: color_of(pt['col'])
            un = set().union(*ps) if ps else set()
            if un != rs: errs.append(f'{w}: 부품 획을 합치면 결과와 달라요 (빠짐 {sorted(i + 1 for i in rs - un)} / 넘침 {sorted(i + 1 for i in un - rs)}) — 획 번호는 1부터')
        except ValueError as ex: errs.append(f'{w}: {ex}')
        if not res.get('n'): errs.append(f'{w}: res 이름(n) 없음')
        if res.get('r') and not re.fullmatch(r'[ぁ-ゖー・]+', res['r']): errs.append(f'{w}: res 읽기는 히라가나만')
        if not st.get('mini'): errs.append(f'{w}: mini 없음')
        if KATA.search(st.get('mini', '')): errs.append(f'{w}: mini 가타카나 금지')
    if tree:
        last = tree[-1].get('res', {})
        if last.get('p', '') != '': errs.append(f'{c}: 마지막 단계 res.p는 "" (한자 전체)')
        if last.get('n') and last['n'].replace(' ', '') != hun.replace(' ', ''): warns.append(f'{c}: 마지막 res 이름 {last["n"]!r} ≠ 앱 훈음 {hun!r}')
        kun_h = [to_hira(re.sub(r'[()（）.\-]', '', x)) for x in k['kun']]
        if last.get('r') and any(r_ not in on_h and r_ not in kun_h for r_ in last['r'].split('・')):
            warns.append(f'{c}: 마지막 res 읽기 {last["r"]} 가 앱 읽기({"・".join(on_h)})에 없음')
    # 소리 줄
    snd = e.get('snd', '')
    if not snd: errs.append(f'{c}: snd 없음')
    if KATA.search(snd): errs.append(f'{c}: snd 가타카나 금지(히라가나로)')
    return errs, warns

# ---------------- 컴파일 ----------------
RADFIX = str.maketrans({'⻌': '辶', '⺕': '彐', '⻖': '阝', '⻏': '阝', '⺤': '爫', '⺨': '犭', '⺅': '亻', '⺡': '氵', '⺘': '扌', '⺖': '忄', '⺾': '艹', '⺲': '罒', '⻊': '足', '⺮': '竹', '⺗': '心', '⻗': '雨', '⺧': '牛', '⺌': '小', '⺍': '小', '⺼': '月', '⻝': '食', '⻞': '食', '⺩': '王', '⺆': '冂'})
def fixt(s):
    return (s or '').translate(RADFIX)
def text_warn(c, label, s, warns):
    for ch in s or '':
        if ord(ch) >= 0x20000: warns.append(f'{c}: {label}에 확장 한자 {ch}(U+{ord(ch):X}) — 아이패드에서 네모로 나올 수 있음. 아는 글자나 말로 바꾸기')
        elif 0x2E80 <= ord(ch) <= 0x2EFF and ch not in RADFIX_SRC: warns.append(f'{c}: {label}에 부수 보충 글자 {ch} — 일반 한자로 바꾸기')
RADFIX_SRC = '⻌⺕⻖⻏⺤⺨⺅⺡⺘⺖⺾⺲⻊⺮⺗⻗⺧⺌⺍⺼⻝⻞⺩⺆'
def comp_scene(c, items):
    out = []
    for it in items:
        it = dict(it)
        for ck in ('c', 'fill', 'stroke'):
            if ck in it and isinstance(it[ck], str) and it[ck] != 'none': it[ck] = color_of(it[ck])
        if 'k' in it:
            s = resolve(c, it['k'])
            col = it.get('color')
            if isinstance(col, dict):
                cm = {}
                for p, cv in col.items():
                    for i in resolve(c, p): cm[i] = color_of(cv)
                it['cs'] = [cm.get(i, it.get('c') or INK) for i in s]
            else:
                it['cs'] = [color_of(col) if col else (it.get('c') or INK)] * len(s)
            it['s_'] = s; it['vb'] = vbox(c, s) if it['k'] else [0, 0, 109]
            it.pop('color', None)
        out.append(it)
    return out

def vbox(c, s):
    import kvgbox
    x0, y0, x1, y1 = kvgbox.bbox([kvg(c)['strokes'][i] for i in s])
    sz = max(x1 - x0, y1 - y0, 30) + 12; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return [round(cx - sz / 2, 1), round(cy - sz / 2, 1), round(sz, 1)]

def compile_entry(e):
    d = data(); c = e['c']; k = d['K'][c]; K = kvg(c)
    n = len(K['strokes'])
    def colmap(m):
        cm = {}
        for p, cv in (m or {}).items():
            for i in resolve(c, p): cm[i] = color_of(cv)
        return cm
    p2col = colmap((e.get('p2') or {}).get('color'))
    panels = []
    for pk in ('p1', 'p2', 'p3'):
        p = e[pk]; o = {'cap': fixt(p['cap'])}
        if 'scene' in p: o['sc'] = comp_scene(c, p['scene'])
        if 'color' in p:
            o['kc'] = [p2col.get(i, INK) for i in range(n)]
            if 'under' in p: o['un'] = comp_scene(c, p['under'])
        panels.append(o)
    # 부수로 쪼개기 — 색: p2에서 정한 색(가장 가까운 조상 경로) → 앞 단계 결과면 빨강 → 남은 팔레트
    tree = []
    prev_res = []
    for st in e.get('tree') or []:
        used = []; parts = []
        for pt in st['parts']:
            s = resolve(c, pt['p'])
            col = color_of(pt['col']) if pt.get('col') else None
            if not col:
                if any(set(s) == set(r) for r in prev_res) and PALETTE['red'] not in used: col = PALETTE['red']
                else:
                    cs = [p2col.get(i) for i in s]
                    cs = [x for x in cs if x]
                    if cs and len(set(cs)) == 1 and cs[0] not in used: col = cs[0]
            if not col or col in used:
                col = next(PALETTE[a] for a in AUTO if PALETTE[a] not in used)
            used.append(col)
            parts.append({'s': s, 'vb': vbox(c, s), 'c': col, 'n': fixt(pt['n']), **({'r': pt['r']} if pt.get('r') else {}), **({'nt': fixt(pt['note'])} if pt.get('note') else {})})
        rs = resolve(c, st['res'].get('p', ''))
        cs = {}
        for pt in parts:
            for i in pt['s']: cs[i] = pt['c']
        res = {'s': rs, 'vb': vbox(c, rs) if st['res'].get('p', '') else [0, 0, 109], 'cs': [cs.get(i, INK) for i in rs], 'n': fixt(st['res']['n']), **({'r': st['res']['r']} if st['res'].get('r') else {})}
        tree.append({'pa': parts, 're': res, 'mi': fixt(st['mini'])})
        prev_res.append(rs)
    hun = k['h'].lstrip('? ').strip()
    out = {'c': c, 'h': hun, 'on': [to_hira(x) for x in k['on']], 'kun': k['kun'], 'hook': fixt(e['hook']), 'br': fixt(e.get('bridge', '')),
           'S': [compact(x) for x in K['strokes']], 'p': panels, 't': tree, 'bs': fixt(e.get('basic', '')), 'snd': fixt(e['snd'])}
    return out

def load_batches(paths):
    out = []
    for p in paths:
        j = json.load(open(p, encoding='utf-8'))
        out += j if isinstance(j, list) else j.get('cards', [])
    return out

def info(c):
    d = data(); k = d['K'].get(c)
    if not k: print(c, '앱 한자 목록에 없음'); return
    order = d['order'].index(c) + 1 if c in d['order'] else '?'
    print(f'==== {c}  #{order}  훈음: {k["h"]}  획: {k["n"]}')
    print('  음독(히라가나):', '・'.join(to_hira(x) for x in k['on']) or '—', '  훈독:', '・'.join(k['kun']) or '—')
    print('  옛 해설(10/7 검수, 참고만):', k.get('s', ''), '|', k.get('x', ''))
    src = d['src'].get(c)
    if src: print('  이 단어장에서 실제 읽기(많이 쓰는 순):', ', '.join(f'{r[0]}×{r[2]}' for r in src['reads']))
    ws = sorted((d['W'][i] for i in k['u'] if i in d['W']), key=lambda w: (w.get('ord') is None, w.get('ord') or 0, w['id']))
    print('  단어:', ' / '.join(f"{w['w']}({w['r']}: {w['m'][:14]})" for w in ws[:14]) + (f' … 외 {len(ws) - 14}개' if len(ws) > 14 else ''))
    ref = REF().get(c)
    if ref: print('  참고 어원(MakeMeAHanzi, 중국 기준):', json.dumps(ref, ensure_ascii=False))
    K = kvg(c)
    print(f'  KanjiVG 트리 (경로 → 획 번호, 1부터; 총 {len(K["strokes"])}획):')
    def walk(n, path, depth):
        for kid in n['kids']:
            el = kid['el'] or '(이름 없음)'
            same = [x for x in n['kids'] if x['el'] == kid['el']]
            seg = el if (len(same) == 1 or all(x['part'] for x in same)) else f'{el}#{same.index(kid) + 1}'
            p = (path + '/' + seg) if path else seg
            extra = []
            if kid['orig']: extra.append(f'원래 {kid["orig"]}')
            if kid['phon']: extra.append(f'소리 부분 표시({kid["phon"]})')
            if kid['part']: extra.append(f'나뉜 조각 {kid["part"]}')
            if kid['pos']: extra.append(kid['pos'])
            rd = KREAD().get(kid['el'] or '', '')
            key = f"{kid['el']}<{kid['orig']}>" if kid['orig'] and f"{kid['el']}<{kid['orig']}>" in RAD() else kid['el']
            nm = expected_name(key)
            if key in RAD() and RAD()[key][1]: nm = f'{nm} / note: {RAD()[key][1]}'
            print('    ' + '  ' * depth + f'{p}  획 {",".join(str(i + 1) for i in kid["s"])}' + (f'  ({"; ".join(extra)})' if extra else '') + (f'  읽기:{rd}' if rd else '') + (f'  이름:{nm}' if nm else ''))
            walk(kid, p, depth + 1)
    walk(K['root'], '', 0)

_rad = None
def RAD():
    global _rad
    if _rad is None:
        _rad = {k: v for k, v in json.load(open(os.path.join(HERE, 'radicals.json'), encoding='utf-8')).items() if not k.startswith('_')}
    return _rad
def expected_name(el):
    if not el: return None
    if el in RAD(): return RAD()[el][0]
    K = data()['K']
    if el in K: return K[el]['h'].lstrip('? ').strip()
    return None
def last_el(path, c=None):
    """경로 마지막 부품 → 이름표 키(원래 글자가 있으면 'el<orig>')"""
    if not path or path.startswith('s:'): return None
    el = path.split('/')[-1].split('#')[0]
    if c:
        try:
            n = node_at(c, path)
            if n and n.get('orig') and f"{el}<{n['orig']}>" in RAD(): return f"{el}<{n['orig']}>"
        except Exception: pass
    return el
def node_at(c, path):
    nodes = [kvg(c)['root']]
    for seg in path.split('/'):
        m = re.match(r'^(.+?)(?:#(\d+))?$', seg); el, idx = m.group(1), m.group(2)
        nxt = []
        for n in nodes:
            cands = [k for k in n['kids'] if k['el'] == el]
            if idx and int(idx) <= len(cands): nxt.append(cands[int(idx) - 1])
            elif not idx: nxt += cands
        nodes = nxt
    return nodes[0] if nodes else None
_lh = None
def LH(c):
    global _lh
    if _lh is None:
        _lh = {}
        for line in open(SP + '/libhangul/hanja.txt', encoding='utf-8'):
            if line.startswith('#') or line.count(':') < 2: continue
            a, b, m = line.rstrip('\n').split(':', 2)
            if len(b) == 1: _lh.setdefault(b, []).append(f'{a}:{m}' if m else a)
    return _lh.get(c, [])

_ref = None
def REF():
    global _ref
    if _ref is None:
        _ref = {}
        for line in open(SP + '/mmah/dictionary.txt', encoding='utf-8'):
            j = json.loads(line)
            _ref[j['character']] = {k: j[k] for k in ('decomposition', 'etymology') if k in j}
    return _ref
_kr = None
def KREAD():
    global _kr
    if _kr is None:
        kd = json.load(open(SP + '/kdata/kanji.json', encoding='utf-8'))
        _kr = {c: '・'.join(v.get('readings_on') or []) for c, v in kd.items() if v.get('readings_on')}
    return _kr

if __name__ == '__main__':
    sys.path.insert(0, HERE)
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'info':
        for c in ''.join(sys.argv[2:]): info(c)
    elif cmd == 'hun':
        for c in ''.join(sys.argv[2:]):
            print(c, '| 이름표:', RAD().get(c), '| 앱 훈음:', data()['K'].get(c, {}).get('h'), '| libhangul:', ' / '.join(LH(c)[:4]), '| 일본 음:', KREAD().get(c, ''))
    elif cmd == 'validate':
        cards = load_batches(sys.argv[2:]); bad = 0; seen = set()
        for e in cards:
            if e.get('c') in seen: print(f'{e.get("c")}: 같은 한자 두 번'); bad += 1
            seen.add(e.get('c'))
            er, wa = validate(e)
            for x in er: print('  오류', x)
            for x in wa: print('  주의', x)
            bad += bool(er)
            if not er:
                try: compile_entry(e)
                except Exception as ex: print('  오류', e.get('c'), '컴파일 실패', ex); bad += 1
        print(f'{len(cards)}장 검사, 오류 있는 카드 {bad}장')
        sys.exit(1 if bad else 0)
    elif cmd == 'compile':
        i = sys.argv.index('-o'); out = sys.argv[i + 1]; paths = sys.argv[2:i] + sys.argv[i + 2:]
        cards = load_batches(paths)
        comp = [compile_entry(e) for e in cards]
        json.dump(comp, open(out, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        print('compiled', len(comp), os.path.getsize(out), 'bytes')
    else:
        print(__doc__)
