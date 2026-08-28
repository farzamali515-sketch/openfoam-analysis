# ONERA M6 Wing — Boundary-Layer Mesh Repair & Force Coefficients

## Objective

You are given a steady RANS CFD case for the ONERA M6 half-wing that runs
end-to-end but produces an untrustworthy result: the wall-adjacent mesh has
no boundary layer, so the wall-function boundary conditions are being
evaluated far outside their valid range. Your job is to repair the mesh so
it actually resolves a boundary layer consistent with the case's boundary
conditions, re-run the solve to convergence, and report the resulting force
coefficients.

This is a mesh-quality and convergence problem, not a from-scratch case
setup: the geometry, flow conditions, and boundary condition *types* are
already correct and must not change. What's broken is purely the near-wall
mesh resolution.

## Public inputs (`data/`)

- `data/case/constant/` — mesh (`polyMesh/`), wing surface
  (`triSurface/onera.stl`), `transportProperties`, `turbulenceProperties`
- `data/case/system/` — current `blockMeshDict`, `snappyHexMeshDict`,
  `surfaceFeatureExtractDict`, `fvSchemes`, `fvSolution`, `controlDict`
- `data/case/0.orig/` — initial/boundary fields: `U`, `p`, `k`, `omega`, `nut`
- `data/geometry.md` — half-wing geometry, axis convention, reference
  dimensions (`lRef`, `Aref`)
- `data/flow_conditions.md` — freestream conditions, turbulence quantities,
  flow regime
- `data/boundary_conditions.md` — per-patch BC set for `U`, `p`, `k`,
  `omega`, `nut`
- `data/solver_settings.md` — current `fvSchemes`/`fvSolution`/`controlDict`
  and the exact convergence target already declared in `residualControl`

## The known defect

`snappyHexMesh`, as currently configured in `data/case/system/snappyHexMeshDict`,
adds **zero boundary-layer cells** on the `onera` (wing) patch — confirmed by
"Writing 0 faces inside added layer" in the meshing log. Consequences:

- Wing-surface y+ lands at roughly 80–2000 (average ~450), far outside the
  30–300 range the declared `kqRWallFunction`/`omegaWallFunction`/
  `nutkWallFunction` boundary conditions assume.
- The pressure residual plateaus around 1e-4 and never reaches the 1e-5
  target already declared in `system/fvSolution`'s `residualControl` — the
  solve exhausts its iteration budget instead of converging.
- Resulting force coefficients are not physically defensible for this
  geometry and angle of attack.

You need to retune the layer-addition settings (and/or the surrounding
`meshQualityControls`) so the boundary layer actually forms, without
relaxing the mesh quality thresholds already in place, then re-run the
solve.

## Deliverable

Write a single JSON file to `/tmp/output/force_coefficients.json` with
exactly these keys:

```json
{
  "Cl": <float>,
  "Cd": <float>,
  "CmPitch": <float>,
  "yPlus_min": <float>,
  "yPlus_max": <float>,
  "yPlus_average": <float>,
  "residual_p_final": <float>,
  "residual_U_final": <float>,
  "residual_k_final": <float>,
  "residual_omega_final": <float>
}
```

`Cl`, `Cd`, `CmPitch` come from the `forceCoeffs` function object already
configured in `system/controlDict` (patch `onera`, `liftDir`/`dragDir` at
the case's angle of attack, `lRef`/`Aref` as documented in
`data/geometry.md`). `yPlus_*` come from the `yPlus` function object's
per-patch min/max/average on `onera`. Residuals are the final initial
residuals for `p`, `Ux` (or `U` magnitude), `k`, and `omega`.

## Constraints

- Do not change the geometry, freestream conditions, angle of attack,
  turbulence model, or boundary condition *types* documented in
  `data/flow_conditions.md` and `data/boundary_conditions.md`.
- Do not relax the mesh quality thresholds already set in
  `meshQualityControls` (`maxNonOrtho`, `maxBoundarySkewness`,
  `maxInternalSkewness`, `minVolRatio`) to force layer addition through —
  the fix must come from the layer-growth parameters (first layer
  thickness, expansion ratio, layer count) being consistent with the
  quality constraints, not from loosening the constraints.
- Either target is acceptable: a wall-function-consistent y+ (30–300 average
  on `onera`), or a fully resolved near-wall mesh (y+ ≲ 5) — but if you
  choose the resolved route, you must also switch the wall boundary
  conditions to a low-Re-capable set and say so in your reasoning; do not
  report y+ ≲ 5 while leaving wall-function BCs in place.
- The solve must reach the 1e-5 residual target already declared in
  `system/fvSolution`'s `residualControl`, within the iteration budget in
  `system/controlDict`. Do not raise the iteration budget as a substitute
  for fixing convergence.

## Completion rule

Submit only after the mesh shows nonzero boundary-layer face coverage on
`onera` in the meshing log, y+ falls in a range consistent with the wall
treatment you're using, and all four residuals (`p`, `U`, `k`, `omega`)
reach 1e-5. A run that hits the iteration cap without meeting
`residualControl` is not yet done.
