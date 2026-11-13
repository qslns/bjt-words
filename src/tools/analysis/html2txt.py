"""BJT 공개 샘플 HTML → 일본어 줄만 (usage: python3 -I html2txt.py OUT.txt IN.html...)"""
import os
import sys, re, html
out, ins = sys.argv[1], sys.argv[2:]
JP = re.compile(r'[぀-ヿ一-鿿]')
with open(out, 'w', encoding='utf-8') as f:
    f.write('@@ L1 1\n')
    for p in ins:
        t = open(p, encoding='utf-8', errors='replace').read()
        t = re.sub(r'(?is)<(script|style).*?</\1>', ' ', t)
        t = re.sub(r'(?i)<br\s*/?>|</p>|</div>|</li>|</tr>|</h\d>', '\n', t)
        t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
        for line in t.split('\n'):
            line = re.sub(r'\s+', ' ', line).strip()
            if len(JP.findall(line)) >= 4: f.write(line + '\n')
