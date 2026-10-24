"""새 예문(new_*.tsv: bn, scene, jp{target}+漢字[よみ], ko) → 루비·TTS. 주석 표시는 숫자와 섞이지 않게 사설 문자로."""
import sys, re, json, glob
sys.path.insert(0, '/home/claude/work/pipeline')
import build as B
L = json.load(open('/home/claude/work/basic/list.json', encoding='utf-8'))
H = json.load(open('/home/claude/work/basic/headinfo.json', encoding='utf-8'))
card = {o['bn']: o for o in L}
MK = re.compile('(\\d+)')
ANN2 = re.compile(r'([0-9０-９]*[㐀-鿿々]+)\[([ぁ-ゖー]+)\]')
TTS_KANA_B = {'一日', '表', '日', '頃', '代', '階', '方', '上', '下', '中', '後', '間', '分', '空く', '開く', '辛い', '人気', '昨夜', 'この間', 'お宅',
              '一昨日', '明後日', '再来月', '箱', '外国人', '時々', 'この頃', '角', '訳', '下手', '上手', '家', '港'}   # 10/14 검수: 음성 엔진이 다르게 읽을 수 있는 표제어
COUNTER_HEAD = set('日月年時分秒人名件個回円部社割枚階倍週台本冊度位歳号番期点泊席杯箱軒店便通万億代周着棟戸組')
def plain_so_far(m): return re.sub(r'[{}]', '', re.sub(r'\[([^|\]]+)\|[^\]]*\]', r'\1', m))
def proc(jp, head, hr):
    forced = []
    def sub(m):
        forced.append((m.group(1), m.group(2))); return '%d' % (len(forced) - 1)
    s = ANN2.sub(sub, jp)
    markup = tts = ''; rev = []
    for ch in re.split(r'(\{[^{}]*\})', s):
        if not ch: continue
        is_t = ch.startswith('{'); body = ch[1:-1] if is_t else ch
        seg = ''
        for k, pc in enumerate(MK.split(body)):
            if not pc: continue
            if k % 2 == 1:
                base, yomi = forced[int(pc)]
                seg += ''.join(f'[{t}|{r}]' if r else t for t, r in B.align(base, yomi)); tts += yomi; rev.append((base, yomi, 'ANN')); continue
            if is_t and pc == head and B.has_kanji(head):
                seg += ''.join(f'[{t}|{r}]' if r else t for t, r in B.align(head, hr))
                tts += hr if (head in B.TTS_KANA or head in TTS_KANA_B) else pc; rev.append((pc, hr, 'HEAD')); continue
            for surf, rd, lem in B.tokenize_plain(pc):
                if rd and B.has_kanji(surf) and re.search('[0-9０-９]$', plain_so_far(markup + seg)) and surf[0] in COUNTER_HEAD:
                    seg += surf; tts += surf; continue   # 숫자 뒤 조수사는 루비 없이(1500 카드와 같게, 연탁·촉음 오류 방지)
                if rd and B.has_kanji(surf):
                    seg += ''.join(f'[{t}|{r}]' if r else t for t, r in B.align(surf, rd)); rev.append((surf, rd, lem))
                    tts += rd if surf in B.TTS_KANA else surf
                else:
                    seg += surf; tts += surf
        markup += ('{' + seg + '}') if is_t else seg
    return markup, tts, rev
if __name__ == '__main__':
    out = {}
    for p in sorted(glob.glob('/home/claude/work/basic/new_*.tsv')):
        for ln in open(p, encoding='utf-8'):
            if not ln.strip() or ln.startswith('#'): continue
            f = ln.rstrip('\n').split('\t')
            assert len(f) == 4, (p, ln)
            bn, sc, jp, ko = int(f[0]), f[1], f[2], f[3]
            assert sc in B.__dict__.get('SC', {'mtg','notice','talk','tel','news','mail','graph','biz','report','visit','doc'}), (bn, sc)
            assert jp.count('{') == 1 and jp.count('}') == 1, (bn, jp)
            o = card[bn]; head = o['w'].replace('〜', ''); hr = o['r'].replace('〜', '')
            j, t, rev = proc(jp, head, hr)
            out.setdefault(str(bn), []).append({'s': sc, 'j': j, 'k': ko, 't': t, 'src': p.rsplit('/', 1)[1]})
    json.dump(out, open('/home/claude/work/basic/new_proc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    a, b = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, 99999)
    for bn in sorted(out, key=int):
        if not (a <= int(bn) <= b): continue
        for e in out[bn]: print(f"#{bn} {card[int(bn)]['w']} | {e['j']} | {e['t']}")
    print('cards', len(out), 'sentences', sum(len(v) for v in out.values()), file=sys.stderr)
