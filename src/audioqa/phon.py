"""일본어 음소 인식(prj-beatrice/japanese-hubert-base-phoneme-ctc-v4) — 음성이 실제로 무슨 소리인지 받아쓰기
계산은 ONNX Runtime(같은 모델을 내보낸 hubert_ctc.onnx, torch와 결과 동일 확인), CTC 점수는 torch"""
import os, subprocess, numpy as np, torch, onnxruntime as ort
from transformers import Wav2Vec2Processor
torch.set_num_threads(2)
M = 'prj-beatrice/japanese-hubert-base-phoneme-ctc-v4'
proc = Wav2Vec2Processor.from_pretrained(M)
_so = ort.SessionOptions(); _so.intra_op_num_threads = int(os.environ.get('ORT_THREADS', '2')); _so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
sess = ort.InferenceSession(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hubert_ctc.onnx'), _so, providers=['CPUExecutionProvider'])
VOC = proc.tokenizer.get_vocab(); ID2 = {v: k for k, v in VOC.items()}
SKIP = {'PAD', 'UNK', 'SOS', 'EOS', 'pau', 'sil'}
def load16(fn):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', fn, '-f', 's16le', '-ac', '1', '-ar', '16000', '-'], capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768
def logits(x):
    sr = 16000; a = np.concatenate([np.zeros(sr, np.float32), x, np.zeros(sr // 2, np.float32)])
    iv = proc(a, sampling_rate=sr, return_tensors='np')['input_values'].astype(np.float32)
    return torch.from_numpy(sess.run(None, {'input_values': iv})[0][0]).log_softmax(-1)
def greedy(lp):
    ids = lp.argmax(-1).tolist(); out = []; prev = None
    for i in ids:
        if i != prev and i != VOC['PAD']:
            t = ID2[i]
            if t not in SKIP: out.append(t)
        prev = i
    return out
def ctc_score(lp, seq):
    """기대 음소열의 CTC 로그 우도(합)"""
    if not seq: return -1e9
    tgt = torch.tensor([[VOC[p] for p in seq]])
    return -torch.nn.functional.ctc_loss(lp.unsqueeze(1), tgt, torch.tensor([lp.shape[0]]), torch.tensor([len(seq)]), blank=VOC['PAD'], reduction='sum', zero_infinity=True).item()
if __name__ == '__main__':
    import sys
    for fn in sys.argv[1:]:
        lp = logits(load16(fn)); print('%-24s %s' % (fn.split('/')[-1], ' '.join(greedy(lp))))
def logits_chunked(x, gap=0.35, thr_db=-45.0):
    """긴 쉼(gap초 이상)에서 잘라 조각마다 인식 → 이어 붙임. 한 번에 넣으면 긴 쉼 뒤 문장을 통째로 빠뜨리는 일이 있어서(10/22 확인)"""
    sr = 16000; H = int(0.01 * sr)
    e = np.array([np.sqrt((x[i:i + H] ** 2).mean() + 1e-12) for i in range(0, len(x), H)])
    db = 20 * np.log10(e + 1e-12); quiet = db < thr_db
    cuts = []; i = 0; n = len(quiet)
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]: j += 1
            if (j - i) * 0.01 >= gap and i > 0 and j < n: cuts.append(((i + j) // 2) * H)
            i = j
        else: i += 1
    bounds = [0] + cuts + [len(x)]
    parts = [logits(x[a:b]) for a, b in zip(bounds[:-1], bounds[1:]) if b - a > int(0.05 * sr)]
    return torch.cat(parts, 0) if parts else logits(x)
