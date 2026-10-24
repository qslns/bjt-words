"""두 번째 받아쓰기: ReazonSpeech(일본 방송 3만5천 시간, 단어 단위) → pyopenjtalk로 가나 읽기"""
import numpy as np, sherpa_onnx, pyopenjtalk
from phon import load16
from qa_ctx import CAR
M = '/tmp/claude-0/-home-claude/4ecb1043-4c6e-5d36-a7b6-577be7533edc/scratchpad/reazon/x/sherpa-onnx-zipformer-ja-reazonspeech-2024-08-01/'
rec = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=M + 'encoder-epoch-99-avg-1.int8.onnx', decoder=M + 'decoder-epoch-99-avg-1.int8.onnx',
                                                    joiner=M + 'joiner-epoch-99-avg-1.int8.onnx', tokens=M + 'tokens.txt', num_threads=2, decoding_method='greedy_search')
def text_of(x):
    s = rec.create_stream(); s.accept_waveform(16000, x); rec.decode_stream(s); return s.result.text
def kana_of(t): return pyopenjtalk.g2p(t, kana=True) if t else ''
def in_ctx(fn, car='n', gap=0.15):
    PRE, POST = CAR[car]; z = np.zeros(int(gap * 16000), np.float32)
    x = np.concatenate([np.zeros(8000, np.float32), PRE, z, load16(fn), z, POST, np.zeros(8000, np.float32)])
    t = text_of(x); return t, kana_of(t)
if __name__ == '__main__':
    import sys
    for fn in sys.argv[1:]:
        car = 'k' if fn.endswith(':k') else 'n'; fn = fn.split(':')[0]
        print(fn.split('/')[-1], *in_ctx(fn, car))
