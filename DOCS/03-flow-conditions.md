# Flow Conditions — ONERAV2 Analysis

Source files: `ONERAV2/constant/transportProperties`,
`ONERAV2/constant/turbulenceProperties`, `ONERAV2/0.orig/*`

## User-given conditions

| Quantity | Value | Source |
|---|---|---|
| Freestream velocity, `U∞` | 102 m/s | user-given |
| Static pressure, `p` | 101325 Pa | user-given |
| Density, `ρ` | 1.281 kg/m³ | user-given |
| Reference area, `Aref` | 0.09290304 m² | user-given |

## Assumed / derived values (not given by the user — flag if wrong)

| Quantity | Value | Basis |
|---|---|---|
| Angle of attack, AoA | 3.06° | Not specified by the user. Carried over from this mesh's own documented default (`MESHING_NOTES.md` / `blockMeshDict` header — "standard M6 case" AoA). **Confirm if a different AoA (or zero-lift case) was intended.** |
| Dynamic viscosity, `μ` | 1.82×10⁻⁵ Pa·s | Standard air value, same as used elsewhere in this project (Cylinder case). Not given by the user. |
| Kinematic viscosity, `ν` | `μ/ρ` = 1.4207×10⁻⁵ m²/s | Derived from the two rows above |
| Implied temperature, `T` | 275.6 K | Ideal-gas check only: `T = p/(R_specific·ρ)`, `R_specific = 287.058 J/(kg·K)` — reference, not used directly (solver is incompressible) |
| Turbulence intensity, `I` | 5% | Project default (`references/turbulence_bc_reference.md`) — not given by the user |
| Turbulence length scale, `l` | 7% of chord = 0.056413 m | Project default convention for external aero |

## Regime

- Mach number: `M = U∞ / a`, `a = sqrt(1.4 × 287.058 × 275.6) = 332.8 m/s` → **M ≈ 0.307**
- Treated as **subsonic incompressible** (`simpleFoam`), per this project's
  default (`SKILL.md`: "Default flow regime is subsonic incompressible...").
  M≈0.3 is a borderline call — a different session's `Cylinder`/`CylinderV2`
  case at a similar Mach number instead used a compressible solver
  (`rhoSimpleFoam`); this case followed the skill's stated default instead,
  for consistency with the detailed BC/solver reference material it provides
  for `simpleFoam`.
- Reynolds number (chord-based): `Re_c = U∞·c/ν = 102 × 0.8059 / 1.4207e-05`
  **≈ 5.786 × 10⁶** — fully turbulent.

## Turbulence quantities (freestream)

```
k     = 1.5 × (I × U∞)²             = 1.5 × (0.05 × 102)²      = 39.015 m²/s²
omega = sqrt(k) / (Cmu^0.25 × l)     Cmu = 0.09
      = sqrt(39.015) / (0.5477 × 0.056413) = 202.17 1/s
nut (initial guess) = k / omega     ≈ 0.19298 m²/s
```

## Turbulence model

`kOmegaSST` (RAS), `constant/turbulenceProperties` — this project's default
for external aerodynamics (good near-wall + freestream behaviour, industry
standard for airfoil/wing RANS work).

## Freestream velocity vector (AoA applied here, geometry stays axis-aligned)

Chord along +X, up along +Z. Positive AoA is applied by tilting the
*velocity* vector (not the geometry) so the relative wind approaches the
fixed wing from slightly above-forward:

```
Ux = U∞ · cos(AoA) =  101.854 m/s
Uz = -U∞ · sin(AoA) = -5.445 m/s
U  = (101.854, 0, -5.445) m/s
```
