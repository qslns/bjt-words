"""확장 후보 목록 만들기 (2026-11-13) — 공식 모의는 쓰지 않음, 단어장 제작에 안 쓴 글 3종으로 빈도를 잼
usage: python3 make_lists.py DATA_APP_JSON OLD_WORDS_JSON JLPT_DIR BSD_TXT REPORTS_TXT DRILLS_TXT OUT_DIR

나오는 것 (OUT_DIR):
  restore_order.json  지운 2,312개를 값 순서로 (복원할 때 1501번부터 이 순서)
  basic_add.json      N5·N4 목록 중 앱(복원분 포함)에 없는 말 — 기본 886번부터 붙일 후보(빈도 순)
  n3n2_missing.json   N3·N2 목록 중 없는 말 — 2단계 후보(사용자 확인 뒤에만)
점수 = 내용어 10만 개당 등장 수의 가중합: 비즈니스 대화(BSD) 0.35 · 보고서(chABSA) 0.25 · 문법·경어 드릴 문장 0.40
(빈도 0인 말은 옛 등급 A→B, JLPT 급수 N5→N1→없음, id 순으로 뒤에 붙임 — 옛 ord·sc·mk는 모의 빈도가 섞였을 수 있어 안 씀)"""
import sys, re, json, csv, collections, os
import fugashi
data, oldp, jd, fd, fw, fm, outd = sys.argv[1:8]
os.makedirs(outd, exist_ok=True)
tg = fugashi.Tagger()
W = json.load(open(data, encoding='utf-8'))['words']
OLD = json.load(open(oldp, encoding='utf-8'))

def forms(s):
    s = re.sub(r'[（(][^)）]*[)）]', '', s)
    out = []
    for f in re.split(r'[;；,，・/／、]', s):
        f = f.replace('〜', '').replace('～', '').replace(' ', '').replace('　', '').strip()
        if f: out.append(f)
    return out
def toks(s):
    o = []; prev = None
    for t in tg(s):
        f = t.feature
        aux = f.pos2 == '非自立可能' and f.pos1 in ('動詞', '形容詞') and prev is not None and (
            (prev.pos1 == '助詞' and prev.pos2 == '接続助詞') or (f.lemma == '為る' and prev.pos1 == '名詞'))
        o.append((f.lemma or t.surface, f.pos1, 'AUX' if aux else f.pos2, t.surface)); prev = f
    return o
def key(f): return tuple(x[0] for x in toks(f))

# JLPT 급수표 (옛 단어 동점 정렬용)
LVR = {}
for i, lv in enumerate(('n5', 'n4', 'n3', 'n2', 'n1')):
    for r in csv.DictReader(open(os.path.join(jd, lv + '.csv'), encoding='utf-8')):
        for f in forms(r['expression']) or forms(r['reading']): LVR.setdefault(f, i)
def lvrank(w): return min([LVR[f] for f in forms(w['w']) if f in LVR] or [9])
# JLPT 목록에서 없는 말 찾기
have = set()
for w in W + OLD:
    for f in forms(w['w']): have.add(f); have.add(key(f))
cands = []
for lv in ('n5', 'n4', 'n3', 'n2'):
    for r in csv.DictReader(open(os.path.join(jd, lv + '.csv'), encoding='utf-8')):
        fs = forms(r['expression']) or forms(r['reading'])
        if not fs or (set(fs) | set(key(f) for f in fs)) & have: continue
        cands.append({'id': 'J%s-%d' % (lv, len(cands)), 'w': fs[0], 'alt': fs[1:], 'r': r['reading'], 'en': r['meaning'], 'lv': lv.upper()})

# 매칭 사전: 현재 단어 > 옛 단어 > JLPT 후보 (같은 키면 앞쪽이 가져감), 긴 것 먼저
ALL = [(w['id'], w['w'], 0) for w in W] + [(w['id'], w['w'], 1) for w in OLD] + [(c['id'], c['w'], 2) for c in cands]
key2id, pri = {}, {}
for wid, hw, p in ALL:
    h = re.sub(r'[（(].*?[)）]', '', hw).strip()
    if re.search(r'.[〜～].', h) or re.search(r'[…○]', h): continue
    h = h.strip('〜～')
    for form in re.split(r'[・／/]', h):
        k = key(form)
        if k and (k not in key2id or p < pri[k]): key2id[k] = wid; pri[k] = p
MAXL = max(len(k) for k in key2id)
CONTENT = {'名詞', '動詞', '形容詞', '形状詞', '副詞', '連体詞', '接続詞', '感動詞', '代名詞', '接頭辞', '接尾辞'}
JP = re.compile(r'[぀-ヿ一-鿿]')
def is_c(t): return t[1] in CONTENT and t[2] not in ('固有名詞', '数詞', 'AUX') and t[0] != '御' and bool(JP.search(t[3]))
def count(path):
    c = collections.Counter(); n = 0
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('@@'): continue
        ts = toks(line); i = 0; n += sum(1 for t in ts if is_c(t))
        while i < len(ts):
            hit = None
            for L in range(min(MAXL, len(ts) - i), 0, -1):
                k = tuple(t[0] for t in ts[i:i + L])
                if k in key2id and any(is_c(t) for t in ts[i:i + L]): hit = (key2id[k], L); break
            if hit: c[hit[0]] += 1; i += hit[1]
            else: i += 1
    return c, n
(cD, nD), (cW, nW), (cM, nM) = count(fd), count(fw), count(fm)
def score(i): return 0.35 * 1e5 * cD[i] / nD + 0.25 * 1e5 * cW[i] / nW + 0.40 * 1e5 * cM[i] / nM

oldrows = sorted(({'id': w['id'], 'w': w['w'], 'r': w['r'], 'm': w['m'], 'old_tier': w.get('t'), 'c': w.get('c'),
                   'jlpt': ('N%d' % (5 - lvrank(w))) if lvrank(w) < 9 else '', 'score': round(score(w['id']), 2)} for w in OLD),
                 key=lambda r: (-r['score'], 0 if r['old_tier'] == 'A' else 1, 5 - int(r['jlpt'][1]) if r['jlpt'] else 9, r['id']))
json.dump(oldrows, open(os.path.join(outd, 'restore_order.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
for c in cands: c['score'] = round(score(c['id']), 2)
lvo = {'N5': 0, 'N4': 1, 'N3': 2, 'N2': 3}
basic = sorted((c for c in cands if c['lv'] in ('N5', 'N4')), key=lambda c: (-c['score'], lvo[c['lv']]))
n3n2 = sorted((c for c in cands if c['lv'] in ('N3', 'N2')), key=lambda c: (-c['score'], lvo[c['lv']]))
json.dump(basic, open(os.path.join(outd, 'basic_add.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(n3n2, open(os.path.join(outd, 'n3n2_missing.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('content tokens: dialogue', nD, 'reports', nW, 'drills', nM)
print('restore', len(oldrows), 'with evidence', sum(1 for r in oldrows if r['score'] > 0), '| top 30:', ' '.join(r['w'] for r in oldrows[:30]))
print('basic_add', len(basic), 'with evidence', sum(1 for c in basic if c['score'] > 0), '| top 30:', ' '.join(c['w'] for c in basic[:30]))
print('n3n2', len(n3n2), 'with evidence', sum(1 for c in n3n2 if c['score'] > 0), '| top 30:', ' '.join(c['w'] for c in n3n2[:30]))
