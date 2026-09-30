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
| import: the grid layer as a GeometrySet (faces) | 15 ms | 700,569 |
| export: that GeometrySet as a layer (specs) | 21 ms | 8 |
| export: that layer written as a crate (bytes) | 38 ms | 30,863,460 |
| usdc: write the grid layer (bytes) | 37 ms | 30,863,379 |
| usdz: write the grid layer as a package (bytes) | 56 ms | 30,863,545 |
| usdz: read that package (bytes) | 18.5 ms | 30,863,545 |

The usda grid is the same mesh as a layer: points, face vertex counts and
indices, and a faceVarying `primvars:st`, written with 17-digit doubles for
the uvs (the written layer prints floats in their shorter float form).
Numeric arrays parse and format in parallel chunks on luce-geocore's pool.
The usdc grid is the same layer written as a crate by luce-usd (0.8.0,
integer arrays compressed; OpenUSD's usdcat writes the same layer 3 bytes
longer). Crate arrays decode in parallel, each straight into its column, and
compressible arrays are compressed in parallel before packing (times exclude
file I/O). The import rows turn the read crate
layer into the mesh luced-3d draws (points placed in parallel, faces
checked and wound, normals and quad triangles made in the same passes,
the faceVarying st gathered into `uv`): a whole `Usd.load` of the grid
crate is the read plus the import, 33 ms, against 16 ms for prism. The
export rows write that set back (one Mesh prim sharing the mesh's columns)
and serialize it. The usdz rows hold that crate as the package's root layer: reading
opens the ZIP directory and reads the crate in place; writing is the crate
write plus a CRC-32 and one copy into the stored, 64-byte aligned entry.

## Targets

| Case | .prism (save / load) | .usdc target | .usda target |
|---|---|---|---|
| 700k-face grid (luced-3d case) | 3.8 / 17.0 ms | ≤ 30 / ≤ 25 ms | ≤ 150 / ≤ 120 ms |
| 837×837 grid with corner uv | 7.8 / 18.6 ms | ≤ 40 / ≤ 35 ms | ≤ 250 / ≤ 200 ms |
| camera.step tessellated (707k points, 655k faces, 9 attributes) | 11.8 / 25.5 ms | ≤ 60 / ≤ 60 ms | ≤ 400 / ≤ 350 ms |

Kitchen Set (composed: references, payloads, variants, instancing): `Usd.load`
no slower than OpenUSD's C++ `UsdStage::Open` plus reading every mesh's
points and indices, timed by a local driver; its export as usda under 0.5 s.

Measured on the M-series Mac with the local driver (ourcat --geometry
--timing), Kitchen_set.usd (275,656 faces, 71.5 MB of usda out):

| Phase | Time |
|---|---:|
| compose and flatten the stage | 110 ms |
| import the flattened layer as a GeometrySet | 71 ms |
| export the GeometrySet as a layer | 75 ms |
| write that layer as usda | 161 ms |
| write it as usdc instead | 230 ms |

usdcat --flatten of the same stage takes about 570 ms; ours, usda included, 240 ms.
