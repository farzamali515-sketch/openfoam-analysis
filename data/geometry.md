# Geometry — ONERA M6 Half-Wing

Source file: `data/case/constant/triSurface/onera.stl`

## Model

- Half-wing (symmetry plane at the root, modelled from `Y = 0` outward) —
  the mesh and all results represent **one wing**, not a full aircraft.
- Geometry is axis-aligned in the mesh: no angle of attack is baked into
  the STL or the mesh. AoA is applied via the solved-flow velocity
  direction (see `flow_conditions.md`).

## Axis convention

| Axis | Meaning |
|---|---|
| X | Chordwise (streamwise) |
| Y | Spanwise (`Y = 0` is the wing root / symmetry plane) |
| Z | Up / thickness direction |

## Bounding box (metres)

| Axis | Min | Max | Extent |
|---|---|---|---|
| X (chordwise) | 0.00225 | 1.14882 | 1.14657 |
| Y (spanwise)  | 0       | 1.21838 | 1.21838 (half-span) |
| Z (thickness) | 0.05178 | 0.130625 | 0.07885 |

## Reference dimensions

| Quantity | Value | Used for |
|---|---|---|
| Root chord, `lRef` | 0.8059 m | `forceCoeffs` moment-coefficient scale |
| Reference area, `Aref` | 0.09290304 m² | Force-coefficient reference area, already corresponding to this half-wing (not doubled for a mirrored full wing) |

The X-extent (1.14657 m) exceeds the root chord (0.8059 m) because the wing
is swept/tapered — the tip trailing edge sits further aft in X than the root
trailing edge.
