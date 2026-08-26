# Solver Settings — ONERAV2 Analysis

Source files: `ONERAV2/system/controlDict`, `system/fvSchemes`, `system/fvSolution`

## Solver

`simpleFoam` — incompressible, steady-state, SIMPLE/SIMPLEC algorithm.

## `fvSchemes`

```
ddtSchemes      { default steadyState; }
gradSchemes     { default Gauss linear; }
divSchemes
{
    default                         none;
    div(phi,U)                      bounded Gauss linearUpwindV grad(U);
    div(phi,k)                      bounded Gauss upwind;
    div(phi,omega)                  bounded Gauss upwind;
    div((nuEff*dev2(T(grad(U)))))   Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
wallDist        { method meshWave; }
```

## `fvSolution`

```
solvers
{
    p              { solver GAMG; smoother GaussSeidel; tolerance 1e-06; relTol 0.01; }
    "(U|k|omega)"  { solver smoothSolver; smoother GaussSeidel; tolerance 1e-05; relTol 0.1; }
}

SIMPLE
{
    nNonOrthogonalCorrectors 1;
    consistent      yes;              // SIMPLEC
    residualControl { p 1e-5; U 1e-5; k 1e-5; omega 1e-5; }
}

relaxationFactors
{
    fields    { p 0.3; }
    equations { U 0.7; k 0.7; omega 0.7; }
}
```

Conservative (not the higher SIMPLEC-typical relaxation) as a starting
point per `references/solver_control_reference.md`, given the known mesh
quality caveats.

## `controlDict`

| Setting | Value |
|---|---|
| `startTime` / `endTime` | 0 / 2000 (iteration count, `deltaT=1`) |
| `writeControl` / `writeInterval` | `timeStep` / 100 |
| `purgeWrite` | 3 |

### Function objects

**`forceCoeffs1`** — produces `postProcessing/forceCoeffs1/0/coefficient.dat`
(Cd, Cl, CmPitch, ... history):

| Parameter | Value | Note |
|---|---|---|
| `patches` | `(onera)` | wing wall patch |
| `rho` / `rhoInf` | `rhoInf` / 1.281 | only scales the coefficients — the incompressible run itself is density-free |
| `liftDir` | `(0.053382 0 0.998573)` | = +90° from `dragDir` in the X-Z plane |
| `dragDir` | `(0.998573 0 -0.053382)` | = freestream unit direction at AoA=3.06° |
| `pitchAxis` | `(0 1 0)` | spanwise (Y) |
| `CofR` | `(0.203725 0 0.0912)` | approx. quarter-chord, root |
| `magUInf` | 102 | |
| `lRef` | 0.8059 | root chord |
| `Aref` | 0.09290304 | user-given |

**`residuals1`** — `p U k omega` residual history,
`postProcessing/residuals1/0/residuals.dat`.

**`yPlus1`** — writes the `yPlus` field each `writeInterval`, and prints
per-patch min/max/average to the solver log — this is what caught the
boundary-layer/y+ mismatch documented in `06-results.md`.
