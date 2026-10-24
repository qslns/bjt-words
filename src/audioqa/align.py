"""기대 음소열 E와 들린 음소열 G 정렬(편집 거리 역추적) → 단위(구간)마다 들린 음소"""
def align(E, G):
    n, m = len(E), len(G); D = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): D[i][0] = i
    for j in range(m + 1): D[0][j] = j
    for i in range(1, n + 1):
        Ei = E[i-1]; Di = D[i]; Dp = D[i-1]
        for j in range(1, m + 1):
            Di[j] = min(Dp[j] + 1, Di[j-1] + 1, Dp[j-1] + (Ei != G[j-1]))
    # 역추적: 각 E 위치에 붙는 G 조각(삽입은 앞 E 위치에 붙임)
    i, j = n, m; att = [[] for _ in range(n + 1)]   # att[i]: E[i-1]에 대응하는 G들 (att[0] = 맨 앞 삽입)
    while i > 0 or j > 0:
        if i > 0 and j > 0 and D[i][j] == D[i-1][j-1] + (E[i-1] != G[j-1]):
            att[i].insert(0, G[j-1]); i -= 1; j -= 1
        elif i > 0 and D[i][j] == D[i-1][j] + 1:
            i -= 1
        else:
            att[i].insert(0, G[j-1]); j -= 1
    return D[n][m], att
def heard_spans(E, G, spans):
    """spans: [(a, b)] E 구간 → 각 구간에 들린 G 음소 목록"""
    d, att = align(E, G)
    out = []
    for a, b in spans:
        h = []
        for k in range(a + 1, b + 1): h += att[k]
        if a == 0: h = att[0] + h
        out.append(h)
    return d, out
