"""contact sheets: python3 -I sheet.py IMG_DIR OUT_DIR"""
import sys, os, glob
from PIL import Image, ImageDraw, ImageFont
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
fs = sorted(glob.glob(os.path.join(src, 'p*.jpg')))
TW, TH, C, R = 300, 424, 6, 4
for si in range(0, len(fs), C * R):
    sh = Image.new('RGB', (C * TW, R * (TH + 24)), 'white'); d = ImageDraw.Draw(sh)
    for k, f in enumerate(fs[si:si + C * R]):
        im = Image.open(f).convert('RGB'); im.thumbnail((TW, TH))
        x, y = (k % C) * TW, (k // C) * (TH + 24)
        sh.paste(im, (x, y + 24)); d.text((x + 4, y + 4), os.path.basename(f), fill='red')
    sh.save(os.path.join(out, f'sheet_{si // (C * R) + 1}.jpg'), quality=80)
print('ok')
