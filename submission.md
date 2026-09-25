# DrawAgent — hackathon submission pack (TapeOut Genesis Transistor Hackathon)

## Form fields
- **Processor contract address:** 0x93778d6D5a8372690564fED126ea8d0604929C7F (X Layer, chain 196)
- **Deployment wallet:** 0x4ba1e9e275ef61b56c99532d0066506436201d73
- **Transistors (ERC-1155):** 0x204466D4B547494A2e402647Ec8d473d4947DbBa
- **Product demo:** https://drawagent-demo.vercel.app
- **OKX.AI agent:** DrawAgent, ID 13908 (ASP, X Layer)

## Project description (paste-ready)
DrawAgent is a trustless draw service: raffles for 8 entrants and 3-ballot votes
executed by real on-chain circuits on X Layer, served by OKX.AI agent #13908.
Every result is a permanent on-chain function anyone can call for free
(eval circuit #2 for draws, #1 for tallies) and verify with one read call.
Each execution burns the processor's transistors, tying demand to real usage;
escrow settles each agent job on delivery.

## Asset issuance (publicly disclosed at deployment)
- Total transistors: 1,000,000 · mint price 0.00066 OKB · creation fee 0.0066 OKB
- Burned so far: 78 (DRAW-8 #2) + 31 (TALLY-3 #1) = 109 transistors of real usage
- Revenue: mint income withdrawable by creator on the processor detail page

## Circuits
- #1 TALLY-3 — full adder, 3 vote bits → 2 count bits. Verified: eval(1,0x05)=0x02
- #2 DRAW-8 — XOR-fold, 8 seed bits → 3 winner bits. Verified: eval(2,0x80)=0x02, eval(2,0x01)=0x01

## Verification (all free read calls, https://rpc.xlayer.tech)
- eval(uint256,bytes) selector 0x934d06ea on the processor address, I/O bits little-endian
- Processor page: https://www.tapeout.net/#l2/xlayer/0x93778d6D5a8372690564fED126ea8d0604929C7F

## Status / pending
- [x] IGNIX token live: https://ignix.bot/launch?token=0x40068a2987d9bB411e88b79731a9659eab18EEeE (`0x40068a2987d9bB411e88b79731a9659eab18EEeE`)
- [ ] Pilot draw with a real community (evidence: tx + video)
- [ ] 2-min demo video (live draw → on-chain verify)
- [ ] Submit form before 2026-10-06 11:00 (UTC+07:00)
