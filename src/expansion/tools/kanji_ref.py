"""한자 참고표 (11/13): jamdict(KANJIDIC2)에서 음독·훈독·획수·부수 번호·한국 음(korean_h)·영어 뜻
쓰기: python3 kanji_ref.py 한자들 > out.json   (또는 import해서 ref(c))"""
import sys, json, unicodedata
from jamdict import Jamdict
_J = None
RAD = {i + 1: unicodedata.normalize('NFKC', chr(0x2F00 + i)) for i in range(214)}
_MEMO = {}
def ref(c):
    if c in _MEMO: return _MEMO[c]
    _MEMO[c] = _ref(c)
    return _MEMO[c]
def _ref(c):
    global _J
    if _J is None: _J = Jamdict()
    r = _J.lookup(c)
    for ch in r.chars:
        if ch.literal != c: continue
        on, kun, kh, mean = [], [], [], []
        for g in ch.rm_groups:
            for x in g.readings:
                if x.r_type == 'ja_on': on.append(x.value)
                elif x.r_type == 'ja_kun': kun.append(x.value)
                elif x.r_type == 'korean_h': kh.append(x.value)
            mean += [m.value for m in g.meanings if m.m_lang in ('', 'en')]
        rn = None
        for x in ch.radicals:
            if x.rad_type == 'classical': rn = int(x.value)
        return {'on': on, 'kun': kun, 'kh': kh, 'en': mean[:6], 'n': ch.stroke_count, 'rad': RAD.get(rn), 'radn': rn, 'grade': ch.grade, 'freq': ch.freq}
    return None
if __name__ == '__main__':
    out = {c: ref(c) for c in ''.join(sys.argv[1:])}
    print(json.dumps(out, ensure_ascii=False, indent=0))
