# Porting OpenUSD

luce-usd rewrites the parts of OpenUSD v26.08 that loading, composing and
saving geometry needs, in Luce Base, module by module. Each Luce module's
header names the OpenUSD sources it follows. This table is the plan and the
record; statuses change as milestones land.

| Milestone | OpenUSD | luce-usd | Status |
|---|---|---|---|
| M0 | `sdf/crateFile.cpp`, `textFileFormat.cpp`, `zipFile.cpp` (signatures) | `sniff.lucb`, `source.lucb` | done |
| M1 | `sdf/path*.cpp`, `pathParser.h`, `tf/token`, `crateDataTypes.h`, `schema.cpp` (type names), `listOp.cpp`, `data.cpp` | `sdf/` | done |
| M2 | `sdf/textFileFormatParser*`, `textParserHelpers.cpp`, `parserHelpers.cpp`, `parserValueContext.cpp`, `fileIO_Common.*`, `usdaFileFormat.cpp`, `schema.cpp` (metadata fields, validators), `tf/stringUtils.cpp` (TfDictionaryLessThan, double text) | `usda/`, `sdf/schema.lucb` | done: 2,017 of 2,056 testenv layers byte-identical to usdcat |
| M3 | `sdf/crateFile.cpp`, `crateData.cpp`, `integerCoding.cpp`, `tf/fastCompression.cpp` (LZ4: luce-compress) | `usdc/` | planned |
| M4 | `sdf/crateFile.cpp` (writing) | `usdc/` | planned |
| M5 | `sdf/zipFile.cpp`, `usdUtils/usdzPackage.cpp` (zip writing: luce-compress) | `usdz/` | planned |
| M6 | `usdGeom/` (xformOp, mesh, subset, curves, points, pointInstancer, primvar), stage metadata | `stage/`, `usd_geom/`, `convert/` | planned |
| M7 | (luced-3d: File rows, Export node) | | planned |
| M8 | `pcp/layerStack.cpp`, `mapFunction.cpp`, `primIndex.cpp` (references, payloads), `ar/` (filesystem, packages) | `pcp/` | planned |
| M9 | `pcp/primIndex.cpp` (variants, inherits, specializes), `instanceKey.cpp`, `usd/stage.cpp`, `usd/resolveInfo`, time samples | `pcp/`, `stage/` | planned |
| M10 | (luced-3d composition rows) | | planned |
| M11 | performance pass (Kitchen Set) | | planned |

## Not ported, and why

| OpenUSD | Why |
|---|---|
| Hydra, usdImaging, Storm | luce-3d is the renderer; GeometrySet is the display path. |
| Plug, schema codegen, file-format plugins | One package, fixed formats; schemas are hand-written tables. Unknown prim types pass through as data. |
| Ar resolvers beyond the filesystem | Anchored, absolute and package-relative paths plus optional search paths only. |
| Python, usdview, Tf notices, change processing, edit targets | Whole layers are loaded and written; a live editable stage is a separate product. |
| Value clips, Ts spline evaluation, UsdSkel, UsdLux, UsdShade networks, MaterialX, UsdPhysics, UsdVol, cameras | Geometry first. Splines and unknown values round-trip as opaque data. |
| Tf, Vt, Gf, Work as libraries | Base, luce-geocore's columns and parallel pool cover them. |

## Parity scores

Measured with the local driver (docs/PARITY.md) against OpenUSD v26.08.

| Suite | Score | Known gaps |
|---|---|---|
| usda (all testenv `.usda` usdcat accepts) | 2,017 / 2,056 byte-identical | attribute splines (`.spline`, Ts) and array edits (`edit [...]`) are refused; path expression values are not re-anchored to their prim |
| sdf-parsing (testSdfParsing) | 69 printed as expected, 113 bad files rejected, 8 differ | the same spline and array-edit files; two baselines made with a test plugin's metadata registered |
