"""짧은 소리(한자 읽기·대표 소리·단어)를 'これは … です' 사이에 넣고 받아쓰기 + 소리 모양 검사
usage: python3 qa_ctx.py kanji <audio_dir> <jobs.json> <out.json>
       python3 qa_ctx.py words <audio_dir> <data_app.json> <out.json>
       python3 qa_ctx.py files <list.json: [[name, file, reading]]> <out.json>"""
import sys, json, time, numpy as np
from phon import load16, logits, greedy, ctc_score
from kana import to_ph, norm, ed
from align import heard_spans
from acoustic import check
D = '/tmp/claude-0/-home-claude/4ecb1043-4c6e-5d36-a7b6-577be7533edc/scratchpad/ten/'
CAR = {'n': (load16(D + 'pre_n.wav'), load16(D + 'post_n.wav')), 'k': (load16(D + 'pre_k.wav'), load16(D + 'post_k.wav'))}
PE = ['k', 'o', 'r', 'e', 'w', 'a']; QE = ['d', 'e', 's', 'u']
def judge(fn, exp, gap=0.15, car='n'):
    """car: 앞뒤 말소리 목소리('n' 나나미, 'k' 게이타) — 후보와 같은 목소리로"""
    PRE, POST = CAR[car]
    x = load16(fn); z = np.zeros(int(gap * 16000), np.float32)
    lp = logits(np.concatenate([PRE, z, x, z, POST])); G = greedy(lp)
    En = norm(PE + exp + QE); a, b = len(PE), len(PE) + len(exp)
    d_all, H = heard_spans(En, norm(G), [(0, a), (a, b), (b, len(En))])
    mid = H[1]; d = ed(En[a:b], mid)
    mg = round(ctc_score(lp, En) - ctc_score(lp, En[:a] + mid + En[b:]), 2) if mid else -99
    why, dur = check(fn, exp)
    return {'got': ' '.join(mid), 'd': d, 'mg': mg, 'ctx_ok': H[0] == En[:a] and H[2] == En[b:], 'why': why, 'dur': round(dur, 2)}
if __name__ == '__main__':
    mode = sys.argv[1]; items = []
    if mode == 'kanji':
        A, J = sys.argv[2], json.load(open(sys.argv[3], encoding='utf-8')); OUT = sys.argv[4]
        rd = {j['key']: j['t'].strip('「」') for j in J['kr']}
        items = [(k, f'{A}/{k}.mp3', [r]) for k, r in rd.items()] + [(k, f'{A}/{k}.mp3', [rd[p] for p in parts]) for k, parts in J['rep'].items()]
    elif mode == 'words':
        A, W = sys.argv[2], json.load(open(sys.argv[3], encoding='utf-8'))['words']; OUT = sys.argv[4]
        items = [(f"w/{w['id']}", f"{A}/w/{w['id']}.mp3", [w['r'].replace('〜', '')]) for w in W]
    else:
        L = json.load(open(sys.argv[2], encoding='utf-8')); OUT = sys.argv[3]
        items = [(n, f, [r]) for n, f, r in L]
    res = []; t0 = time.time()
    for n, (key, fn, reads) in enumerate(items):
        exp = sum((to_ph(r.replace('(', '').replace(')', '')) for r in reads), [])
        j = judge(fn, exp); j.update(key=key, reads=reads, exp=' '.join(exp)); res.append(j)
        if n % 200 == 0: print(n, len(items), round(time.time() - t0), flush=True)
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('done', len(res), 'mismatch', sum(1 for r in res if r['d'] > 0), 'acoustic', sum(1 for r in res if r['why']), round(time.time() - t0))
