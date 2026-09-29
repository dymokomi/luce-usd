# USD and GeometrySet

How `Usd.load` turns a stage into a luce-geocore `GeometrySet`, and how
`Usd.save` writes one back. The code is in `src/luce_usd/convert/`.

## Loading

A GeometrySet holds one component per family, so loading merges prims, as
Houdini's USD Import does:

- every mesh becomes part of one mesh;
- every Points prim becomes part of one point cloud;
- every curves prim becomes part of one curves component;
- every PointInstancer becomes rows of one instances component.

Each face, curve and point keeps its prim's path in the text attribute
`path`, so Blast and the path filters see the hierarchy. Points are placed
by their prims' world transforms, in f64, over the set's origin.

Which prims load:

- defined, active prims only: not `over`s or `class`es;
- not invisible ones;
- purposes `default` and `render`, plus `proxy` and `guide` on request;
- not the prototypes of a point instancer, which are placed by it.

Values are read at the `time` argument. Without one, the layer's
`startTimeCode` is used, else each attribute's first sample. Samples in
between are interpolated linearly.

`Usd.warnings()` lists what a load left out.

### Meshes

- **Winding.** `leftHanded` meshes, and meshes under a mirroring transform,
  have their faces reversed, keeping the first corner.
- **Dropped faces.** Faces with fewer than 3 corners or no area are
  dropped. A face of more than 256 corners skips its prim.
- **Primvars** become attributes by interpolation:

  | USD interpolation | Attribute domain |
  |---|---|
  | vertex, varying | point |
  | faceVarying | corner |
  | uniform | face |
  | constant | detail |

  Indexed primvars are expanded, and `elementSize` multiplies the tuple
  width (at most 4).
- **Names.** `displayColor` becomes `Cd`, `displayOpacity` becomes `Alpha`,
  `st` (or the first texCoord2f primvar) becomes `uv`, and `normals` becomes
  `N`. Other primvars drop the `primvars:` prefix.
- **Constant primvars** are inherited from ancestor prims. When several
  prims merge, one that differs between prims is stored per face.
- **Types.** Floating point becomes f32, and double becomes f64. Integers
  become i32 or i64, and strings and tokens become text.
- **GeomSubsets** become face, point and edge groups named after the
  subset. Subsets with the same name on different prims are merged.
- **Materials.** Each face's bound material path (direct bindings,
  including subsets') goes in the face text attribute `material`.
- **Subdivision.**
  - `subdivisionScheme` becomes `subd.scheme`, shown at level 1.
    Unauthored means Catmull-Clark (USD's default) unless
    `subdivide = false`.
  - `interpolateBoundary` becomes `subd.boundary`.
  - Creases become the edge attribute `crease`, corners become the point
    attribute `corner_sharpness`, and holes become the face group `hole`.
  - The merged mesh holds one scheme: the one most faces ask for.
- **Intrinsic shapes.** Cube, Sphere, Cylinder, Cone, Capsule and Plane
  are tessellated: 24 segments around and 12 along.

### Curves, points and instances

- **BasisCurves.** Linear curves become poly curves.
- **Bezier.** Cubic Bezier curves become Bezier curves with `handle_l` and
  `handle_r`.
- **Bspline.** Cubic B-splines become uniform order-4 NURBS.
- **Catmull-Rom** curves become Catmull-Rom curves. A nonperiodic one drops
  its phantom first and last points.
- **NurbsCurves** keep their order, their knots (narrowed to f32) and their
  weights, as `w`.
- **Periodic curves** become cyclic.
- **Points.** `widths` becomes `width`, and `ids` becomes `id`.
- **PointInstancer.**
  - Each prototype is loaded once as its own set. Its paths are relative
    to the prototype's parent.
  - Each instance is a row: its position, orientation and scale, then the
    instancer's transform. A sheared row takes the nearest rotation and
    scale, with a warning.
  - With `flatten = true`, instances are baked into the other components
    instead.

### Stage metadata

The set's detail attributes record:

- `usd.upAxis`;
- `usd.metersPerUnit`;
- `usd.time`.

`convert_units = true` rotates a Z-up stage to Y-up and scales it to
meters.

## Saving

Elements are grouped by their `path` text into prims at those paths, with
Xform ancestors. Elements without a path go under `/<root>/mesh`,
`/<root>/points`, `/<root>/curves` or `/<root>/instances`. When the whole
mesh is one prim, it keeps its point numbering, and its columns are written
without a copy.

Attributes are written back as primvars:

| Attribute domain | USD interpolation |
|---|---|
| point | vertex |
| corner | faceVarying |
| face | uniform |
| detail | constant |

Other details:

- **Names and types.** `Cd`, `Alpha`, `uv` and `N` get their USD names
  back. Value types come from the scalar type, the width and the role (a
  3-wide float color is `color3f[]`).
- **Unwritten values.** A prim whose share of an attribute is all zero does
  not get that primvar: merging filled zeros there.
- **Groups** become GeomSubsets. `hole` becomes `holeIndices`.
- **Subdivision.** `subdivisionScheme` is always written: absent `subd.*`
  means `none`. Creases are written as two-point chains.
- **Materials.**
  - One material per prim becomes a `material:binding` on the prim.
  - Several materials become `materialBind` subsets, one per material,
    declared `nonOverlapping`.
  - Materials themselves are not written.
- **Curves** go to one prim per kind, open or closed:
  - poly as linear;
  - Bezier as cubic bezier, with the handles between the points;
  - uniform order-4 NURBS as bspline;
  - other NURBS as NurbsCurves, with explicit knots;
  - Catmull-Rom as pinned catmullRom.
- **Instances** become a PointInstancer whose prototypes sit under its
  `Prototypes` scope.
- **Stage metadata.** `upAxis` and `metersPerUnit` come from the set's
  `usd.*` detail, defaulting to Y and 1. The first root prim becomes the
  `defaultPrim`.

## What does not survive a round trip

- **Local transforms.** Points are baked to world space, so the Xforms are
  written as identity.
- **Time samples.** One time is loaded.
- **Attributes on prims that lacked them.** Values filled in by merging
  (zeros) are left out on save, so these stay absent. A constant that
  differed between prims comes back uniform.
- **Subdivision schemes that differ between prims.** The merged mesh holds
  one scheme.
- **Unconverted prims.** Materials, shaders, cameras, lights, skeletons and
  composition arcs are not converted. `Usd.convert` keeps them, since it
  works on layers.
- **Components with no USD form.** CAD, volumes and SDFs are left out.
  Tessellate CAD before saving.
