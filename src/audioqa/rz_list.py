"""예문 파일 몇 개를 ReazonSpeech로 받아쓰기 (usage: python3 rz_list.py 2281-1 2314-1 ...)"""
import sys, numpy as np
from reazon import text_of
from phon import load16
for k in sys.argv[1:]:
    x = load16(f'/home/claude/bjt-words/audio/s/{k}.mp3')
    print(k, text_of(np.concatenate([np.zeros(8000, np.float32), x, np.zeros(8000, np.float32)])), flush=True)
