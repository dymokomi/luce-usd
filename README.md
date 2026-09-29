# luce-usd

Universal Scene Description for Luce, written in **Luce Base**. luce-usd
reads and writes USD layers (`.usda` text, `.usdc` crate, `.usdz` packages)
and converts composed stages to and from luce-geocore `GeometrySet`s. It is
a gradual rewrite of Pixar's [OpenUSD](https://github.com/PixarAnimationStudios/OpenUSD)
(release v26.08): the modules follow OpenUSD's libraries (Sdf, Pcp, Usd,
UsdGeom) and each names the OpenUSD sources it ports. `docs/PORT.md` tracks
what is ported.

Status: **M6**. The Sdf data model; usda, usdc and usdz read and written
as OpenUSD does them (against OpenUSD's own test corpus, 2,019 of 2,056
text layers print byte-identical to `usdcat`, every crate and package reads
identically, and 2,020 layers written as crates read back identically;
splines and array edits are the gap); and a single-layer stage converted to
and from luce-geocore `GeometrySet`s (docs/MAPPING.md). Composition
(references, payloads, variants, inherits, native instancing) comes next
(docs/PORT.md).

## Luce API

```
from usd import Usd

let geometry = Usd.load("chair.usdc")           # a GeometrySet
let later = Usd.load("chair.usdc", time = 24.0, flatten = true, convert_units = true)
print(Usd.warnings())                           # what the last load left out
Usd.save(geometry, "out.usdz", root = "geo")    # .usda, .usdc, .usd or .usdz
Usd.convert("in.usda", "out.usdc")              # layer to layer, nothing lost
print(Usd.info("chair.usdc"))                   # format, units, prims by type
```

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
