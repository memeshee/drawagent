# DrawAgent circuits — canvas wiring recipes (flat NAND only, no sub-circuits on X Layer)

Notation: `N = A NAND B`. Place one NAND gate per line, wire exactly as listed.
XOR block (inputs X,Y → Z, 4 NANDs):
  Na = X NAND Y | Nb = X NAND Na | Nc = Y NAND Na | Z = Nb NAND Nc

## DRAW-8 — 24 NANDs, 8 seed inputs → 3 winner bits
W0 = S0^S3^S6 · W1 = S1^S4^S7 · W2 = (S2^S5)^(S1^S4)
Inputs: S0..S7 (1 bit each). Outputs: W0,W1,W2 (winner = W0 + 2·W1 + 4·W2, picks #0–7).

A = S0^S3:
N1 = S0 NAND S3 · N2 = S0 NAND N1 · N3 = S3 NAND N1 · A = N2 NAND N3
W0 = A^S6:
N5 = A NAND S6 · N6 = A NAND N5 · N7 = S6 NAND N5 · W0 = N6 NAND N7
B = S1^S4:
N9 = S1 NAND S4 · N10 = S1 NAND N9 · N11 = S4 NAND N9 · B = N10 NAND N11
W1 = B^S7:
N13 = B NAND S7 · N14 = B NAND N13 · N15 = S7 NAND N13 · W1 = N14 NAND N15
C = S2^S5:
N17 = S2 NAND S5 · N18 = S2 NAND N17 · N19 = S5 NAND N17 · C = N18 NAND N19
W2 = C^B:
N21 = C NAND B · N22 = C NAND N21 · N23 = B NAND N21 · W2 = N22 NAND N23

## TALLY-3 — full adder, 9 NANDs, 3 vote inputs → 2 count bits
Inputs: V0,V1,V2. Outputs: SUM (count bit 0), COUT (count bit 1). Yes-count = SUM + 2·COUT.
N1 = V0 NAND V1
N2 = V0 NAND N1
N3 = V1 NAND N1
N4 = N2 NAND N3      (= V0^V1)
N5 = N4 NAND V2
N6 = N4 NAND N5
N7 = V2 NAND N5
SUM = N6 NAND N7
COUT = N1 NAND N5

## Tape-out checklist
1. Mint ~60 transistors on the detail page (≈0.04 OKB: 33 for circuits + margin for one retry).
2. Canvas → chain selector → X Layer. Wire DRAW-8, simulate (try S=0x01 → expect W=001), TAPE OUT.
3. Same for TALLY-3 (try V=101 → SUM=0, COUT=1 → count 2).
4. Send the two circuit IDs → demo page config + verification.
