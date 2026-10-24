"""예문 받아쓰기 결과 분류: 사람이 볼 목록만 남기기
usage: python3 triage_s.py <qa_s_live.jsonl> [mg_seg=2] [mg_txt=5]"""
import sys, json, re
def benign(f):
    e, h = f['exp'].split(), f['heard'].split()
    # という → とゆう
    if 'i u' in f['exp'] and 'y u u' in f['heard'] and ''.join(e).replace('iu', 'yuu') == ''.join(h): return True
    # 쉼(、) 앞뒤 'cl' 끼어듦만 다름
    if [x for x in h if x != 'cl'] == [x for x in e if x != 'cl']: return True
    # 장음 길이만 다름(가타카나 외래어 끝 등)
    if re.sub(r'(a|i|u|e|o)\1+', r'\1', ' '.join(h).replace(' ', '')) == re.sub(r'(a|i|u|e|o)\1+', r'\1', ' '.join(e).replace(' ', '')) and f['k'] == 'txt' and re.search(r'[ァ-ヺー]', f['u']): return True
    return False
if __name__ == '__main__':
    P = sys.argv[1]; MS = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0; MT = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
    out = []; n = 0
    for l in open(P, encoding='utf-8'):
        r = json.loads(l); n += 1; keep = []
        for f in r['fl']:
            dig = bool(re.search(r'[0-9０-９]', f['u']))
            if benign(f): continue
            if f['k'] == 'seg' and f['mg'] > MS: keep.append(f)
            elif f['k'] == 'txt' and (dig and f['mg'] > 0.5 or f['mg'] > MT): keep.append(f)
        rate = r['d'] / max(r['n'], 1)
        if keep or rate > 0.15: out.append((r, keep, rate))
    print('sentences', n, 'to review', len(out))
    for r, keep, rate in out:
        v = 'K' if r['i'] == 1 else 'N'
        print(f"{r['id']}-{r['i']} [{v}] d={r['d']}/{r['n']} | {r['j'].replace('{','').replace('}','')}")
        for f in keep: print(f"     {f['k']} {f['u']}: {f['exp']} → {f['heard']}  mg {f['mg']}")
        if rate > 0.15: print('     GOT:', r['got'])
