# Hidden fixtures (not yet created)

`compute_score.py` expects a `reference.json` in this directory with:

```json
{
  "Cl_ref": <float>,
  "Cd_ref": <float>,
  "cl_tolerance": <float>,
  "cd_tolerance": <float>
}
```

## Why this file does not exist yet

These values must come from a genuinely converged, physically valid
solve of the repaired case — not a guess. As of this writing, no such run
exists: the only completed run of this case (see the repo root's
`results/summary.txt`) has zero boundary-layer cells on the wing, y+
82.6-2089.5, and a pressure residual that never reached the 1e-5 target —
the exact defect this task asks the agent to fix. Its `Cl = -1.69046` is
explicitly documented as not physically valid and must not be used as
`Cl_ref`.

## How to populate it

1. Retune `data/case/system/snappyHexMeshDict`'s layer settings (see
   `instruction.md`) until `snappyHexMesh` reports nonzero boundary-layer
   coverage on the `onera` patch, without loosening `meshQualityControls`.
2. Run `solution/solve.sh` (or the equivalent `SCRIPTS/run_meshing.py` +
   `SCRIPTS/run_analysis.py` pipeline it wraps) to convergence — y+ average
   in range, all four residuals at 1e-5.
3. Take the resulting `Cl`/`Cd` as `Cl_ref`/`Cd_ref`.
4. Set `cl_tolerance`/`cd_tolerance` from genuine solver sensitivity (e.g.
   re-run with one mesh refinement level finer and use the delta), not an
   arbitrary round number — see the Taiga QA guide's "naive guesses clear
   the tolerances" and "knife-edge numerics" pitfalls.
5. Re-run `solution/solve.sh` one more time after fixture generation and
   confirm it scores 1.0 through `compute_score.py` before committing.
