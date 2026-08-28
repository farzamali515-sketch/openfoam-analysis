# Boundary Conditions

Source files: `data/case/0.orig/U`, `p`, `k`, `omega`, `nut`

All five outer-domain patches (`inlet`, `outlet`, `farfieldSide`,
`farfieldBottom`, `farfieldTop`) use the `freestream*` BC family rather than
distinct fixed-inflow/fixed-outflow types — this handles local in/outflow
direction correctly near domain corners, which matters here because the
AoA-tilted velocity isn't purely aligned with the box axes.

| Patch | U | p | k | omega | nut |
|---|---|---|---|---|---|
| `inlet` | `freestreamVelocity` | `freestreamPressure` | `freestream` | `freestream` | `calculated` |
| `outlet` | `freestreamVelocity` | `freestreamPressure` | `freestream` | `freestream` | `calculated` |
| `farfieldSide` | `freestreamVelocity` | `freestreamPressure` | `freestream` | `freestream` | `calculated` |
| `farfieldBottom` | `freestreamVelocity` | `freestreamPressure` | `freestream` | `freestream` | `calculated` |
| `farfieldTop` | `freestreamVelocity` | `freestreamPressure` | `freestream` | `freestream` | `calculated` |
| `symmetry` | `symmetryPlane` | `symmetryPlane` | `symmetryPlane` | `symmetryPlane` | `symmetryPlane` |
| `onera` (wing wall) | `noSlip` | `zeroGradient` | `kqRWallFunction` | `omegaWallFunction` | `nutkWallFunction` |

## Freestream values used

| Field | `freestreamValue` |
|---|---|
| U | `(101.854 0 -5.445)` m/s |
| p | `0` Pa (gauge) |
| k | `39.015` m²/s² |
| omega | `202.17` 1/s |

## Wall treatment — this is what the mesh must satisfy

`kqRWallFunction`/`omegaWallFunction`/`nutkWallFunction` assume a valid
log-law region, i.e. wing-surface y+ roughly in the **30–300** range. The
BC set itself is the correct standard choice for a properly layered mesh —
the problem is purely that the current mesh doesn't deliver a y+ in that
range (see `instruction.md` for the specific defect). Do not change these
BC types unless you deliberately switch to a low-Re-capable set for a
fully resolved (y+ ≲ 5) approach, and say so.
