#!/usr/bin/env python3
"""
Automated meshing pipeline for the ONERA M6 half-wing case (V2 - relaxed
boundary layers, see system/snappyHexMeshDict header and MESHING_NOTES.md).

Run from the case root with the OpenFOAM environment sourced, e.g.:
    source /usr/lib/openfoam/openfoam2606/etc/bashrc
    python3 run_meshing.py

From Windows PowerShell, invoke it through WSL, e.g.:
    wsl.exe -d Ubuntu -e bash -lc \
        "source /usr/lib/openfoam/openfoam2606/etc/bashrc && \
         cd /mnt/i/Openfoam/OPENFOAM/ONERAV2 && python3 run_meshing.py"

Pipeline: blockMesh -> surfaceFeatureExtract -> snappyHexMesh -> checkMesh -> foamToVTK

See MESHING_NOTES.md for the full parameter derivation. constant/triSurface/
onera.stl is the mm->m scaled, root-aligned, AND surfaceMeshConvert
-clean'd version of the original ONERAM6.STL, carried over from the ONERA
case (not reprocessed here).

KNOWN ISSUE (see MESHING_NOTES.md section 5a): snappyHexMesh has crashed
intermittently on this geometry (a hexRef8 octree-consistency SIGABRT
during castellation). Not reliably fixed by dict tuning or by retrying -
extensive retry testing on the original ONERA case (46+ consecutive
failures in one investigation) showed retrying is NOT a dependable
workaround, so SNAPPY_MAX_ATTEMPTS is kept low here.
"""

import shutil
import subprocess
import sys
from pathlib import Path

CASE_DIR = Path(__file__).resolve().parent

SNAPPY_MAX_ATTEMPTS = 3   # see KNOWN ISSUE above - raising this does not help

STEPS = [
    ("blockMesh",             ["blockMesh"]),
    ("surfaceFeatureExtract", ["surfaceFeatureExtract"]),
    ("snappyHexMesh",         ["snappyHexMesh", "-overwrite"]),
    ("checkMesh",              ["checkMesh"]),
    ("foamToVTK",              ["foamToVTK", "-latestTime"]),
]


def check_environment() -> None:
    missing = [cmd for cmd, _ in STEPS if shutil.which(cmd) is None]
    if missing:
        sys.exit(
            "OpenFOAM tools not found on PATH: "
            + ", ".join(missing)
            + "\nSource the OpenFOAM environment first, e.g.:\n"
            + "    source /usr/lib/openfoam/openfoam2606/etc/bashrc"
        )
    stl = CASE_DIR / "constant" / "triSurface" / "onera.stl"
    if not stl.exists():
        sys.exit(
            f"{stl} not found. See MESHING_NOTES.md - copy the cleaned "
            "onera.stl from the ONERA case's constant/triSurface/ into "
            "this one before running this script."
        )


def run_step(name: str, cmd: list, max_attempts: int = 1) -> None:
    log_file = CASE_DIR / f"log.{name}"
    for attempt in range(1, max_attempts + 1):
        label = f"{name} (attempt {attempt}/{max_attempts})" if max_attempts > 1 else name
        print(f"--> Running {label} ...")
        with open(log_file, "w") as log:
            result = subprocess.run(cmd, cwd=CASE_DIR, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode == 0:
            print(f"    OK - log written to {log_file.name}")
            return
        print(f"    FAILED (exit {result.returncode}) - see {log_file.name}")
    sys.exit(result.returncode)


def main() -> None:
    check_environment()
    for name, cmd in STEPS:
        attempts = SNAPPY_MAX_ATTEMPTS if name == "snappyHexMesh" else 1
        run_step(name, cmd, max_attempts=attempts)
    print("\nMeshing pipeline complete.")
    print("Review the mesh in ParaView via:")
    print(f"  - {CASE_DIR / 'ONERAV2.foam'} (native OpenFOAM reader)")
    print(f"  - {CASE_DIR / 'VTK'} (standalone VTK export)")
    print("Check the actual 'Extruding X out of Y faces' lines in "
          "log.snappyHexMesh (not just the summary table) for the real "
          "boundary-layer coverage achieved - see MESHING_NOTES.md.")


if __name__ == "__main__":
    main()
