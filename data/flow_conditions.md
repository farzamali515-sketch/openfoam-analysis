# Flow Conditions

Source files: `data/case/constant/transportProperties`,
`data/case/constant/turbulenceProperties`, `data/case/0.orig/*`

## Freestream conditions

| Quantity | Value |
|---|---|
| Freestream velocity, `U∞` | 102 m/s |
| Angle of attack, AoA | 3.06° |
| Static pressure, `p` | 101325 Pa |
| Density, `ρ` | 1.281 kg/m³ |
| Dynamic viscosity, `μ` | 1.82×10⁻⁵ Pa·s |
| Kinematic viscosity, `ν` | 1.4207×10⁻⁵ m²/s |

## Regime

- Mach number ≈ 0.307 — treated as subsonic incompressible (`simpleFoam`).
- Reynolds number (chord-based): `Re_c = U∞·lRef/ν ≈ 5.786 × 10⁶` — fully
  turbulent.

## Turbulence quantities (freestream)

```
Turbulence intensity, I = 5%
Turbulence length scale, l = 7% of chord = 0.056413 m
k     = 1.5 × (I × U∞)²             = 39.015 m²/s²
omega = sqrt(k) / (Cmu^0.25 × l)     = 202.17 1/s      (Cmu = 0.09)
nut (initial guess) = k / omega     ≈ 0.19298 m²/s
```

Turbulence model: `kOmegaSST` (RAS) — do not change this.

## Freestream velocity vector

Chord along +X, up along +Z. AoA is applied by tilting the *velocity*
vector, not the geometry:

```
Ux = U∞ · cos(AoA) =  101.854 m/s
Uz = -U∞ · sin(AoA) = -5.445 m/s
U  = (101.854, 0, -5.445) m/s
```

This vector, along with `p`, `k`, and `omega` freestream values, is already
set in `data/case/0.orig/`. Do not change these.
