"""소리 모양 검사(받아쓰기와 별개): 무음·길이·끝에 따로 붙은 짧은 잡음·첫 자음 앞 긴 'ㅅ' 바람 소리"""
import numpy as np
from phon import load16
def frames(x, sr=16000, hop=0.005, win=0.02):
    H = int(hop * sr); Wn = int(win * sr); out = []
    for i in range(0, max(1, len(x) - Wn), H):
        s = x[i:i + Wn]; rms = np.sqrt((s ** 2).mean()) + 1e-12; db = 20 * np.log10(rms)
        sp = np.abs(np.fft.rfft(s * np.hanning(Wn))) ** 2; f = np.fft.rfftfreq(Wn, 1 / sr)
        tot = sp.sum() + 1e-18; hi = sp[f > 3000].sum() / tot
        s0 = s - s.mean(); ac = np.correlate(s0, s0, 'full')[Wn - 1:]; ac /= (ac[0] + 1e-12)
        per = ac[int(sr / 400):int(sr / 70)].max()
        out.append((i / sr, db, hi, per))
    return out
FRIC = ('s', 'sh', 'h', 'f', 'ts', 'ch', 'hy', 'z', 'j')
def check(fn, exp_ph):
    """exp_ph: 기대 음소 목록. 문제 목록을 돌려줌(빈 목록 = 통과)"""
    x = load16(fn); dur = len(x) / 16000; why = []
    pk = np.abs(x).max()
    if pk < 0.08: why.append('quiet %.2f' % pk)
    F = frames(x)
    on = next((t for t, db, hi, per in F if db > -50), None)
    vo = next((t for t, db, hi, per in F if db > -30 and hi < 0.2), None)   # 모음 같은 공명음 시작
    VLS = ('k', 't', 's', 'sh', 'ch', 'ts', 'h', 'f', 'p', 'ky', 'hy', 'py', 'cl')
    def all_devoiceable(ph):
        vs = [i for i, x in enumerate(ph) if x in ('a', 'i', 'u', 'e', 'o', 'N')]
        return bool(vs) and all(ph[i] in ('i', 'u') and i > 0 and ph[i - 1] in VLS and (i + 1 == len(ph) or ph[i + 1] in VLS) for i in vs)
    if on is None: why.append('no sound'); return why, dur
    if vo is None:
        if not all_devoiceable(exp_ph): why.append('no voice')
        return why, dur
    pre = vo - on
    first = exp_ph[0] if exp_ph else ''
    VL = ('k', 't', 's', 'sh', 'ch', 'ts', 'h', 'f', 'p', 'ky', 'hy', 'py', 'cl')
    devoice = len(exp_ph) >= 3 and first in VL and exp_ph[1] in ('i', 'u') and exp_ph[2] in VL   # きく·きた처럼 첫 모음이 무성화되는 꼴은 원래 길게 들림
    # 첫소리가 마찰음이 아닌데(모음·파열음·비음 등) 유성음 앞에 0.08초 넘는 높은 소리 = 'ㅅ' 같은 바람 소리
    if first not in FRIC and pre > 0.08 and not devoice:
        hiF = [hi for t, db, hi, per in F if on <= t < vo and db > -50]
        if hiF and np.mean(hiF) > 0.6: why.append('fricative-onset %.3fs' % pre)
    # 끝에 따로 붙은 짧은 덩어리(꼬리 잡음): 마지막 소리 덩어리가 0.09초 미만이고 앞과 0.04초 이상 떨어짐
    act = [db > -45 for t, db, hi, per in F]
    segs = []; st = None
    for k, a in enumerate(act + [False]):
        if a and st is None: st = k
        if not a and st is not None: segs.append((st * 0.005, k * 0.005)); st = None
    segs = [s for s in segs if s[1] - s[0] >= 0.015]
    if len(segs) >= 2:
        a, b = segs[-1]; gap = a - segs[-2][1]
        last = exp_ph[-1] if exp_ph else ''
        if b - a < 0.09 and gap >= 0.04 and not (len(exp_ph) >= 2 and exp_ph[-1] in ('u', 'i') and exp_ph[-2] in ('ts', 'k', 's', 'sh', 'ch', 'f', 'h')):
            why.append('tail %.2fs after %.2fs gap' % (b - a, gap))
    return why, dur
if __name__ == '__main__':
    import sys
    from kana import to_ph
    for fn, r in zip(sys.argv[1::2], sys.argv[2::2]):
        print(fn, r, check(fn, to_ph(r)))
