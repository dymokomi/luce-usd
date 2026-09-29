#!/usr/bin/env python3
"""luce-usd's benchmark: builds bench/main.lucb with --native --opt 3, runs
it and prints a Markdown table (case, milliseconds, count). Pass --runs N to
keep each case's best of N runs."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile


def grid_usda(path, n):
    """The n x n quad grid (geocore's verb benchmark grid) as a usda Mesh with
    a faceVarying st, written as usdcat would print it."""
    def number(value):
        text = repr(float(value))
        return text[:-2] if text.endswith(".0") else text
    with open(path, "w") as out:
        out.write('#usda 1.0\n(\n    defaultPrim = "grid"\n    metersPerUnit = 1\n    upAxis = "Y"\n)\n\n')
        out.write('def Mesh "grid"\n{\n')
        out.write("    int[] faceVertexCounts = [" + ", ".join(["4"] * (n * n)) + "]\n")
        corners = []
        for z in range(n):
            for x in range(n):
                a = z * (n + 1) + x
                corners += [a, a + n + 1, a + n + 2, a + 1]
        out.write("    int[] faceVertexIndices = [" + ", ".join(map(str, corners)) + "]\n")
        points = []
        for z in range(n + 1):
            for x in range(n + 1):
                points.append(f"({number(x - n * 0.5)}, 0, {number(z - n * 0.5)})")
        out.write("    point3f[] points = [" + ", ".join(points) + "]\n")
        uv = []
        for z in range(n):
            for x in range(n):
                for (cx, cz) in ((x, z), (x, z + 1), (x + 1, z + 1), (x + 1, z)):
                    uv.append(f"({number(cx / n)}, {number(cz / n)})")
        out.write("    texCoord2f[] primvars:st = [" + ", ".join(uv) + "] (\n        interpolation = \"faceVarying\"\n    )\n")
        out.write('    uniform token subdivisionScheme = "none"\n}\n\n')

ROOT = Path(__file__).resolve().parents[1]
EXE = ".exe" if os.name == "nt" else ""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=Path(os.environ.get("LUCE_BASE", ROOT.parent / f"luce-base/build/luce-base{EXE}")))
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="luce-usd-bench-") as temporary:
        binary = Path(temporary) / f"bench{EXE}"
        env = dict(os.environ, LUCE_CACHE=str(Path(temporary) / "cache"))
        subprocess.run([str(args.base.resolve()), "build", str(ROOT / "bench/main.lucb"), "--native", "--opt", "3", "-o", str(binary)],
                       check=True, env=env, timeout=900)
        grid = Path(temporary) / "grid.usda"
        grid_usda(grid, 837)
        best = {}
        order = []
        for _ in range(args.runs):
            output = subprocess.run([str(binary), str(grid)], check=True, capture_output=True, text=True, timeout=900).stdout
            for line in output.splitlines():
                name, milliseconds, count = line.split("\t")[:3]
                if name not in best:
                    order.append(name)
                    best[name] = (float(milliseconds), count)
                elif float(milliseconds) < best[name][0]:
                    best[name] = (float(milliseconds), count)
    print("| Case | Time | Count |\n|---|---:|---:|")
    for name in order:
        milliseconds, count = best[name]
        print(f"| {name} | {milliseconds:.1f} ms | {int(count):,} |")


if __name__ == "__main__":
    main()
