# Parity with OpenUSD (local only)

luce-usd is checked against OpenUSD v26.08 itself: its `usdcat` and
`usdchecker`, run over OpenUSD's own test corpus. The OpenUSD build and the
comparison driver are comparison tools, so they live outside the repo, in
`~/Dev/luce_dev/.donors/` beside the donor checkout. CI never runs them.

## Setup

```sh
cd ~/Dev/luce_dev/.donors
git clone https://github.com/PixarAnimationStudios/OpenUSD.git && git -C OpenUSD checkout v26.08
oracles/luce-usd/build.sh     # C++ tools only: no Python, imaging or plugins (~10 min)
```

`build.sh` runs OpenUSD's `build_scripts/build_usd.py` with Python, imaging,
usdview and every optional plugin off, and installs to `.donors/OpenUSD-install`
(`bin/usdcat`, `usdchecker`, `usdzip`, `sdfdump`).

## Running

```sh
python3 ~/Dev/luce_dev/.donors/oracles/luce-usd/parity.py [suite ...]
```

| Suite | Checks |
|---|---|
| `sdf-parsing` | `sdf/testenv/testSdfParsing.testenv` (192 files): good files print as their baselines, bad files fail |
| `usda` | every testenv `.usda` (2,271): ours, parsed and written, byte-identical to `usdcat` |
| `usdc` | every testenv `.usdc` (38): ours read and printed as usda, identical to `usdcat` |
| `usdc-corpus` | every testenv `.usda` written as `.usdc` by `usdcat`: ours reads it identically |
| `usdc-write` | every testenv `.usda` written as `.usdc` by us, read back by `usdcat` identically |
| `usdz` | every testenv `.usdz`: ours reads the root layer and prints it identically to `usdcat` |
| `usdz-write` | every testenv `.usda` written as a `.usdz` by us: read back by `usdcat` identically, and `usdchecker`'s package validators (stored, 64-byte aligned) pass |
| `museum` | the 141 `testPcpMuseum_*` cases: our composition report equals `compositionResults_*.txt`, and our flatten equals `usdcat --flatten` |

`geometry_sweep.py` (next to the driver) imports every testenv layer as a
GeometrySet and exports it back through `ourcat --geometry`; nothing may
crash, and `usdcat` must read every exported layer.

The driver builds nothing in the repo: it runs `ourcat`, a small Base program
next to it (`.donors/oracles/luce-usd/ourcat/`) that prints a layer through
luce-usd as usda, and compares it with `usdcat`. usdcat's results are cached.
Scores go into `docs/PORT.md` when a milestone lands.
