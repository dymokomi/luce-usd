#!/usr/bin/env python3
"""luce-usd's memory-safety gate: the Base module checks (tests/main.lucb)
through the C backend, built with AddressSanitizer and
UndefinedBehaviorSanitizer (no checks disabled), run in a scratch directory
holding the fixtures as the gate does. Any report fails."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--base", type=Path, default=Path(os.environ.get("LUCE_BASE", ROOT.parent / "luce-base/build/luce-base")))
args = parser.parse_args()
runtime = ROOT.parent / "luce-base/runtime"
env = dict(os.environ, LUCE_STD=os.environ.get("LUCE_STD", str(ROOT.parent / "luce-base/src/std")),
           ASAN_OPTIONS="halt_on_error=1:abort_on_error=1:detect_leaks=0",
           UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1")
with tempfile.TemporaryDirectory(prefix="luce-usd-sanitize-") as temporary:
    work = Path(temporary)
    shutil.copytree(ROOT / "tests/fixtures", work / "tests/fixtures")
    env["LUCE_CACHE"] = str(work / "cache")
    source, binary = work / "checks.c", work / "checks"
    print("BUILD tests/main.lucb --emit=c, ASan + UBSan", flush=True)
    subprocess.run([str(args.base.resolve()), "build", str(ROOT / "tests/main.lucb"), "--emit=c", "-o", str(source)],
                   check=True, env=env, timeout=900)
    subprocess.run([os.environ.get("CC", "cc"), "-std=gnu11", "-O1", "-g", "-w", "-fno-strict-aliasing",
                    "-fsanitize=address,undefined", "-fno-sanitize-recover=all", "-fno-omit-frame-pointer",
                    "-I", str(runtime), str(source), str(runtime / "lucb_rt.c"), "-pthread", "-lm", "-o", str(binary)],
                   check=True, timeout=1800)
    print("TEST sanitized checks", flush=True)
    subprocess.run([str(binary)], check=True, env=env, cwd=work, timeout=3000)
print("PASS luce-usd AddressSanitizer + UndefinedBehaviorSanitizer", flush=True)
