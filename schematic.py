#!/usr/bin/env python3
"""Generate NAND-gate schematics for DrawAgent circuits -> SVG (+PNG via cairosvg/chrome)."""
import math

BG = "#0b0e13"; FG = "#e8edf3"; MUT = "#8b98a9"; GATE_FILL = "#141a23"; GATE_EDGE = "#4a5a70"
GW, GH = 76, 46          # gate box size
ROW = 56                 # row pitch
X_IN = 110
X_COL = lambda d: 300 + (d - 1) * 150
X_OUT = lambda maxd: 300 + maxd * 150 + 60

PALETTE = ["#f472b6", "#60a5fa", "#34d399", "#fbbf24", "#a78bfa", "#f87171", "#22d3ee", "#a3e635"]
INTERNAL = ["#7dd3fc", "#6ee7b7", "#c4b5fd", "#fda4af", "#fcd34d", "#93c5fd"]

def nand_path(x, y):
    # D-shaped NAND: flat left, curved right, output bubble. pins at left (y-11,y+11), out right center
    w, h = GW, GH
    r = h / 2
    body = (f"M{x},{y - r} H{x + w - r} "
            f"A{r},{r} 0 0 1 {x + w - r},{y + r} "
            f"H{x} Z")
    bubble_cx = x + w + 7
    return body, bubble_cx

def schematic(title, subtitle, inputs, gates, outputs, in_rows, fname, width):
    """
    inputs: [names]; gates: list of (name, inA, inB, row, depth); outputs: [(name, src, row)]
    in_rows: {input_name: row}
    """
    maxd = max(d for _, _, _, _, d in gates)
    rows = max([r for _, _, _, r, _ in gates] + [in_rows[i] for i in inputs] + [r for _, _, r in outputs]) + 1
    H = rows * ROW + 130
    W = width or (X_OUT(maxd) + 120)
    y_of = lambda r: 90 + r * ROW + ROW / 2

    # net colors
    color = {}
    for i, n in enumerate(inputs):
        color[n] = PALETTE[i % len(PALETTE)]
    for i, (g, _, _, _, _) in enumerate(gates):
        color[g] = INTERNAL[(i // 4) % len(INTERNAL)]

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
             f'<rect width="{W}" height="{H}" fill="{BG}"/>',
             f'<text x="24" y="40" fill="{FG}" font-size="26" font-family="system-ui" font-weight="700">{title}</text>',
             f'<text x="24" y="66" fill="{MUT}" font-size="14" font-family="system-ui">{subtitle}</text>']

    gate_pos = {}
    # input stubs (labels left of dot, wires exit right)
    for n in inputs:
        y = y_of(in_rows[n])
        parts.append(f'<circle cx="{X_IN - 40}" cy="{y}" r="5" fill="{color[n]}"/>')
        parts.append(f'<text x="{X_IN - 52}" y="{y + 6}" fill="{color[n]}" font-size="17" font-family="monospace" font-weight="700" text-anchor="end">{n}</text>')
        color.setdefault(n, "#fff")

    # gates (labels ABOVE the body, never on pins/wires)
    for (g, a, b, r, d) in gates:
        x = X_COL(d); y = y_of(r)
        body, bcx = nand_path(x, y)
        gate_pos[g] = (x, y, bcx)
        parts.append(f'<path d="{body}" fill="{GATE_FILL}" stroke="{GATE_EDGE}" stroke-width="2"/>')
        parts.append(f'<circle cx="{bcx}" cy="{y}" r="6" fill="{BG}" stroke="{GATE_EDGE}" stroke-width="2"/>')
        parts.append(f'<text x="{x + GW / 2}" y="{y - GH / 2 - 10}" fill="{FG}" font-size="18" font-family="monospace" font-weight="700" text-anchor="middle">{g}</text>')

    def src_point(net):
        if net in gate_pos:
            x, y, bcx = gate_pos[net]
            return bcx + 6, y, color[net]
        return X_IN - 40, y_of(in_rows[net]), color[net]

    # fanout stubs: one stub + junction dot per source net, branches offset so they never share pixels
    edges = []
    for (g, a, b, r, d) in gates:
        x = X_COL(d); y = y_of(r)
        edges.append((a, x, y - 11))
        edges.append((b, x, y + 11))
    from collections import defaultdict
    by_net = defaultdict(list)
    for e in edges:
        by_net[e[0]].append(e)
    branch_start = {}
    for net, lst in by_net.items():
        x1, y1, c = src_point(net)
        sx = x1 + 24
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{sx}" y2="{y1}" stroke="{c}" stroke-width="2.5"/>')
        parts.append(f'<circle cx="{sx}" cy="{y1}" r="4.5" fill="{c}"/ telephone>')
        for i, (n, dx, dy) in enumerate(lst):
            off = (i - (len(lst) - 1) / 2) * 8
            branch_start[(n, dx, dy)] = (sx, y1 + off, c)

    def wire(net, dx, dy_in):
        sx, sy, c = branch_start[(net, dx, dy_in)]
        mx = (sx + dx) / 2
        parts.append(f'<path d="M{sx},{sy} C{mx},{sy} {mx},{dy_in} {dx},{dy_in}" fill="none" stroke="{c}" stroke-width="2.5"/>')

    for (g, a, b, r, d) in gates:
        x = X_COL(d); y = y_of(r)
        wire(a, x, y - 11)
        wire(b, x, y + 11)
        parts.append(f'<circle cx="{x}" cy="{y - 11}" r="3" fill="{FG}"/>')
        parts.append(f'<circle cx="{x}" cy="{y + 11}" r="3" fill="{FG}"/>')

    for (oname, src, r) in outputs:
        x1, y1, c = src_point(src)
        y = y_of(r); xe = X_OUT(maxd)
        mx = (x1 + xe) / 2
        parts.append(f'<path d="M{x1},{y1} C{mx},{y1} {mx},{y} {xe},{y}" fill="none" stroke="{c}" stroke-width="3"/>')
        parts.append(f'<circle cx="{xe + 34}" cy="{y}" r="5" fill="{c}"/>')
        parts.append(f'<text x="{xe + 46}" y="{y + 6}" fill="{c}" font-size="17" font-family="monospace" font-weight="700">{oname}</text>')

    parts.append('</svg>')
    open(fname, "w").write("\n".join(parts))
    print("wrote", fname, f"{W}x{H}")

# ---------------- DRAW-8 ----------------
def xor_block(s, prefix, rows4):
    # returns gates for T = X^Y using names prefix+(1..4)-> (Na,Nb,Nc,T)
    X, Y = s
    Na, Nb, Nc, T = [f"{prefix}{i}" for i in (1, 2, 3, "")] if False else (f"{prefix}a", f"{prefix}b", f"{prefix}c", prefix)
    return [(Na, X, Y), (Nb, X, Na), (Nc, Y, Na), (T, Nb, Nc)]

draw_gates, _r = [], iter(range(24))
spec = [
    # (gate, inA, inB, row, depth)
    ("N1", "S0", "S3", 0, 1), ("N2", "S0", "N1", 1, 2), ("N3", "S3", "N1", 2, 2), ("A", "N2", "N3", 3, 3),
    ("N5", "A", "S6", 4, 4), ("N6", "A", "N5", 5, 5), ("N7", "S6", "N5", 6, 5), ("W0", "N6", "N7", 7, 6),
    ("N9", "S1", "S4", 8, 1), ("N10", "S1", "N9", 9, 2), ("N11", "S4", "N9", 10, 2), ("B", "N10", "N11", 11, 3),
    ("N13", "B", "S7", 12, 4), ("N14", "B", "N13", 13, 5), ("N15", "S7", "N13", 14, 5), ("W1", "N14", "N15", 15, 6),
    ("N17", "S2", "S5", 16, 1), ("N18", "S2", "N17", 17, 2), ("N19", "S5", "N17", 18, 2), ("C", "N18", "N19", 19, 3),
    ("N21", "C", "B", 20, 4), ("N22", "C", "N21", 21, 5), ("N23", "B", "N21", 22, 5), ("W2", "N22", "N23", 23, 6),
]
schematic("DRAW-8 · 24 NANDs", "8 seed bits → 3 winner bits · winner = W0 + 2·W1 + 4·W2 · each gate burns 1 transistor",
          ["S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7"], spec,
          [("W0", "W0", 7), ("W1", "W1", 15), ("W2", "W2", 23)],
          {"S0": 0, "S3": 1, "S6": 4, "S1": 8, "S4": 9, "S7": 12, "S2": 16, "S5": 17},
          "/home/kiter/drawagent-demo/draw8.svg", 1420)

# ---------------- TALLY-3 ----------------
tally = [
    ("N1", "V0", "V1", 0, 1),
    ("N2", "V0", "N1", 1, 2), ("N3", "V1", "N1", 2, 2),
    ("N4", "N2", "N3", 3, 3),
    ("N5", "N4", "V2", 4, 4),
    ("N6", "N4", "N5", 5, 5), ("N7", "V2", "N5", 6, 5),
    ("SUM", "N6", "N7", 7, 6), ("COUT", "N1", "N5", 8, 6),
]
schematic("TALLY-3 · full adder, 9 NANDs", "3 votes → 2 count bits · yes-count = SUM + 2·COUT",
          ["V0", "V1", "V2"], tally,
          [("SUM", "SUM", 7), ("COUT", "COUT", 8)],
          {"V0": 0, "V1": 1, "V2": 5},
          "/home/kiter/drawagent-demo/tally3.svg", 1420)
