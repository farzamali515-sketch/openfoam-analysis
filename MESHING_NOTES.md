# ONERA M6 half-wing - V2 case notes

This case is a variant of `../ONERA/` (same geometry, domain, and surface
refinement) with **relaxed boundary layers**. See `../ONERA/MESHING_NOTES.md`
for everything not repeated below: geometry cleanup, reference flow
values, domain/background sizing, surface refinement strategy, and the
known intermittent snappyHexMesh crash issue (section 5a there).

## What's different from ONERA

The original ONERA case used a user-specified layer stack (first layer
1.556e-06 m, expansionRatio 1.4367 derived, 20 layers, 0.005 m total)
together with tightened `meshQualityControls`. That combination only
achieved 26.7% face coverage / 18.7% of the target thickness (see
`../ONERA/MESHING_NOTES.md` section 5b) - too aggressive a layer growth
for the tightened quality to accept.

Per instruction, **quality stays tightened** (unchanged from ONERA:
`maxNonOrtho 50`, `maxBoundarySkewness 15`, `maxInternalSkewness 3`,
`minVolRatio 0.02`) and **the layers are relaxed instead**:

| | ONERA | ONERA V2 |
|---|---|---|
| First layer thickness | 1.556e-06 m | **2.0e-05 m** (~13x bigger) |
| Number of layers | 20 | **12** |
| Expansion ratio | 1.4367 (derived) | **1.25** |
| Resulting total thickness | 0.005 m (target) | **~1.08e-03 m** (consequence, not chosen directly) |

The 2.0e-05 m first cell corresponds to roughly y+~5 (vs. the sub-y+1
target implied by 1.556e-06 m), using the same flat-plate Cf estimate as
`../ONERA/MESHING_NOTES.md` section 5 (Re_c=5.535e6, u_tau=3.6766 m/s at
U=102 m/s/M=0.3, rho=1.225 kg/m3, p=101325 Pa). expansionRatio 1.25 is
near-standard practice, versus the earlier ~44%-per-layer growth.

**The resulting ~1.08 mm total stack is well short of the original 5 mm
target** - this is the direct, expected cost of relaxing the layers
instead of the quality. If that's too thin, the alternative (relax
quality, keep the original 5 mm/20-layer/1.556 micron spec) is still on
the table - ask to revisit it.

## Running it

Same as ONERA:
```bash
source /usr/lib/openfoam/openfoam2606/etc/bashrc
cd /path/to/ONERAV2
python3 run_meshing.py
```

## Reviewing in ParaView

- `ONERAV2.foam` - native OpenFOAM reader.
- `VTK/` - standalone export, written by the `foamToVTK` step.
