"""기본 카드 추가 정보(이야기·BJT 포인트·바꿔 말하면·어원·헷갈리는 짝) 읽기.
파일: basic/x/ex_*.txt, 한 줄 = 'bn | st | p | y | o | pr' (p가 '='이면 기존 포인트 유지)
pr 토큰: 'No.N'(본편 번호) / 'BN'(기본 번호) / 표제어(유일해야 함)"""
import glob, re
def load(words, prob):
    ex = {}
    for path in sorted(glob.glob('/home/claude/work/basic/x/ex_*.txt')):
        for k, ln in enumerate(open(path, encoding='utf-8'), 1):
            ln = ln.rstrip('\n')
            if not ln.strip() or ln.startswith('#'): continue
            f = [x.strip() for x in ln.split('|')]
            if len(f) != 6: prob.append(f'extras {path}:{k} fields={len(f)}'); continue
            bn = int(f[0])
            if bn in ex: prob.append(f'extras dup bn {bn}')
            ex[bn] = {'st': f[1], 'p': f[2], 'y': f[3], 'o': f[4], 'pr': [t.strip() for t in f[5].split(',') if t.strip()]}
    byno = {w['ord'] + 1: w for w in words if w.get('ord') is not None}
    bybn = {w['bn']: w for w in words if w.get('bn') is not None}
    def res(tok):
        m = re.fullmatch(r'No\.(\d+)', tok)
        if m: return byno.get(int(m.group(1)))
        m = re.fullmatch(r'B(\d+)', tok)
        if m: return bybn.get(int(m.group(1)))
        c = [w for w in words if w['w'] == tok] or [w for w in words if w['w'].lstrip('〜') == tok.lstrip('〜')]
        if len(c) == 1: return c[0]
        if len(c) > 1: prob.append(f'pr ambiguous {tok}: ' + ', '.join(f"{w['w']}({w['r']})" for w in c))
        return None
    for bn, e in ex.items():
        ids = []
        for t in e['pr']:
            w = res(t)
            if w is None: prob.append(f'pr unresolved #{bn} {t}'); continue
            ids.append(w['id'])
        e['prids'] = ids
    return ex
