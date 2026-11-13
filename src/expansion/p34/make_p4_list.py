# P4(N3·N2 빠진 말) 목록 정리 1단계: 빈도 점수 > 0인 것(405개) — 뺄 것·표기 바꿀 것은 이유와 함께
# 점수 0인 것(896개)은 같은 기준으로 에이전트가 분류(p4_zero_*) → 나중에 합침
# 표기 규칙: 상용한자 밖 글자가 든 말은 가나(공용문), 〜 표제는 접사 카드(본편 〜化·〜期처럼)
import json, re, sys
sys.path.insert(0, '/home/claude/work/expansion/tools')
from kanji_ref import ref
from cardlib import is_kanji, hira
E = '/home/claude/work/expansion'
n = json.load(open(E + '/n3n2_missing.json', encoding='utf-8'))
log = json.load(open(E + '/p2/basic_final_log.json', encoding='utf-8'))
used = {x['src'] for x in log['add']} | {x['src'] for x in log['drop']}
items = [x for x in n if x['id'] not in used]
DROP = {
 'ところ': '문법(〜ところ) — 所는 앱에 있음', 'みたい': '문법(〜みたい)', 'ほう': '문법(〜ほう 비교) — 方는 앱에 있음',
 '所為': '복원 목록의 せい(3450)', 'ちょうだい': '앱의 頂戴する', '毎': '복원 목록의 〜ごと', '日日': '앱의 日にち', '始めに': '앱의 初めに(1112)',
 '付': '복원 목록의 〜付き', '極': '복원 목록의 ごく', '果して': '복원 목록의 果たして', '話中': '앱의 話し中', '伯父さん': '기본 おじさん',
 '伯母': '기본 おばさん', '水曜': '앱의 水曜日', '申し訳': '앱의 申し訳ない·申し訳ございません', '御覧': '앱의 ご覧になる', '知らせ': '앱의 お知らせ',
 '具体': '앱의 具体的', '足る': '앱의 足りる(옛 꼴)', 'ビルディング': '앱의 ビル', '皿': '기본 お皿', '罹る': '앱의 かかる(가나 표기가 같음)',
 '蕎麦': '앱의 そば와 가나 표기가 같음(蕎는 상용한자 밖)', '我': '앱의 我が社', '否': 'いや(아니) 감탄사는 가나 — 否는 可否·賛否 속에서만',
 '住': '낱자 조각(衣食住·住所 속에서만)', '異': '낱자 조각(異議·異なる 속에서만)', '苦': '낱자 조각(苦労·苦手 속에서만)', '茶': '앱의 お茶',
}
CHANGE = {  # w → (새 w, 새 r, 메모)
 '性': ('〜性', 'せい', '접미어 ~성(安全性·可能性·利便性) — 낱말 性(성별)은 p에'), '大': ('大〜', 'だい', '접두어 대~(大企業·大規模)'),
 '小': ('小〜', 'しょう', '접두어 소~(小規模·小会議室)'), '学': ('〜学', 'がく', '접미어 ~학(経済学·心理学)'), '無': ('無〜', 'む', '접두어 무~(無関心·無責任)'),
 '重': ('重〜', 'じゅう', '접두어 중~(重工業·重労働)'), '校': ('〜校', 'こう', '학교 세는 말·~교(3校·母校)'), '病': ('〜病', 'びょう', '접미어 ~병(糖尿病)'),
 '園': ('〜園', 'えん', '접미어 ~원(幼稚園·動物園)'), '帳': ('〜帳', 'ちょう', '접미어 ~장(手帳·通帳)'), '科': ('〜科', 'か', '접미어 ~과(内科·学科)'),
 '教': ('〜教', 'きょう', '접미어 ~교(仏教)'), '画': ('〜画', 'が', '접미어 ~화(日本画·映画)'), '和': ('和〜', 'わ', '접두어 일본식(和食·和室)'),
 '弁': ('〜弁', 'べん', '접미어 ~사투리(関西弁)'), '年生': ('〜年生', 'ねんせい', '학년(小学3年生)'), '或': ('ある〜', 'ある', '어떤~(ある日·ある企業) — 동사 ある와 다름'),
 'なにも': ('何も', 'なにも', '何も〜ない'), 'お出掛け': ('お出かけ', 'おでかけ', '지금 표기'), 'タイア': ('タイヤ', 'タイヤ', '지금 표기'),
 'そのころ': ('その頃', 'そのころ', ''), '人差指': ('人差し指', 'ひとさしゆび', '지금 표기'), '生意気な': ('生意気', 'なまいき', 'な형용사는 な 없이'),
 '従兄弟': ('いとこ', 'いとこ', '熟字訓 — 지금은 가나가 흔함'), '釣': ('釣り', 'つり', '지금 표기'), 'はあ': ('はあ', 'はあ', ''), 'しまった': ('しまった', 'しまった', ''),
 '為す': ('なす', 'なす', '為의 な 읽기는 상용 밖 → 가나'), '堪える': ('こらえる', 'こらえる', '堪의 こら 읽기는 상용 밖'),
 '掻く': ('かく', 'かく', '掻는 상용한자 밖(書く·欠く와 헷갈림 주의)'),
}
def joyo_ok(w):
    for ch in w:
        if is_kanji(ch) and ch not in '々':
            r = ref(ch); g = r and r.get('grade')
            try: g = int(g)
            except Exception: g = None
            if g is None or g > 8: return False
    return True
out, dropped, changed = [], [], []
for x in items:
    if x['score'] <= 0: continue
    w, r = x['w'], re.sub(r'\s*\((かん|ひかく)\)', '', x['r']).split(';')[0].strip()
    if w in DROP: dropped.append({'src': x['id'], 'w': w, 'why': DROP[w]}); continue
    note = ''
    if w in CHANGE:
        nw, nr, note = CHANGE[w]
        if (nw, nr) != (w, r): changed.append({'src': x['id'], 'from': w + '|' + x['r'], 'to': nw + '|' + nr, 'why': note})
        w, r = nw, nr
    elif not joyo_ok(w):
        changed.append({'src': x['id'], 'from': w + '|' + x['r'], 'to': hira(r) + '|' + hira(r), 'why': '상용한자 밖 글자 → 가나'})
        note = '원래 표기 ' + w + '(상용한자 밖)'; w = r
    if '～' in r or '〜' in r: sys.exit('정리 안 된 〜: %s %s' % (w, r))
    out.append({'src': x['id'], 'w': w, 'r': hira(r) if not re.fullmatch(r'[゠-ヿ・ー]+', r) else r, 'en': x['en'], 'lv': x['lv'], 'score': x['score'], 'note': note})
json.dump(out, open(E + '/p34/p4_scored.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump({'drop': dropped, 'change': changed}, open(E + '/p34/p4_scored_log.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
zero = [x for x in items if x['score'] <= 0]
json.dump(zero, open(E + '/p34/p4_zero_input.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('scored kept', len(out), 'dropped', len(dropped), 'changed', len(changed), '| zero-score to classify', len(zero))
print([c['to'] for c in changed if c['why'].startswith('상용')])
