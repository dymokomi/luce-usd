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
| M3 | `sdf/crateFile.cpp` (reading), `crateValueInliners.h`, `integerCoding.cpp`, `tf/fastCompression.cpp` (LZ4: luce-compress `lz4`) | `usdc/reader/`, `usdc/compression.lucb` | done: all 30 testenv `.usdc` and 2,005 of 2,040 usdcat-written crates read byte-identical |
| M4 | `sdf/crateFile.cpp` (packing, _Write, path tree), `crateValueInliners.h` | `usdc/writer/` | done: 2,020 of 2,056 corpus layers written by us read back identically by usdcat |
| M5 | `sdf/zipFile.cpp`, `usdUtils/usdzPackage.cpp` (zip writing: luce-compress) | `usdz/` | done: all 51 testenv packages usdcat opens read identically; 2,020 layers written as usdz read back identically, none failing usdchecker's package validators |
| M6 | `usdGeom/` (xformOp, mesh, subset, curves, points, pointInstancer, primvar, gprims), stage metadata | `stage/`, `usd_geom/`, `convert/` | done: every testenv layer luce-usd reads imports and exports without failing, and usdcat reads every exported layer (2,105 of 2,105) |
| M7 | (luced-3d: File rows, Export node) | luced-3d `usd_nodes.luc` | done: the File node reads USD with its options, the Export node writes USD, OBJ or prism by extension, `luced-3d --import` smoke checks installed builds |
| M8 | `pcp/layerStack.cpp`, `mapFunction.cpp`, `primIndex.cpp` (references, payloads), `ar/` (filesystem, packages), `usd/stage.cpp` (Flatten) | `pcp/`, `flatten/`, `ar.lucb` | done |
| M9 | `pcp/primIndex.cpp` (task queue, variants, inherits, specializes, implied classes), `strengthOrdering.cpp`, `instancing.cpp`, `instanceKey.cpp`, `usd/instanceCache.cpp`, `usd/stage.cpp` (prototypes in Flatten) | `pcp/`, `flatten/instances.lucb` | in progress: Kitchen Set and its instanced version flatten as usdcat does (the instanced one up to usdcat's run-to-run prototype numbering) and import |
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
| usda (all testenv `.usda` usdcat accepts) | 2,019 / 2,056 byte-identical | attribute splines (`.spline`, Ts) and array edits (`edit [...]`) are refused; path expression values are not re-anchored to their prim |
| usdc (testenv `.usdc`) | 30 / 30 byte-identical | |
| usdc-corpus (each testenv `.usda` written as `.usdc` by usdcat) | 2,005 / 2,040 | the same spline files |
| usdc-write (each testenv `.usda` written as `.usdc` by luce-usd, read by usdcat) | 2,020 / 2,056 (layers OpenUSD cannot write as crates either count as agreeing) | splines; path expression anchoring |
| usdz (testenv `.usdz` usdcat opens) | 51 / 51 byte-identical | |
| usdz-write (each testenv `.usda` written as `.usdz` by luce-usd) | 2,020 / 2,056 read back identically; 0 fail usdchecker's RootPackageValidator/UsdzPackageValidator | the usdc-write gaps |
| flatten (each testenv `.usda` and museum root, usdcat --flatten) | 1,831 / 2,078 byte-identical (prototypes numbered as with USD_ASSIGN_PROTOTYPES_DETERMINISTICALLY) | relocates; value clips; splines |
| museum (testPcpMuseum composition results, 151 cases) | 101 / 151 identical to the baselines | relocates (43 cases); expression variables (asset paths, sublayers, variant selections); two `_graph` cases print Pcp's graph dump; BasicInherits and SubrootReferenceAndVariants, whose root layers OpenUSD v26.08 itself refuses to read |
| sdf-parsing (testSdfParsing) | 69 printed as expected, 113 bad files rejected, 8 differ | the same spline and array-edit files; two baselines made with a test plugin's metadata registered |
