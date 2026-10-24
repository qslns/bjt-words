"""두 번째 받아쓰기(ReazonSpeech) 공용 판정: 'これは X です' 사이에 넣고 X 부분 가나 읽기가 기대 읽기와 같은지
- 기대·결과 모두 히라가나로, 장음(ー)·おう/おお·えい/ええ 같게 봄
- 결과가 한자 한 글자면 그 한자 읽기 목록(한자 카드 음·훈)에 기대 읽기가 있으면 통과(같은 소리 다른 글자)"""
import re, json
from reazon import in_ctx, kana_of
from kana import kata2hira
cards = {c['c']: c for c in json.load(open('/home/claude/work/kz/kz_cards.json', encoding='utf-8'))}
V = {'a': 'あかさたなはまやらわがざだばぱゃ', 'i': 'いきしちにひみりぎじぢびぴぃ', 'u': 'うくすつぬふむゆるぐずづぶぷゅぅ', 'e': 'えけせてねへめれげぜでべぺぇ', 'o': 'おこそとのほもよろをごぞどぼぽょぉ'}
def vow(c):
    for v, cs in V.items():
        if c in cs: return v
    return None
def nl(s):
    s = kata2hira(s or ''); s = re.sub(r'[^ぁ-ゖー]', '', s); out = ''
    for c in s:
        if c == 'ー' and out:
            c = {'a': 'あ', 'i': 'い', 'u': 'う', 'e': 'い', 'o': 'う'}.get(vow(out[-1]), '')
        out += c
    out = re.sub(r'(?<=[おこそとのほもよろごぞどぼぽょ])お', 'う', out)   # おお → おう
    out = re.sub(r'(?<=[えけせてねへめれげぜでべぺ])え', 'い', out)       # ええ → えい
    out = out.replace('ぢ', 'じ').replace('づ', 'ず')
    return out
def readings(c):
    k = cards.get(c); out = set()
    if not k: return out
    for r in k['on'] + k['kun']:
        out.add(r.replace('(', '').replace(')', '')); out.add(r.split('(')[0])
    return {nl(x) for x in out}
def strip_ctx(t):
    t = re.sub(r'[［］〈〉「」『』、。・\s]', '', t)
    t = re.sub(r'^(これは|コレワ|これわ|コレハ)', '', t); t = re.sub(r'(です|デス)$', '', t)
    return t
def rz_judge(fn, exp_kana, car='n'):
    t, _ = in_ctx(fn, car); mid = strip_ctx(t)
    mk = kana_of(mid) if mid else ''
    e = nl(exp_kana); ok = nl(mid) == e or nl(mk) == e
    if not ok and len(mid) == 1 and e in readings(mid): ok = True
    return {'rz_text': t, 'rz_mid': mid, 'rz_kana': nl(mk) if mk else nl(mid), 'rz_ok': ok}
