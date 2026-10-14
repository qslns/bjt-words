import glob, re
Y = {'ゃ': 'ya', 'ゅ': 'yu', 'ょ': 'yo'}
T = dict(zip('あいうえおかきくけこがぎぐげごさしすせそざじずぜぞたちつてとだぢづでどなにぬねのはひふへほばびぶべぼぱぴぷぺぽまみむめもやゆよらりるれろわを',
             '아이우에오카키쿠케코가기구게고사시스세소자지즈제조타치쓰테토다지즈데도나니누네노하히후헤호바비부베보파피푸페포마미무메모야유요라리루레로와오'))
TY = {'き': '캬큐쿄', 'し': '샤슈쇼', 'ち': '챠츄쵸', 'に': '냐뉴뇨', 'ひ': '햐휴효', 'み': '먀뮤묘', 'り': '랴류료', 'ぎ': '갸규교', 'じ': '쟈쥬죠', 'び': '뱌뷰뵤', 'ぴ': '퍄퓨표'}
def add_final(s, fin):  # 받침 추가 (ㄴ=4, ㅅ=19)
    if not s: return s
    c = ord(s[-1]) - 0xAC00
    if c < 0 or c > 11171 or c % 28: return None
    return s[:-1] + chr(0xAC00 + c + fin)
def tr(h):
    out = ''; i = 0
    while i < len(h):
        ch = h[i]
        if i + 1 < len(h) and h[i + 1] in Y and ch in TY:
            out += TY[ch]['ゃゅょ'.index(h[i + 1])]; i += 2; continue
        if ch == 'ん':
            r = add_final(out, 4); out = r if r else out + 'ㄴ'; i += 1; continue
        if ch == 'っ':
            r = add_final(out, 19); out = r if r else out + 'ㅅ'; i += 1; continue
        if ch == 'ー': i += 1; continue
        out += T.get(ch, '?'); i += 1
    return out
flag = []
for f in sorted(glob.glob('/home/claude/work/kanji_mn/mn/0*.tsv')):
    for line in open(f, encoding='utf-8').read().split('\n'):
        if not line.strip(): continue
        c, t = line.split('\t')
        for m in re.finditer(r'([가-힣]+)\(([ぁ-ゟ]+)\)', t):
            pre, h = m.group(1), m.group(2)
            x = tr(h)
            if pre.endswith(x): continue
            # 음차 시도로 보이는지: 첫 음절 같거나 길이 같고 절반 이상 일치
            tail = pre[-len(x):] if len(pre) >= len(x) else pre
            same = sum(1 for a, b in zip(tail, x) if a == b)
            if same >= max(1, len(x) // 2) or (tail and x and tail[0] == x[0]):
                flag.append((c, pre, h, x, t))
for x in flag: print(x)
print(len(flag))
