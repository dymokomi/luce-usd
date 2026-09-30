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
| M9 | `pcp/primIndex.cpp` (task queue, variants, inherits, specializes, implied classes, relocations), `strengthOrdering.cpp`, `layerStack.cpp` (relocations, expression variables), `instancing.cpp`, `instanceKey.cpp`, `expressionVariables.cpp`, `sdf/variableExpression*.cpp`, `usd/instanceCache.cpp`, `usd/primDefinition.cpp`, `usd/stage.cpp` (prototypes and built-in properties in Flatten) | `pcp/`, `flatten/`, `sdf/expressions.lucb`, `prim_definitions.lucb`, `schema_table.lucb` | done: 147 of 151 museum cases compose as OpenUSD's baselines; Kitchen Set flattens byte-identical to usdcat (its instanced version up to usdcat's run-to-run prototype numbering) and loads in about 0.2 s, instances as instances; value clips are left for later |
| M10 | `usd/variantSets.cpp` (GetNames, GetVariantNames, SetVariantSelection in the session layer), `usd/stage.cpp` (load rules) | `pcp/session.lucb`, `pcp/summary.lucb`, `Usd.load(variants, payloads)`, `Usd.composition` | done: the luced-3d File node shows the stage (layers, prims, instances), menus for its first variant sets, a variant selections text and payload globs |
| M11 | performance pass (Kitchen Set) | | done: compose and flatten 150 to 110 ms; export 6.2 s to 75 ms (edge attributes' marked edges found once, not per prim); usda writing 556 to 160 ms (every mid-sized array formatted together on the pool) |

## Not ported, and why

| OpenUSD | Why |
|---|---|
| Hydra, usdImaging, Storm | luce-3d is the renderer; GeometrySet is the display path. |
| Plug, schema codegen, file-format plugins | One package, fixed formats; schemas are hand-written tables. Unknown prim types pass through as data. |
| Ar resolvers beyond the filesystem | Anchored, absolute and package-relative paths plus optional search paths only. |
| Python, usdview, Tf notices, change processing, edit targets | Whole layers are loaded and written; a live editable stage is a separate product. |
| `matches_regex` in variable expressions | No regular expression engine in luce-usd; the function fails, so an expression using it gives nothing. |
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
| flatten (each testenv `.usda` and museum root, usdcat --flatten) | 1,952 / 2,078 byte-identical (prototypes numbered as with USD_ASSIGN_PROTOTYPES_DETERMINISTICALLY) | value clips; splines; path expressions mapped into prototypes |
| museum (testPcpMuseum composition results, 151 cases) | 147 / 151 identical to the baselines | two `_graph` cases print Pcp's graph dump; BasicInherits and SubrootReferenceAndVariants, whose root layers OpenUSD v26.08 itself refuses to read |
| sdf-parsing (testSdfParsing) | 69 printed as expected, 113 bad files rejected, 8 differ | the same spline and array-edit files; two baselines made with a test plugin's metadata registered |
