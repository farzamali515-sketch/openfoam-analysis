# Geometry — ONERA M6 Half-Wing

Source file: `ONERAV2/constant/triSurface/onera.stl` (also `ONERAV2.foam` case root)

## Model

- Half-wing (symmetry plane at the root, modelled from `Y = 0` outward) — the
  mesh and all results represent **one wing**, not a full aircraft/full span.
- Geometry is axis-aligned in the mesh: **no angle of attack is baked into
  the STL or the mesh**. AoA is applied later, purely as the solved-flow
  velocity direction (see `03-flow-conditions.md`).

## Axis convention

| Axis | Meaning |
|---|---|
| X | Chordwise (streamwise) |
| Y | Spanwise (`Y = 0` is the wing root / symmetry plane) |
| Z | Up / thickness direction |

## Bounding box (metres, from `surfaceCheck`/mesh notes)

| Axis | Min | Max | Extent |
|---|---|---|---|
| X (chordwise) | 0.00225 | 1.14882 | 1.14657 |
| Y (spanwise)  | 0       | 1.21838 | 1.21838 (half-span) |
| Z (thickness) | 0.05178 | 0.130625 | 0.07885 |

## Reference dimensions used in the analysis

| Quantity | Value | Used for |
|---|---|---|
| Root chord, `c` | 0.8059 m | `lRef` in `forceCoeffs` (moment coefficient scale) |
| Reference area, `Aref` | 0.09290304 m² | **User-given.** Used directly as the force-coefficient reference area. Assumed to already correspond to the half-wing modelled here (not doubled for a full/mirrored wing) — flag if that assumption is wrong. |

Note: the X-extent (1.14657 m) is larger than the root chord (0.8059 m)
because the wing is swept/tapered — the tip trailing edge sits further aft
in X than the root trailing edge, widening the chordwise bounding box beyond
any single station's chord length.
