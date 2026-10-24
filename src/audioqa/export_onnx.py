import torch, numpy as np, time
from transformers import HubertForCTC
M = 'prj-beatrice/japanese-hubert-base-phoneme-ctc-v4'
model = HubertForCTC.from_pretrained(M).eval()
x = torch.randn(1, 16000 * 4)
torch.onnx.export(model, (x,), 'hubert_ctc.onnx', input_names=['input_values'], output_names=['logits'],
                  dynamic_axes={'input_values': {1: 'n'}, 'logits': {1: 't'}}, opset_version=17, dynamo=False)
print('exported')
