# Benchmarks

`python3 bench/run.py` (one `--native --opt 3` build, best of three runs,
Apple M-series). The reference rows time luce-geocore's own `.prism` codec on
the same geometry, so USD rows read as ratios against it.

The geometry: the 837×837 quad grid (702,244 points, 700,569 faces) with a
corner `uv`, as luce-geocore's benchmark saves it.

| Case | Time | Count |
|---|---:|---:|
| Reference: save the grid with uv to .prism (bytes) | 7.8 ms | 84,089,051 |
| Reference: load that .prism (faces) | 18.6 ms | 700,569 |
| Reference: read that file whole (bytes) | 6.1 ms | 84,089,051 |
| usda: read the grid layer (bytes) | 111 ms | 156,993,389 |
| usda: write the grid layer (bytes) | 124 ms | 108,574,613 |
| usdc: read the grid layer (bytes) | 18 ms | 30,863,379 |
| usdc: write the grid layer (bytes) | 37 ms | 30,863,379 |

The usda grid is the same mesh as a layer: points, face vertex counts and
indices, and a faceVarying `primvars:st`, written with 17-digit doubles for
the uvs (the written layer prints floats in their shorter float form).
Numeric arrays parse and format in parallel chunks on luce-geocore's pool.
The usdc grid is the same layer written as a crate by luce-usd (0.8.0,
integer arrays compressed; OpenUSD's usdcat writes the same layer 3 bytes
longer). Crate arrays decode in parallel, each straight into its column, and
compressible arrays are compressed in parallel before packing (times exclude
file I/O).

## Targets

| Case | .prism (save / load) | .usdc target | .usda target |
|---|---|---|---|
| 700k-face grid (luced-3d case) | 3.8 / 17.0 ms | ≤ 30 / ≤ 25 ms | ≤ 150 / ≤ 120 ms |
| 837×837 grid with corner uv | 7.8 / 18.6 ms | ≤ 40 / ≤ 35 ms | ≤ 250 / ≤ 200 ms |
| camera.step tessellated (707k points, 655k faces, 9 attributes) | 11.8 / 25.5 ms | ≤ 60 / ≤ 60 ms | ≤ 400 / ≤ 350 ms |

Kitchen Set (composed: references, payloads, variants, instancing): `Usd.load`
no slower than OpenUSD's C++ `UsdStage::Open` plus reading every mesh's
points and indices, timed by a local driver.
