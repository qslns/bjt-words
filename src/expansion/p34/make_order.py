# P3+P4 합친 본편 순서(ord 1500~): 같은 점수(BSD·chABSA·드릴 빈도)로 복원 2,312 + N3·N2(점수>0) → 점수 0인 복원(원래 순서) → 점수 0인 N3·N2(분류 뒤)
# 같은 점수면 복원 먼저(업무 말), 그다음 N3 → N2. P4 새 카드 id는 20001부터(목록 순서대로)
import json, os
E = '/home/claude/work/expansion'
ro = json.load(open(E + '/restore_order.json', encoding='utf-8'))
p4 = json.load(open(E + '/p34/p4_scored.json', encoding='utf-8'))
zp = E + '/p34/p4_zero_final.json'
p4z = json.load(open(zp, encoding='utf-8')) if os.path.exists(zp) else []
# 11/13 11:20 겹침(お·ご 붙은 꼴 등) — 복원·N3N2에서 뺌
DROP_R = {3808: '기본 お祭り(10286)와 같은 말', 807: '앱의 休み와 같은 말(お는 정중)', 1420: '앱의 互い와 같은 말', 1423: '앱의 昼(낮·점심)와 같은 말',
          1599: '앱의 お土産와 같은 말', 2219: '앱의 お見舞い와 같은 말', 3521: '앱의 お菓子와 같은 말'}
DROP_N = {'Jn2-1553': '복원 목록의 生意気(3275)', 'Jn2-1509': '앱의 お手洗い', 'Jn3-739': '앱의 お酒'}
ro = [x for x in ro if x['id'] not in DROP_R]
p4 = [x for x in p4 if x['src'] not in DROP_N]
p4z = [x for x in p4z if x['src'] not in DROP_N]
R = [dict(kind='R', id=x['id'], w=x['w'], r=x['r'], m=x['m'], score=x['score'], tier=x['old_tier'], key=(0,)) for x in ro]
P = [dict(kind='N', src=x['src'], w=x['w'], r=x['r'], en=x['en'], lv=x['lv'], score=x['score'], note=x['note']) for x in p4]
Z = [dict(kind='N', src=x['src'], w=x['w'], r=x['r'], en=x['en'], lv=x['lv'], score=0, note=x.get('note', '')) for x in p4z]
pos = {id(x): i for i, x in enumerate(R)}
scored = [x for x in R if x['score'] > 0] + P
scored.sort(key=lambda x: (-x['score'], 0 if x['kind'] == 'R' else 1, 0 if x.get('lv') == 'N3' else 1, pos.get(id(x), 0)))
order = scored + [x for x in R if x['score'] <= 0] + Z
# 새 N3·N2 카드 id는 한 번 정하면 고정(p34/p4_ids.json: src → id) — 카드·음성 파일 이름이 id라서
idp = E + '/p34/p4_ids.json'
ids = json.load(open(idp, encoding='utf-8')) if os.path.exists(idp) else {}
nid = max(list(ids.values()) + [20000]) + 1
for i, x in enumerate(order):
    x['ord'] = 1500 + i
    if x['kind'] == 'N':
        if x['src'] not in ids: ids[x['src']] = nid; nid += 1
        x['id'] = ids[x['src']]
    x.pop('key', None)
json.dump(ids, open(idp, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(order, open(E + '/p34/main_order.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('total', len(order), '→ No.1501 ~', 1500 + len(order))
for p in range(0, len(order), 500):
    ch = order[p:p + 500]
    print('%d부 No.%d–%d: 복원 %d · N3N2 %d · 점수 %.2f→%.2f' % (4 + p // 500, 1501 + p, 1500 + p + len(ch), sum(x['kind'] == 'R' for x in ch), sum(x['kind'] == 'N' for x in ch), ch[0]['score'], ch[-1]['score']))
