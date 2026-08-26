# Results — ONERAV2 Analysis

Source files: `ONERAV2/results/summary.txt`, `results/summary.json`,
`results/force_coeffs.csv`, `results/residuals.csv`, `results/*.png`,
`ONERAV2/log.simpleFoam`

## Headline numbers (2000 iterations)

| Quantity | Value |
|---|---|
| Cl | **−1.6905** |
| Cd | **0.1063** |
| L/D | −15.90 |
| CmPitch | 0.5936 |

## ⚠️ Validity — do not treat these as physically trustworthy

Two independent red flags on this run:

**1. y+ on the wing surface: min 82.6, max 2089.5, average 456.**
Far outside both the resolved-sublayer range (~1) and the standard
wall-function range (~30–300) that this case's BC set (`kqRWallFunction` /
`omegaWallFunction` / `nutkWallFunction`) assumes. Root cause: `snappyHexMesh`
added **zero** boundary-layer cells on this mesh (see `02-mesh.md`) — the
near-wall cells are the raw background/refinement hex cells, roughly two
orders of magnitude too coarse for 102 m/s flow.

**2. Cl = −1.69 is not physically plausible** for a 3.06° AoA wing.
Thin-airfoil theory gives Cl ≈ 2π·α(rad) ≈ 0.34 for the 2D section; a finite
swept wing would reduce that further, not flip its sign or exceed −1. A wall
function evaluated where no log-law region exists produces unreliable
near-wall pressure/shear, which is what's showing up here.

## Convergence

| Field | Final "initial residual" reported in `log.simpleFoam` |
|---|---|
| Ux | 1.040×10⁻⁵ |
| Uy | 1.128×10⁻⁵ |
| Uz | 9.289×10⁻⁶ |
| k | 9.393×10⁻⁶ |
| omega | 9.897×10⁻⁶ |
| p (second/inner solve, last logged) | 1.395×10⁻⁶ |
| **p (first/controlling solve — what `residualControl` checks)** | **~1.0–1.5×10⁻⁴, plateaued** |

U, k, and omega essentially met the 1×10⁻⁵ `residualControl` target. The
**controlling p residual did not** — it plateaued around 1–1.5×10⁻⁴ for the
last several hundred iterations rather than continuing to drop, so the run
used its full 2000-iteration budget instead of stopping early. This is
consistent with (not fully independent of) the near-wall breakdown above
feeding noise into the pressure correction.

## Assumptions this result depends on

- **AoA = 3.06°** — not given by the user; carried over from this mesh's
  documented default (`03-flow-conditions.md`). If a different AoA was
  intended, both Cl and Cd change.
- **μ = 1.82×10⁻⁵ Pa·s** (air) — not given; only ρ was specified.
- **Aref = 0.09290304 m²** applied directly as the half-wing reference area
  (not doubled) — confirm this matches how the number was derived.

## Recommendation

Rebuild the mesh so `snappyHexMesh` actually adds boundary-layer cells (the
`meshQualityControls`/layer settings that produced the zero-coverage result
need retuning — same failure mode seen on the `CylinderV2` case elsewhere in
this project), re-target y+ into the wall-function range (or resolve it with
y+~1 and switch to a low-Re-capable BC set), then re-run. Until then, treat
this Cl/Cd pair as a **diagnostic check of the setup**, not a design number.

## Where to look

- `results/residuals.png`, `results/force_coeffs.png` — convergence plots
- `results/*.csv` — tabular residual/coefficient history
- `VTK/ONERAV2_2000/` — solved flow field for ParaView review
- `ONERAV2.foam` — native OpenFOAM reader entry point
