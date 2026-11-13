"""BSD json들 → bands.py 입력 형식 한 파일 (usage: python3 -I bsd2txt.py OUT.txt IN.json...)"""
import os
import sys, json
out, ins = sys.argv[1], sys.argv[2:]
n = 0
with open(out, 'w', encoding='utf-8') as f:
    f.write('@@ L1 1\n')
    for p in ins:
        for conv in json.load(open(p, encoding='utf-8')):
            for u in conv.get('conversation', []):
                s = (u.get('ja_sentence') or '').strip()
                if s: f.write(s.replace('\n', ' ') + '\n'); n += 1
print('sentences', n)
