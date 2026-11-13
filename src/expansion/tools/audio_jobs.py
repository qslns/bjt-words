#!/usr/bin/env python3
"""새 카드 음성 작업 목록 만들기 (11/13)
쓰기: python3 audio_jobs.py CARDS.jsonl [CARDS2.jsonl …] --out JOBS.json [--only-changed OLD_WORDS.json]
- 단어: audio/w/<id>.mp3, 나나미. 글 = 표제어(한자 단어) · 읽기(〜 표제·한자 한 글자·가나 표제) · は로 시작하는 히라가나 읽기는 가타카나(は→わ 방지)
- 예문: audio/s/<id>-<n>.mp3, 0·2번 나나미 · 1번 게이타. 글 = 루비 뺀 글에 tts_subs.json(지금 덱에서 늘 가나로 바꿔 넣은 것: 明日→あす 등)을 적용
- --only-changed: 복원 카드는 옛 예문과 글(루비 뺀 것)이 같으면 옛 파일을 그대로 쓰므로 목록에서 뺌(대신 검사 목록에 넣음)
결과 JOBS.json: make_audio.py 입력 꼴 [{f, v, t}] + 'tt' 사전({"id-n": 글}, append_cards.py --tt에 씀)"""
import sys, os, json, argparse, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cardlib import strip_ruby, ruby_segments, is_kanji, kata
SUBS = {tuple(k.split('|')): v for k, v in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tts_subs.json'), encoding='utf-8')).items()}
N, K = 'ja-JP-NanamiNeural', 'ja-JP-KeitaNeural'
# 11/13 P2 받아쓰기에서 TTS가 다른 읽기로 읽은 것 → 루비가 이 읽기면 늘 가나로 넣음(私를 わたし로, 君을 くん으로, 米를 べい로 …)
FORCE = {('私', 'わたくし'), ('君', 'きみ'), ('米', 'こめ'), ('星', 'ほし'), ('町', 'まち'), ('後', 'のち'), ('背', 'せい'), ('年', 'とし'), ('月', 'つき'), ('離', 'ばな'), ('止', 'ど')}
def word_text(c):
    w, r = c['w'], c['r']
    core = w.strip('〜～')
    if core != w or len(core) == 1 or not any(is_kanji(ch) for ch in core):
        t = r
        if t.startswith('は'): t = kata(t)
        return t
    return w
def sent_text(j):
    segs, plain = ruby_segments(j)
    out, pos = '', 0
    for b, rd, a, z, tg in segs:
        out += plain[pos:a]
        if SUBS.get((b, rd), 0) >= 2 or (b, rd) in FORCE:
            out += kata(rd) if rd.startswith('は') else rd   # は로 시작하는 히라가나는 조사 わ로 읽힘(はこ→わこ) → 가타카나
        else: out += b
        pos = z
    out += plain[pos:]
    return out
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('files', nargs='+'); ap.add_argument('--out', required=True); ap.add_argument('--only-changed')
    a = ap.parse_args()
    old = {}
    if a.only_changed:
        for w in json.load(open(a.only_changed, encoding='utf-8')): old[w['id']] = w
    jobs, tt, reuse = [], {}, []
    for f in a.files:
        for line in open(f, encoding='utf-8'):
            line = line.strip()
            if not line: continue
            c = json.loads(line)
            o = old.get(c['id'])
            if not o: jobs.append({'f': 'audio/w/%d.mp3' % c['id'], 'v': N, 't': word_text(c)})
            else: reuse.append('audio/w/%d.mp3' % c['id'])
            for n, e in enumerate(c['e']):
                t = sent_text(e['j'])
                tt['%d-%d' % (c['id'], n)] = t
                if o and n < len(o['e']) and strip_ruby(o['e'][n]['j']) == strip_ruby(e['j']):
                    tt['%d-%d' % (c['id'], n)] = o['e'][n].get('t') or t; reuse.append('audio/s/%d-%d.mp3' % (c['id'], n)); continue
                jobs.append({'f': 'audio/s/%d-%d.mp3' % (c['id'], n), 'v': K if n == 1 else N, 't': t})
    json.dump(jobs, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump(tt, open(a.out.replace('.json', '_tt.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump(reuse, open(a.out.replace('.json', '_reuse.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('jobs', len(jobs), '(words %d, sentences %d) · reuse old files %d' % (sum(j['f'].startswith('audio/w/') for j in jobs), sum(j['f'].startswith('audio/s/') for j in jobs), len(reuse)))
