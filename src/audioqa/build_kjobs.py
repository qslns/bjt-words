"""한자 받아쓰기 결과(qa_k_ctx.json)에서 다시 만들 읽기 고르기 → fixgen 작업 목록
usage: python3 build_kjobs.py <qa.json> <jobs_out.json> [voice=both|keita]"""
import sys, json
NA, KE = 'ja-JP-NanamiNeural', 'ja-JP-KeitaNeural'
def kata(s): return ''.join(chr(ord(c) + 0x60) if 'ぁ' <= c <= 'ゖ' else c for c in s)
def cands(r, voice='both'):
    R = kata(r)
    n = [('n1', NA, '「' + r + '」', ''), ('n2', NA, r, ''), ('n3', NA, R, ''), ('n4', NA, '『' + r + '』', ''), ('n5', NA, '「' + R + '」', ''),
         ('n6', NA, '「' + r + '」', '-10%'), ('n7', NA, '「' + r + '」', '+10%'),
         ('n8', NA, '『' + R + '』', ''), ('n9', NA, R, '-10%'), ('n10', NA, r, '-10%'), ('n11', NA, R, '+10%')]
    k = [('k1', KE, '「' + r + '」', ''), ('k2', KE, r, ''), ('k3', KE, R, ''), ('k4', KE, '『' + r + '』', ''), ('k5', KE, '「' + r + '」', '-10%')]
    return (n + k) if voice == 'both' else k
if __name__ == '__main__':
    Q = json.load(open(sys.argv[1], encoding='utf-8')); voice = sys.argv[3] if len(sys.argv) > 3 else 'both'
    bad = [q for q in Q if q['key'].startswith('kr/') and (q['d'] > 0 or q['why'] or not q['ctx_ok'])]
    jobs = [{'name': q['key'], 'read': q['reads'][0].replace('(', '').replace(')', ''), 'trim': 'k', 'cands': cands(q['reads'][0].replace('(', '').replace(')', ''), voice)} for q in bad]
    json.dump(jobs, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('jobs', len(jobs))
