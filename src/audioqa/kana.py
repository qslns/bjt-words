"""히라가나/가타카나 → openjtalk 음소(phoneme-ctc 모델과 같은 기호). 비교용 정규화도 여기."""
import re
H2 = {'きゃ':'ky a','きゅ':'ky u','きょ':'ky o','ぎゃ':'gy a','ぎゅ':'gy u','ぎょ':'gy o','しゃ':'sh a','しゅ':'sh u','しょ':'sh o','しぇ':'sh e',
 'じゃ':'j a','じゅ':'j u','じょ':'j o','じぇ':'j e','ちゃ':'ch a','ちゅ':'ch u','ちょ':'ch o','ちぇ':'ch e','ぢゃ':'j a','ぢゅ':'j u','ぢょ':'j o',
 'にゃ':'ny a','にゅ':'ny u','にょ':'ny o','ひゃ':'hy a','ひゅ':'hy u','ひょ':'hy o','びゃ':'by a','びゅ':'by u','びょ':'by o','ぴゃ':'py a','ぴゅ':'py u','ぴょ':'py o',
 'みゃ':'my a','みゅ':'my u','みょ':'my o','りゃ':'ry a','りゅ':'ry u','りょ':'ry o','てぃ':'t i','でぃ':'d i','でゅ':'dy u','とぅ':'t u','どぅ':'d u',
 'ふぁ':'f a','ふぃ':'f i','ふぇ':'f e','ふぉ':'f o','ふゅ':'fy u','うぃ':'w i','うぇ':'w e','うぉ':'w o','ゔぁ':'v a','ゔぃ':'v i','ゔぇ':'v e','ゔぉ':'v o',
 'つぁ':'ts a','つぃ':'ts i','つぇ':'ts e','つぉ':'ts o','くぁ':'kw a','ぐぁ':'gw a','いぇ':'y e'}
H1 = {'あ':'a','い':'i','う':'u','え':'e','お':'o','か':'k a','き':'k i','く':'k u','け':'k e','こ':'k o','が':'g a','ぎ':'g i','ぐ':'g u','げ':'g e','ご':'g o',
 'さ':'s a','し':'sh i','す':'s u','せ':'s e','そ':'s o','ざ':'z a','じ':'j i','ず':'z u','ぜ':'z e','ぞ':'z o','た':'t a','ち':'ch i','つ':'ts u','て':'t e','と':'t o',
 'だ':'d a','ぢ':'j i','づ':'z u','で':'d e','ど':'d o','な':'n a','に':'n i','ぬ':'n u','ね':'n e','の':'n o','は':'h a','ひ':'h i','ふ':'f u','へ':'h e','ほ':'h o',
 'ば':'b a','び':'b i','ぶ':'b u','べ':'b e','ぼ':'b o','ぱ':'p a','ぴ':'p i','ぷ':'p u','ぺ':'p e','ぽ':'p o','ま':'m a','み':'m i','む':'m u','め':'m e','も':'m o',
 'や':'y a','ゆ':'y u','よ':'y o','ら':'r a','り':'r i','る':'r u','れ':'r e','ろ':'r o','わ':'w a','を':'o','ん':'N','っ':'cl','ゔ':'v u',
 'ぁ':'a','ぃ':'i','ぅ':'u','ぇ':'e','ぉ':'o','ゃ':'y a','ゅ':'y u','ょ':'y o','ゎ':'w a'}
def kata2hira(s): return ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in s)
def to_ph(kana, prev=()):
    """prev: 바로 앞 음소들(토큰이 'ー'로 시작할 때 앞 모음을 잇기 위해)"""
    s = kata2hira(kana); out = []; i = 0
    while i < len(s):
        if s[i:i+2] in H2: out += H2[s[i:i+2]].split(); i += 2; continue
        c = s[i]
        if c == 'ー':
            v = next((p for p in reversed(list(prev) + out) if p in 'aiueo'), None)
            if v: out.append(v)
        elif c in H1: out += H1[c].split()
        i += 1
    return out
VOW = set('aiueo')
def norm(ph):
    """비교용: 무성 모음 I/U → i/u, えい→ええ, おう→おお(장음) 같은 것으로 취급, 쉼 기호 제거"""
    p = [x.lower() if x in ('I', 'U') else x for x in ph if x not in ('pau', 'sil')]
    out = []
    for x in p:
        if out and out[-1] in VOW:
            if (out[-1], x) in (('e', 'i'), ('o', 'u')): x = out[-1]
        out.append(x)
    return out
def ed(a, b):
    """편집 거리 + 정렬"""
    n, m = len(a), len(b); D = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): D[i][0] = i
    for j in range(m + 1): D[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i][j] = min(D[i-1][j] + 1, D[i][j-1] + 1, D[i-1][j-1] + (a[i-1] != b[j-1]))
    return D[n][m]
