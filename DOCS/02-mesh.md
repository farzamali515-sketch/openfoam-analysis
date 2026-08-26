# Mesh — ONERAV2

Source files: `ONERAV2/system/blockMeshDict`, `ONERAV2/system/snappyHexMeshDict`,
`ONERAV2/system/surfaceFeatureExtractDict`, `ONERAV2/MESHING_NOTES.md`

## Domain (background mesh, `blockMeshDict`)

Single hex block, no explicit domain-sizing ratio was given, so these are
documented engineering defaults:

| | |
|---|---|
| Far-field distance | 15c ahead / above / below / spanwise-past-tip; 25c behind the trailing edge (wake room) |
| Background cell size | ~0.95–0.98 m (coarse — snappyHexMesh refinement brings it down near the wing/wake) |
| Background block resolution | 34 × 14 × 25 cells |
| Domain bounding box | X: −12.1 → 21.3, Y: 0 → 13.3, Z: −12.0 → 12.2 (metres) |

### Patches

| Patch | Type | Location |
|---|---|---|
| `inlet` | `patch` | −X face (upstream far-field) |
| `outlet` | `patch` | +X face (downstream far-field / wake exit) |
| `symmetry` | `symmetryPlane` | Y=0 face (wing-root symmetry plane) |
| `farfieldSide` | `patch` | Y=Ymax face (far-field past the wingtip) |
| `farfieldBottom` | `patch` | −Z face |
| `farfieldTop` | `patch` | +Z face |
| `onera` | `wall` | wing surface (from `onera.stl`) |

## Surface refinement (`snappyHexMeshDict`)

| Region | Level | Approx. cell size |
|---|---|---|
| Wing surface (`onera.stl`) | 6–8 (curvature-based) | 15.1 mm .. 3.8 mm |
| Feature edges (LE/TE/tip/root) | 8 | 3.8 mm |
| Near-field box (wing + wake) | 4 | ~60 mm |

`nCellsBetweenLevels = 5`, `resolveFeatureAngle = 30`.

## Mesh quality controls

Tightened beyond the OpenFOAM shipped defaults:

| Parameter | Value |
|---|---|
| `maxNonOrtho` | 50 |
| `maxBoundarySkewness` | 15 |
| `maxInternalSkewness` | 3 |
| `minVolRatio` | 0.02 |

## Boundary layers — ⚠️ known failure

The design intent (documented in `MESHING_NOTES.md`) was a *relaxed* layer
spec, chosen specifically to fit under the tightened quality controls above
after the original `ONERA` case (20 layers, 1.556×10⁻⁶ m first layer,
5 mm target) only achieved 26.7% face coverage:

| | Design target |
|---|---|
| First layer thickness | 2.0×10⁻⁵ m (~y+5) |
| Number of layers | 12 |
| Expansion ratio | 1.25 |
| Resulting total stack (theoretical) | ~1.08×10⁻³ m |

**Actual result (`log.snappyHexMesh`): zero layer cells were added.**
`"Writing 0 faces inside added layer to faceSet layerFaces"` — cell count
before and after the layer-addition stage is identical (907,510 cells).
The wing's near-wall cells are the raw snapped/refined surface cells, not a
prism boundary layer. This is the direct cause of the y+ mismatch reported
in `06-results.md`.

## Final mesh (`checkMesh`)

| Metric | Value |
|---|---|
| Cells | 907,510 |
| Domain bounding box | (−12.1, 0, −12) → (21.3, 13.3, 12.2) |
| Max non-orthogonality | 45.2° (limit 50°) |
| Average non-orthogonality | 6.61° |
| Max skewness | 3.36 (limit — internal 3, boundary 15) |
| Max aspect ratio | 5.11 |
| Result | **Mesh OK** (checkMesh passes cleanly — the zero-layer issue does not register as a checkMesh failure, since it doesn't produce bad cells, only an absent boundary layer) |

## Known intermittent issue

`snappyHexMesh` has crashed intermittently on this case (a `hexRef8`
octree-consistency `SIGABRT` during castellation) — not fixable by tuning
this dict; if it happens, just re-run `run_meshing.py`. See
`../../ONERA/MESHING_NOTES.md` section 5a for the investigation.
