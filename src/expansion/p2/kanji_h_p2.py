# P2 새 한자 99자(앱 950자·옛 자료 407자 밖)의 훈음 h — 음은 KANJIDIC2 korean_h에서 확인, 훈은 표준 훈(한자능력검정·표준국어대사전 쪽)
# on·kun·획수·부수는 jamdict(KANJIDIC2)에서. 구성 s·풀이 x는 P2-5에서 채움
import json, sys, re
sys.path.insert(0, '/home/claude/work/expansion/tools')
from kanji_ref import ref
H = dict(x.split(':') for x in '''誰:누구 수|彼:저 피|僕:종 복|君:임금 군|緑:푸를 록|林:수풀 림|耳:귀 이|校:학교 교|褒:기릴 포|戸:집 호|靴:신 화|叱:꾸짖을 질|弟:아우 제|犬:개 견|卵:알 란|魚:물고기 어|匂:향내 내|寂:고요할 적|浅:얕을 천|眼:눈 안|鏡:거울 경|腕:팔 완|娘:아가씨 낭|漢:한나라 한|山:메 산|草:풀 초|恥:부끄러울 치|帽:모자 모|濯:씻을 탁|腹:배 복|怖:두려워할 포|焼:불사를 소|鼻:코 비|豚:돼지 돈|田:밭 전|舎:집 사|岸:언덕 안|島:섬 도|牛:소 우|砂:모래 사|糖:엿 당|塩:소금 염|橋:다리 교|遊:놀 유|川:내 천|拾:주울 습|泥:진흙 니|涼:서늘할 량|嬢:아가씨 양|乳:젖 유|血:피 혈|歌:노래 가|泳:헤엄칠 영|黄:누를 황|咲:웃을 소|鳥:새 조|飾:꾸밀 식|坂:언덕 판|泣:울 읍|喉:목구멍 후|虫:벌레 충|漫:흩어질 만|糸:실 사|浴:목욕할 욕|絵:그림 회|呂:음률 려|兄:형 형|猫:고양이 묘|箸:젓가락 저|匹:짝 필|弾:탄알 탄|痩:여윌 수|祖:할아버지 조|髪:터럭 발|寺:절 사|湖:호수 호|鉛:납 연|皿:그릇 명|零:떨어질 령|鶏:닭 계|灰:재 회|吹:불 취|磨:갈 마|村:마을 촌|絹:비단 견|悲:슬플 비|雲:구름 운|漬:담글 지|森:수풀 삼|踊:뛸 용|塗:칠할 도|隅:모퉁이 우|毛:털 모|沸:끓을 비|枝:가지 지|輪:바퀴 륜|射:쏠 사|植:심을 식|湯:끓을 탕'''.split('|'))
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
    eum = h.split()[-1]
    if eum not in r['kh']: bad.append((c, h, r['kh']))
    out[c] = {'h': h, 'b': r['rad'], 'bn': radbn.get(r['rad'], ''), 's': '', 'x': '', 'on': r['on'], 'kun': list(dict.fromkeys(kun_fmt(k) for k in r['kun'] if k.strip('-'))), 'n': r['n']}
print('음이 KANJIDIC과 다름:', bad)
print('부수 이름 없음:', ''.join(c for c, e in out.items() if not e['bn']), {e['b'] for e in out.values() if not e['bn']})
json.dump(out, open('/home/claude/work/expansion/p2/kanji_new_p2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(out))
