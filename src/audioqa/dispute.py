"""두 받아쓰기가 다를 때: 음소 인식기 안에서 '정답 읽기' vs 'ReazonSpeech가 들은 읽기' 점수 차(Δ)
Δ = 점수(정답) - 점수(다른 쪽).  Δ가 크면(>2) 정답 쪽이 확실, 작거나 음수면 애매/틀림
usage: python3 dispute.py <qa_rz.json> <out.json>"""
import sys, json, re, numpy as np
from phon import load16, logits, ctc_score
from qa_ctx import CAR, PE, QE
from kana import to_ph, norm, kata2hira
R = '/home/claude/bjt-words'
J = json.load(open(R + '/tools/kanji_voice_jobs.json', encoding='utf-8'))
voice = {j['key']: j.get('v', '') for j in J['kr']}
def car_of(key):
    if key.startswith('k/'): return 'k' if all('Keita' in voice.get(p, '') for p in J['rep'][key]) else 'n'
    return 'k' if 'Keita' in voice.get(key, '') else 'n'
z = np.zeros(int(0.15 * 16000), np.float32)
out = []
for r in json.load(open(sys.argv[1], encoding='utf-8')):
    if r['ok']: continue
    mk = kata2hira(r['mk'] or '')
    mk = re.sub(r'[^ぁ-ゖー]', '', mk)
    if not mk: out.append(dict(r, delta=None, note='asr-letters')); continue
    car = car_of(r['key']); PRE, POST = CAR[car]
    lp = logits(np.concatenate([PRE, z, load16(f"{R}/audio/{r['key']}.mp3"), z, POST]))
    e = norm(PE + to_ph(r['exp']) + QE); a = norm(PE + to_ph(mk) + QE)
    d = round(ctc_score(lp, e) - ctc_score(lp, a), 2)
    out.append(dict(r, delta=d, alt=mk))
    print(r['key'], r['exp'], 'vs', mk, 'Δ', d, flush=True)
json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
