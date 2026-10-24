"""예문 3단계: 남은 걸린 문장 → sfix(sx_2) → 실패한 것 ReazonSpeech로 받아쓰기, 사람이 볼 목록 출력
usage: python3 stage3.py"""
import json, subprocess, os, sys, numpy as np
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
subprocess.run([sys.executable, 'build_sjobs.py', 'sjobs_all.json', 'qa_s_a.jsonl', 'qa_s_live_b.jsonl'], check=True)
done = set()
for p in ('sx_t/spick.json', 'sx_1/spick.json'):
    if os.path.exists(p): done |= set(json.load(open(p, encoding='utf-8')))
keep = set(json.load(open('s_keep.json', encoding='utf-8')))
ov = set(json.load(open('s_override.json', encoding='utf-8')))
J = [j for j in json.load(open('sjobs_all.json', encoding='utf-8')) if (j['name'] not in done and j['name'] not in keep) or j['name'] in ov]
json.dump(J, open('sjobs_2.json', 'w', encoding='utf-8'), ensure_ascii=False)
M = [m for m in json.load(open('sjobs_all_manual.json', encoding='utf-8')) if m[0] not in keep and m[0] not in ov]
json.dump(M, open('sjobs_2_manual.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('sfix jobs', len(J), 'manual', len(M), flush=True)
subprocess.run([sys.executable, 'sfix.py', 'sjobs_2.json', 'sx_2'], check=True)
fails = []
for p in ('sx_t/spick.json', 'sx_1/spick.json', 'sx_2/spick.json'):
    for k, v in json.load(open(p, encoding='utf-8')).items():
        if v.get('fail') and k not in keep: fails.append(k)
from reazon import text_of
from phon import load16
out = {}
for k in sorted(set(fails)):
    x = load16(f'/home/claude/bjt-words/audio/{k}.mp3')
    out[k] = text_of(np.concatenate([np.zeros(8000, np.float32), x, np.zeros(8000, np.float32)]))
json.dump(out, open('fails_rz.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('fails', len(out))
