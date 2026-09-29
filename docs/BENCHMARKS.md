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

## Targets

| Case | .prism (save / load) | .usdc target | .usda target |
|---|---|---|---|
| 700k-face grid (luced-3d case) | 3.8 / 17.0 ms | ≤ 30 / ≤ 25 ms | ≤ 150 / ≤ 120 ms |
| 837×837 grid with corner uv | 7.8 / 18.6 ms | ≤ 40 / ≤ 35 ms | ≤ 250 / ≤ 200 ms |
| camera.step tessellated (707k points, 655k faces, 9 attributes) | 11.8 / 25.5 ms | ≤ 60 / ≤ 60 ms | ≤ 400 / ≤ 350 ms |

Kitchen Set (composed: references, payloads, variants, instancing): `Usd.load`
no slower than OpenUSD's C++ `UsdStage::Open` plus reading every mesh's
points and indices, timed by a local driver.
