"""단어 받아쓰기 결과에서 다시 만들 단어 → fixgen 작업 목록
usage: python3 build_wjobs.py <qa_w.json> <data_app.json> <jobs_out.json>"""
import sys, json, re
NA, KE = 'ja-JP-NanamiNeural', 'ja-JP-KeitaNeural'
def kata(s): return ''.join(chr(ord(c) + 0x60) if 'ぁ' <= c <= 'ゖ' else c for c in s)
def cands(w):
    r = w['r'].replace('〜', ''); R = kata(r); hw = w['w'] if '〜' not in w['w'] else r
    c = []
    if re.search(r'[一-鿿々]', hw): c.append(('n1', NA, hw, ''))
    c += [('n2', NA, r, ''), ('n3', NA, R, ''), ('n4', NA, r, '-10%'), ('n5', NA, R, '-10%'), ('n6', NA, '「' + r + '」', '')]
    if re.search(r'[一-鿿々]', hw): c.append(('k1', KE, hw, ''))
    c += [('k2', KE, r, ''), ('k3', KE, R, '')]
    return c
if __name__ == '__main__':
    Q = json.load(open(sys.argv[1], encoding='utf-8')); W = {f"w/{w['id']}": w for w in json.load(open(sys.argv[2], encoding='utf-8'))['words']}
    bad = [q for q in Q if q['d'] > 0 or q['why'] or not q['ctx_ok']]
    jobs = [{'name': q['key'], 'read': W[q['key']]['r'].replace('〜', ''), 'trim': 'w', 'cands': cands(W[q['key']])} for q in bad]
    json.dump(jobs, open(sys.argv[3], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('jobs', len(jobs))
