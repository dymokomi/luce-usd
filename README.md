# luce-usd

Universal Scene Description for Luce, written in **Luce Base**. luce-usd
reads and writes USD layers (`.usda` text, `.usdc` crate, `.usdz` packages)
and converts composed stages to and from luce-geocore `GeometrySet`s. It is
a gradual rewrite of Pixar's [OpenUSD](https://github.com/PixarAnimationStudios/OpenUSD)
(release v26.08): the modules follow OpenUSD's libraries (Sdf, Pcp, Usd,
UsdGeom) and each names the OpenUSD sources it ports. `docs/PORT.md` tracks
what is ported.

Status: **M3**. The Sdf data model (tokens, paths, values, list ops, layer
data), the usda text format read and written exactly as OpenUSD does, and
usdc crate reading (every crate version, compressed arrays, parallel
decode). Against OpenUSD's own test corpus, 2,019 of 2,056 text layers print
byte-identical to `usdcat`, and every crate reads identically (splines and
array edits are not read yet). Crate writing comes next (docs/PORT.md).

## Exports

- `usd`: the Luce API (`Usd`).
- `usd_kernel`: Base internals for Base code in other packages and for the
  package's checks.

## Tests

`./test.sh` builds `tests/main.lucb` (the Base module checks) at native
optimization levels 0 and 2 and through the C backend, then the Luce API
tests in `tests/api/` natively and through C. CI runs the same on macOS and
Linux against the compilers and packages pinned in `bootstrap/PACKAGES`.
Fixtures in `tests/fixtures/` are our own.

Parity with OpenUSD itself (byte-identical `usdcat` output over OpenUSD's
test corpus, composition baselines) is checked locally, never in CI; see
`docs/PARITY.md`.

`python3 bench/run.py` prints the benchmark table (`docs/BENCHMARKS.md`).

## License

Apache License 2.0 (`LICENSE`). luce-usd is a derivative work of OpenUSD,
which is licensed under the Tomorrow Open Source Technology License 1.0
(`licenses/OPENUSD-TOST-1.0.txt`); see `NOTICE`.
