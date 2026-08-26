# Boundary Conditions — ONERAV2 Analysis

Source files: `ONERAV2/0.orig/U`, `p`, `k`, `omega`, `nut`

Per `references/turbulence_bc_reference.md`, all five outer-domain patches
(`inlet`, `outlet`, `farfieldSide`, `farfieldBottom`, `farfieldTop`) use the
same `freestream*` BC family rather than distinct fixed-inflow /
fixed-outflow types — this handles local in/outflow direction correctly
near domain corners, which matters here because the AoA-tilted velocity
isn't purely aligned with the box axes.

| Patch | U | p | k | omega | nut |
|---|---|---|---|---|---|
| `inlet` | `freestreamVelocity` | `freestreamPressure` | `freestream` | `freestream` | `calculated` |
| `outlet` | `freestreamVelocity` | `freestreamPressure` | `freestream` | `freestream` | `calculated` |
| `farfieldSide` | `freestreamVelocity` | `freestreamPressure` | `freestream` | `freestream` | `calculated` |
| `farfieldBottom` | `freestreamVelocity` | `freestreamPressure` | `freestream` | `freestream` | `calculated` |
| `farfieldTop` | `freestreamVelocity` | `freestreamPressure` | `freestream` | `freestream` | `calculated` |
| `symmetry` | `symmetryPlane` | `symmetryPlane` | `symmetryPlane` | `symmetryPlane` | `symmetryPlane` |
| `onera` (wing wall) | `noSlip` | `zeroGradient` | `kqRWallFunction` | `omegaWallFunction` | `nutkWallFunction` |

**Note on `symmetry` patch type:** the underlying mesh patch is geometrically
typed `symmetryPlane` (not the generic `symmetry`) — the field BC type must
match the geometric patch type or OpenFOAM raises a fatal
"inconsistent patch and patchField types" error. This was hit and fixed
during setup (all fields were initially written with the generic `symmetry`
BC type, which failed against the `symmetryPlane` mesh patch).

## Freestream values used

| Field | `freestreamValue` |
|---|---|
| U | `(101.854 0 -5.445)` m/s |
| p | `0` Pa (gauge) |
| k | `39.015` m²/s² |
| omega | `202.17` 1/s |

## Wall treatment caveat

`kqRWallFunction` / `omegaWallFunction` / `nutkWallFunction` assume a valid
log-law region, i.e. y+ roughly in the 30–300 range. **This mesh's actual
y+ on the wing is 82–2089 (average 456)** because the boundary layer failed
to build (see `02-mesh.md`) — see `06-results.md` for why this invalidates
the near-wall force prediction despite the BC set itself being the correct
standard choice for a properly layered mesh.
