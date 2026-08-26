#!/usr/bin/env python3
"""
Automated steady-state CFD analysis pipeline for the ONERA M6 half-wing
case (ONERAV2 mesh).

Requires the mesh to already exist (see run_meshing.py). Runs, in order:
    initialise 0/ from 0.orig -> simpleFoam -> foamToVTK -> plot_results.py
    -> results summary

Usage (from an environment with OpenFOAM sourced, e.g. inside WSL):
    source /usr/lib/openfoam/openfoam2606/etc/bashrc
    cd /path/to/ONERAV2
    python3 run_analysis.py

From Windows PowerShell, invoke it through WSL, e.g.:
    wsl.exe -d Ubuntu -e bash -lc \
        "source /usr/lib/openfoam/openfoam2606/etc/bashrc && \
         cd /mnt/i/Openfoam/OPENFOAM/ONERAV2 && python3 run_analysis.py"

Every run starts fresh from 0.orig (controlDict has startFrom/startTime = 0),
so re-running the script reproduces the same result. Iteration count/write
frequency are controlled by system/controlDict, not by this script.

Solver/BC setup: simpleFoam (incompressible, SIMPLEC), kOmegaSST, freestream
farfield BCs, AoA = 3.06 deg applied via the inlet velocity direction (see
0.orig/U header comment) - this AoA was ASSUMED (not given by the user),
carried over from this mesh's own documented default in MESHING_NOTES.md.

KNOWN ISSUE (see results/summary.txt for full detail): this mesh has zero
boundary-layer cells on the wing (snappyHexMesh added none despite the
meshing notes describing an intended stack), so y+ on "onera" lands at
~80-2000 - well outside the wall-function-valid range. Cl/Cd from this run
should be treated as a diagnostic check of the setup, NOT a trustworthy
result, until the mesh is rebuilt with working layers. This script does not
fix that; it reports it (see the yPlus check below and the WARNING it
prints if y+ is out of range).

Results are stored in results/:
    summary.json          - Cd/Cl/CmPitch, forces, y+ stats, final residuals,
                             machine-readable
    summary.txt            - same, human-readable, with the validity caveats
    residuals.png, force_coeffs.png, *.csv - from scripts/plot_results.py
    postProcessing/         - copy of the full force/coefficient/yPlus history
    log.simpleFoam          - copy of the solver log

Each pipeline step's raw stdout/stderr also stays in the case root as
log.<step>, and the solved fields are exported to VTK/ for ParaView review.
"""

import glob
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

CASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = CASE_DIR / "results"
PLOT_SCRIPT = CASE_DIR.parent / "scripts" / "plot_results.py"

SOLVER = "simpleFoam"
REQUIRED_TOOLS = [SOLVER, "foamToVTK"]

FIELDS = ["U", "p", "k", "omega", "nut"]

RESIDUAL_FIELDS = ["Ux", "Uy", "Uz", "p", "k", "omega"]

# Wall-function validity range used only to print a warning - not enforced.
YPLUS_WARN_BELOW = 30
YPLUS_WARN_ABOVE = 300

# Rough physical sanity check on Cl (thin-airfoil estimate for this case's
# AoA, ~2*pi*alpha) - only used to print a warning, never to block the run.
CL_SANITY_RANGE = (-0.5, 1.5)


def check_environment() -> None:
    missing = [cmd for cmd in REQUIRED_TOOLS if shutil.which(cmd) is None]
    if missing:
        sys.exit(
            "OpenFOAM tools not found on PATH: "
            + ", ".join(missing)
            + "\nSource the OpenFOAM environment first, e.g.:\n"
            + "    source /usr/lib/openfoam/openfoam2606/etc/bashrc"
        )
    if not (CASE_DIR / "constant" / "polyMesh").exists():
        sys.exit("No mesh found in constant/polyMesh - run run_meshing.py first.")
    if not (CASE_DIR / "0.orig").exists():
        sys.exit("No 0.orig found - nothing to initialise 0/ from.")


def initialise_fields() -> None:
    print("--> Initialising 0/ from 0.orig ...")
    (CASE_DIR / "0").mkdir(exist_ok=True)
    for field in FIELDS:
        src = CASE_DIR / "0.orig" / field
        if src.exists():
            shutil.copy(src, CASE_DIR / "0" / field)


def run_step(name: str, cmd: list) -> None:
    log_file = CASE_DIR / f"log.{name}"
    print(f"--> Running {name} ...")
    start = time.time()
    with open(log_file, "w") as log:
        result = subprocess.run(cmd, cwd=CASE_DIR, stdout=log, stderr=subprocess.STDOUT)
    elapsed = time.time() - start
    if result.returncode != 0:
        print(f"    FAILED (exit {result.returncode}, {elapsed:.0f}s) - see {log_file.name}")
        sys.exit(result.returncode)
    print(f"    OK ({elapsed:.0f}s) - log written to {log_file.name}")


def latest_row(pattern: str):
    """Read every postProcessing/<func>/<time>/<pattern> file and return the
    data row with the largest Time column (handles files split across restarts)."""
    rows = {}
    for path in glob.glob(str(CASE_DIR / "postProcessing" / "*" / "*" / pattern)):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                try:
                    t = float(parts[0])
                except ValueError:
                    continue
                rows[t] = parts
    return rows[max(rows)] if rows else None


def last_residual(field: str):
    log_file = CASE_DIR / f"log.{SOLVER}"
    if not log_file.exists():
        return None
    marker = f"Solving for {field}, Initial residual ="
    value = None
    with open(log_file) as f:
        for line in f:
            if marker in line:
                try:
                    value = float(line.split("Initial residual =")[1].split(",")[0])
                except (IndexError, ValueError):
                    pass
    return value


def last_yplus():
    """Parse the last 'patch onera y+ : min = .. max = .. average = ..' line."""
    log_file = CASE_DIR / f"log.{SOLVER}"
    if not log_file.exists():
        return None
    pattern = re.compile(
        r"patch onera y\+ : min = ([\d.eE+-]+), max = ([\d.eE+-]+), average = ([\d.eE+-]+)"
    )
    result = None
    with open(log_file) as f:
        for line in f:
            m = pattern.search(line)
            if m:
                result = {
                    "min": float(m.group(1)),
                    "max": float(m.group(2)),
                    "average": float(m.group(3)),
                }
    return result


def run_plots() -> None:
    if not PLOT_SCRIPT.exists():
        print(f"--> Skipping plots - {PLOT_SCRIPT} not found")
        return
    coeff_files = sorted(glob.glob(str(CASE_DIR / "postProcessing" / "forceCoeffs*" / "*" / "coefficient*.dat")))
    if not coeff_files:
        print("--> Skipping plots - no coefficient.dat found")
        return
    print("--> Running plot_results.py ...")
    cmd = [
        sys.executable, str(PLOT_SCRIPT),
        "--log", str(CASE_DIR / f"log.{SOLVER}"),
        "--forces", coeff_files[-1],
        "--out-dir", str(RESULTS_DIR),
        "--avg-window", "200",
    ]
    result = subprocess.run(cmd, cwd=CASE_DIR)
    if result.returncode != 0:
        print("    plot_results.py failed (non-fatal) - continuing")


def write_results() -> None:
    print("--> Collecting results ...")
    RESULTS_DIR.mkdir(exist_ok=True)

    coeff_row = latest_row("coefficient*.dat")
    force_row = latest_row("force*.dat")
    yplus = last_yplus()

    summary = {
        "solver": SOLVER,
        "turbulenceModel": "kOmegaSST",
        "conditions": {
            "U_inf_mps": 102,
            "AoA_deg": 3.06,
            "rho_kgm3": 1.281,
            "p_Pa": 101325,
            "nu_m2s": 1.4207e-05,
        },
        "reference": {"lRef_m": 0.8059, "Aref_m2": 0.09290304},
        "final_residuals": {f: last_residual(f) for f in RESIDUAL_FIELDS},
        "yPlus_onera": yplus,
    }

    if coeff_row:
        header = ["Time", "Cd", "Cd_f", "Cd_r", "Cl", "Cl_f", "Cl_r",
                  "CmPitch", "CmRoll", "CmYaw", "Cs", "Cs_f", "Cs_r"]
        summary["forceCoefficients"] = dict(zip(header, map(float, coeff_row)))

    if force_row:
        header = ["Time",
                   "Ftotal_x", "Ftotal_y", "Ftotal_z",
                   "Fpressure_x", "Fpressure_y", "Fpressure_z",
                   "Fviscous_x", "Fviscous_y", "Fviscous_z"]
        summary["forces_N"] = dict(zip(header, map(float, force_row)))

    warnings = []
    if yplus and (yplus["average"] < YPLUS_WARN_BELOW or yplus["average"] > YPLUS_WARN_ABOVE):
        warnings.append(
            f"y+ average {yplus['average']:.1f} is outside the "
            f"{YPLUS_WARN_BELOW}-{YPLUS_WARN_ABOVE} wall-function range - "
            "results are not trustworthy (see MESHING_NOTES.md / boundary layer)."
        )
    if coeff_row:
        cl = float(coeff_row[4])
        if not (CL_SANITY_RANGE[0] <= cl <= CL_SANITY_RANGE[1]):
            warnings.append(
                f"Cl = {cl:.3f} is outside the rough sanity range "
                f"{CL_SANITY_RANGE} for this AoA - treat as suspect."
            )
    summary["warnings"] = warnings

    with open(RESULTS_DIR / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    lines = ["ONERA M6 half-wing (ONERAV2) - steady RANS results summary", "=" * 60, ""]
    if coeff_row:
        lines.append(f"Cl = {float(coeff_row[4]):.4f}")
        lines.append(f"Cd = {float(coeff_row[1]):.4f}")
        if float(coeff_row[1]) != 0:
            lines.append(f"L/D = {float(coeff_row[4]) / float(coeff_row[1]):.3f}")
        lines.append(f"CmPitch = {float(coeff_row[7]):.4f}")
    if yplus:
        lines.append("")
        lines.append(f"y+ (onera): min={yplus['min']:.1f} max={yplus['max']:.1f} "
                      f"average={yplus['average']:.1f}")
    lines.append("")
    lines.append("Final initial residuals:")
    for field, val in summary["final_residuals"].items():
        if val is not None:
            lines.append(f"  {field:6s}: {val:.3e}")
    if warnings:
        lines.append("")
        lines.append("WARNINGS:")
        for w in warnings:
            lines.append(f"  - {w}")
    lines.append("")
    lines.append(f"Full history: results/postProcessing/, fields: VTK/, {CASE_DIR.name}.foam")

    with open(RESULTS_DIR / "summary.txt", "w") as f:
        f.write("\n".join(lines) + "\n")

    # Archive the raw force/coefficient/yPlus history and the solver log
    pp_dst = RESULTS_DIR / "postProcessing"
    if pp_dst.exists():
        shutil.rmtree(pp_dst)
    shutil.copytree(CASE_DIR / "postProcessing", pp_dst)
    log_src = CASE_DIR / f"log.{SOLVER}"
    if log_src.exists():
        shutil.copy(log_src, RESULTS_DIR / f"log.{SOLVER}")

    print(f"    Results written to {RESULTS_DIR}")
    print("\n".join(lines))


def main() -> None:
    check_environment()
    initialise_fields()
    run_step(SOLVER, [SOLVER])
    run_step("foamToVTK", ["foamToVTK", "-latestTime"])
    run_plots()
    write_results()


if __name__ == "__main__":
    main()
