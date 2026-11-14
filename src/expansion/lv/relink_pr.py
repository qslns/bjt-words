#!/usr/bin/env python3
"""앞 단계에서 '아직 없는 말'이라 뺀 pr(짝·헷갈림 연결)을, 그 말이 들어온 뒤에 다시 잇기 (11/14)
usage: python3 relink_pr.py DATA_IN DATA_OUT LOG...   (LOG = append_cards 출력: '경고: pr 못 찾음 <id> <표제> → 뺌')
- 표제가 이제 앱에 있으면 그 카드 pr 끝에 붙임(이미 있으면 그대로). 여전히 없는 것은 lv/pr_pending.txt에 남김"""
import sys, json, re
D = json.load(open(sys.argv[1], encoding='utf-8')); W = {w['id']: w for w in D['words']}
heads = {}
for w in D['words']:
    heads.setdefault(w['w'], w['id']); heads.setdefault(w['w'].strip('〜～'), w['id'])
done, still = 0, []
for f in sys.argv[3:]:
    for line in open(f, encoding='utf-8'):
        m = re.match(r'경고: pr 못 찾음 (\d+) (.+?) → 뺌', line.strip())
        if not m: continue
        cid, x = int(m.group(1)), m.group(2)
        if cid not in W: continue
        tid = heads.get(x) or heads.get(x.strip('〜～'))
        if tid and tid != cid:
            pr = W[cid].setdefault('pr', [])
            if tid not in pr: pr.append(tid); done += 1
        else: still.append('%d %s' % (cid, x))
open(sys.argv[2], 'w', encoding='utf-8').write(json.dumps(D, ensure_ascii=False, separators=(',', ':')))
open('/home/claude/work/expansion/lv/pr_pending.txt', 'w', encoding='utf-8').write('\n'.join(sorted(set(still))) + '\n')
print('다시 이음', done, '· 아직 없음', len(set(still)))
