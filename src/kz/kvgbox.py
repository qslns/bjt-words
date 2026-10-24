"""KanjiVG 경로 범위(bbox)"""
import re
TOK = re.compile(r'[MmCcSsLlHhVvZzQqTtAa]|-?\d*\.?\d+(?:e-?\d+)?')
def path_points(d):
    pts = []; x = y = 0.0; sx = sy = 0.0; cmd = None; toks = TOK.findall(d); i = 0
    def num():
        nonlocal i
        v = float(toks[i]); i += 1; return v
    while i < len(toks):
        t = toks[i]
        if re.match(r'[A-Za-z]', t): cmd = t; i += 1
        if cmd in 'Mm':
            nx, ny = num(), num()
            if cmd == 'm': nx += x; ny += y
            x, y = nx, ny; sx, sy = x, y; pts.append((x, y)); cmd = 'l' if cmd == 'm' else 'L'
        elif cmd in 'Ll':
            nx, ny = num(), num()
            if cmd == 'l': nx += x; ny += y
            x, y = nx, ny; pts.append((x, y))
        elif cmd in 'Hh':
            nx = num(); x = nx + (x if cmd == 'h' else 0); pts.append((x, y))
        elif cmd in 'Vv':
            ny = num(); y = ny + (y if cmd == 'v' else 0); pts.append((x, y))
        elif cmd in 'Cc':
            a = [num() for _ in range(6)]
            if cmd == 'c': a = [a[0] + x, a[1] + y, a[2] + x, a[3] + y, a[4] + x, a[5] + y]
            pts += [(a[0], a[1]), (a[2], a[3]), (a[4], a[5])]; x, y = a[4], a[5]
        elif cmd in 'Ss':
            a = [num() for _ in range(4)]
            if cmd == 's': a = [a[0] + x, a[1] + y, a[2] + x, a[3] + y]
            pts += [(a[0], a[1]), (a[2], a[3])]; x, y = a[2], a[3]
        elif cmd in 'Zz':
            x, y = sx, sy
        else:
            i += 1
    return pts
def bbox(ds):
    pts = [p for d in ds for p in path_points(d)]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)
