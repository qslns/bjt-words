#!/usr/bin/env python3
"""카드 미리보기
  python3 preview.py batches/b01.json            → 앱과 똑같은 카드 모양 (한 장에 1~2장)
  python3 preview.py batches/b01.json --sheet     → 검토용 축소판(한 장에 카드 5장: 장면·그림 3칸·쪼개기·소리) ← 평소엔 이걸로
  출력: preview/<이름>.html, <이름>_pN.png (Read로 열어 보기)"""
import json, sys, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import kzc
from PIL import Image
args = [a for a in sys.argv[1:] if not a.startswith('--')]
SHEET = '--sheet' in sys.argv
src = args[0]
out = args[1] if len(args) > 1 else os.path.join(HERE, 'preview', os.path.splitext(os.path.basename(src))[0] + ('_s' if SHEET else ''))
width = args[2] if len(args) > 2 else '1024'
os.makedirs(os.path.dirname(out), exist_ok=True)
cards = kzc.load_batches([src]); d = kzc.data()
comp = []
for e in cards:
    er, wa = kzc.validate(e)
    if er:
        print('검사 오류 — 먼저 고치세요:', e.get('c')); [print('  ', x) for x in er]; sys.exit(1)
    cc = kzc.compile_entry(e)
    ws = sorted((d['W'][i] for i in d['K'][e['c']]['u'] if i in d['W']), key=lambda w: (w.get('ord') is None, w.get('ord') or 0, w['id']))[:8]
    cc['_w'] = [[w['w'], w['r'], w['m'][:10]] for w in ws]
    comp.append(cc)
css = open(os.path.join(HERE, 'kz.css'), encoding='utf-8').read()
js = open(os.path.join(HERE, 'kz_render.js'), encoding='utf-8').read()
page = '''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>:root{--f-ui:"Apple SD Gothic Neo","Noto Sans KR","Noto Sans CJK KR",system-ui,sans-serif;--f-jp:"Hiragino Mincho ProN","Yu Mincho","Noto Serif JP","Noto Serif CJK JP",serif;--f-kyo:var(--f-jp)}
body{margin:0;background:#F4F5F8;font-family:var(--f-ui);color:#1A2133}.wrap{max-width:980px;margin:0 auto;padding:16px;display:flex;flex-direction:column;gap:18px}
.kz-card{background:#fff;border:1px solid #DCE0E8;border-radius:16px;padding:16px}
.pw{display:flex;flex-wrap:wrap;gap:8px;align-items:center}.pw .l{font-size:12px;font-weight:700;color:#7A8296}.pw span.w{display:inline-flex;flex-direction:column;padding:6px 10px;border:1px solid #DCE0E8;border-radius:10px}
.pw b{font-size:22px;font-weight:500;font-family:var(--f-jp)}.pw small{font-size:12px;color:#4A5367;font-family:var(--f-jp)}.pw em{font-style:normal;font-size:13px}
.sr{display:grid;grid-template-columns:88px 1fr;gap:10px;background:#fff;border:1px solid #DCE0E8;border-radius:12px;padding:10px;color:#1A2133}
.sr [lang=ja]{font-family:var(--f-jp)}
.sr .kk{display:flex;flex-direction:column;align-items:center;gap:2px}.sr .kk b{font-family:var(--f-kyo);font-weight:500;font-size:60px;line-height:1}.sr .kk span{font-size:13px;font-weight:700;text-align:center}
.sr .hk{margin:0;font-size:16px;font-weight:800;background:#FFF3C4;border-radius:8px;padding:4px 8px}.sr .hk small{display:block;font-size:12px;font-weight:600;color:#4A5367}
.sr .ps{display:grid;grid-template-columns:repeat(3,170px);gap:8px;margin-top:6px}.sr .ps .kz-pic{max-width:170px}.sr .ps figcaption{font-size:12px}
.sr .tr{display:flex;flex-direction:column;gap:3px;margin-top:6px;font-size:12px}.sr .tr div{display:flex;align-items:center;gap:4px;flex-wrap:wrap}
.sr .tr .bx{display:inline-flex;align-items:center;gap:2px;border:1px solid #DCE0E8;border-radius:6px;padding:1px 4px;background:#fff}.sr .tr .bx svg{width:30px;height:30px}.sr .tr .bx.re{background:#FFF8E1}
.sr .tr i{font-style:normal;color:#4A5367}.sr .sn{margin:4px 0 0;font-size:12px;background:#FDECEA;border-radius:6px;padding:3px 6px}.sr .bs{margin:4px 0 0;font-size:12px}
''' + css + '</style></head><body><div class="wrap" id="w"></div><script>' + js + '''
const C = ''' + json.dumps(comp, ensure_ascii=False) + ''';
const SHEET = __SHEET__;
function bx(c, s, cols, vb, n, r, re) { return '<span class="bx' + (re ? ' re' : '') + '">' + kzBox(c, s, cols, vb) + kzE(n) + (r ? ' <b lang="ja">' + kzE(r) + '</b>' : '') + '</span>'; }
function row(c) {
  const tr = c.t.length ? c.t.map(st => '<div>' + st.pa.map(p => bx(c, p.s, p.c, p.vb, p.n, p.r)).join('+') + '=' + bx(c, st.re.s, st.re.cs, st.re.vb, st.re.n, st.re.r, 1) + '<i>' + kzMark(st.mi) + '</i></div>').join('') : '<p class="bs">' + kzMark(c.bs) + '</p>';
  return '<article class="sr"><div class="kk"><b lang="ja">' + kzE(c.c) + '</b><span>' + kzE(c.h) + '</span></div><div><p class="hk">' + kzMark(c.hook) + (c.br ? '<small>' + kzMark(c.br) + '</small>' : '') + '</p>' +
    '<div class="ps">' + c.p.map(p => kzPanel(c, p)).join('') + '</div><div class="tr">' + tr + '</div><p class="sn">🔊 ' + kzMark(c.snd) + '</p></div></article>';
}
document.getElementById('w').innerHTML = SHEET ? C.map(row).join('') : C.map(c => kzCardHTML(c, {words: '<div class="pw"><span class="l">단어</span>' + c._w.map(w => '<span class="w"><b>' + kzE(w[0]) + '</b><small>' + kzE(w[1]) + '</small><em>' + kzE(w[2]) + '</em></span>').join('') + '</div>'})).join('');
</script></body></html>'''
page = page.replace('__SHEET__', 'true' if SHEET else 'false')
open(out + '.html', 'w', encoding='utf-8').write(page)
import fcntl
with open(os.path.join(HERE, '.shot.lock'), 'w') as lk:   # 여러 작업이 동시에 돌아도 브라우저는 한 번에 하나씩
    fcntl.flock(lk, fcntl.LOCK_EX)
    r = subprocess.run(['node', os.path.join(HERE, 'shot.mjs'), out + '.html', out, width], capture_output=True, text=True, cwd=HERE, timeout=300)
if r.returncode: print(r.stderr[-2000:]); sys.exit(1)
boxes = json.loads(r.stdout.strip().splitlines()[-1])
im = Image.open(out + '_full.png')
# 카드 단위로 잘라 한 장에 최대 1700px 높이
for f in [f for f in os.listdir(os.path.dirname(out)) if f.startswith(os.path.basename(out) + '_p') and f.endswith('.png')]:
    os.remove(os.path.join(os.path.dirname(out), f))
pages = []; cur = []
for top, h in boxes:
    if cur and (top + h - cur[0][0]) > (1800 if SHEET else 1700): pages.append(cur); cur = []
    cur.append((top, h))
if cur: pages.append(cur)
names = []
for i, pg in enumerate(pages):
    t0 = max(0, int(pg[0][0]) - 6); t1 = min(im.size[1], int(pg[-1][0] + pg[-1][1]) + 6)
    nm = f'{out}_p{i}.png'; im.crop((0, t0, im.size[0], t1)).save(nm); names.append(nm)
print('미리보기', len(comp), '장 →', out + '.html'); print('사진:', ' '.join(names))
