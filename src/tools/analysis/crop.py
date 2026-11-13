"""Cut a page into a grid of overlapping tiles at full resolution, upscaled 1.5x.
usage: python3 -I crop.py IMAGE OUTDIR ROWS COLS   -> prints tile paths"""
import sys, os
from PIL import Image
img, out, R, C = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
os.makedirs(out, exist_ok=True)
im = Image.open(img).convert('L'); W, H = im.size
base = os.path.splitext(os.path.basename(img))[0]
ov = 0.04
for r in range(R):
    for c in range(C):
        x0 = max(0, int((c / C - ov) * W)); x1 = min(W, int(((c + 1) / C + ov) * W))
        y0 = max(0, int((r / R - ov) * H)); y1 = min(H, int(((r + 1) / R + ov) * H))
        t = im.crop((x0, y0, x1, y1)); t = t.resize((int(t.width * 1.5), int(t.height * 1.5)), Image.LANCZOS)
        p = os.path.join(out, f'{base}_r{r}c{c}.png'); t.save(p); print(p)
