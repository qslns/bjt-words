"""단어: 두 인식기 결과를 합쳐 다시 볼 단어 고르기 → consensus 작업 목록
usage: python3 build_wjobs2.py <qa_w_ctx.json> <qa_rz_w.jsonl> <data_app.json> <out_jobs.json>"""
import sys, json, re
from build_wjobs import kata, NA, KE
from acoustic import check
from kana import to_ph
WA = {1268, 1359, 2092, 9294, 9334}   # 実は·あるいは·つきましては·または·それでは: 끝 は는 わ로 읽음
def exp_of(w):
    e = (w.get('tw') or w['r']).replace('〜', '')
    if w['id'] in WA and e.endswith('は'): e = e[:-1] + 'わ'
    return e
def cands(w):
    if w.get('tw'):
        t = w['tw']; T = kata(t)
        return [('n1', NA, t, ''), ('n2', NA, T, ''), ('n3', NA, t, '-10%'), ('n4', NA, T, '-10%'), ('n5', NA, '「' + t + '」', ''),
                ('k1', KE, t, ''), ('k2', KE, T, ''), ('k3', KE, '「' + t + '」', '')]
    r = w['r'].replace('〜', ''); R = kata(r); hw = w['w'].replace('〜', '')
    c = []
    if re.search(r'[一-鿿々]', hw): c += [('n1', NA, hw, ''), ('n1b', NA, hw, '-10%')]
    c += [('n2', NA, r, ''), ('n3', NA, R, ''), ('n4', NA, r, '-10%'), ('n5', NA, R, '-10%'), ('n6', NA, '「' + r + '」', ''), ('n7', NA, R, '+10%')]
    if re.search(r'[一-鿿々]', hw): c.append(('k1', KE, hw, ''))
    c += [('k2', KE, r, ''), ('k3', KE, R, ''), ('k4', KE, '「' + r + '」', '')]
    return c
if __name__ == '__main__':
    Q = {q['key']: q for q in json.load(open(sys.argv[1], encoding='utf-8'))}
    RZ = {}
    for l in open(sys.argv[2], encoding='utf-8'):
        r = json.loads(l); RZ[r['key']] = r
    W = {f"w/{w['id']}": w for w in json.load(open(sys.argv[3], encoding='utf-8'))['words']}
    jobs = []; why = {}
    for key, w in W.items():
        q = Q[key]; z = RZ.get(key); reasons = []
        if q['d'] > 0 or not q['ctx_ok']: reasons.append('ph:' + q['got'])
        if q['why']:
            wy, _ = check(f"/home/claude/bjt-words/audio/{key}.mp3", to_ph(exp_of(w)))
            if wy: reasons.append('ac:' + ','.join(wy))
        if z is None: reasons.append('rz:missing')
        elif not z['rz_ok']: reasons.append('rz:' + z['rz_text'])
        if exp_of(w) != w['r'].replace('〜', ''): reasons.append('exp-changed')
        if reasons:
            jobs.append({'name': key, 'read': exp_of(w), 'trim': 'w', 'cands': cands(w), 'cur_car': 'n', 'why': reasons})
    json.dump(jobs, open(sys.argv[4], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('jobs', len(jobs))
    for j in jobs: print(' ', j['name'], W[j['name']]['w'], j['read'], j['why'])
