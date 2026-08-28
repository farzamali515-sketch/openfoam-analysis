# Solver Settings (current, as shipped in `data/case/system/`)

## Solver

`simpleFoam` — incompressible, steady-state, SIMPLEC. Do not change solver
or turbulence model.

## `fvSchemes` (unchanged, do not modify)

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

## `fvSolution` (unchanged, do not modify) — this is your convergence target

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

`residualControl` above (1e-5 on all four fields) is the convergence bar
your repaired mesh + solve must actually reach — not just approach.

## `controlDict`

| Setting | Value |
|---|---|
| `startTime` / `endTime` | 0 / 2000 (iteration count, `deltaT=1`) |
| `writeControl` / `writeInterval` | `timeStep` / 100 |
| `purgeWrite` | 3 |

### Function objects (already configured — read their output, don't rewrite them)

**`forceCoeffs1`** → `postProcessing/forceCoeffs1/0/coefficient.dat` (Cd,
Cl, CmPitch, ...):

| Parameter | Value |
|---|---|
| `patches` | `(onera)` |
| `rhoInf` | 1.281 |
| `liftDir` | `(0.053382 0 0.998573)` |
| `dragDir` | `(0.998573 0 -0.053382)` |
| `pitchAxis` | `(0 1 0)` |
| `CofR` | `(0.203725 0 0.0912)` |
| `magUInf` | 102 |
| `lRef` | 0.8059 |
| `Aref` | 0.09290304 |

**`residuals1`** → `p U k omega` residual history,
`postProcessing/residuals1/0/residuals.dat`.

**`yPlus1`** → writes the `yPlus` field each `writeInterval`, and prints
per-patch min/max/average to the solver log — use this to check the
boundary-layer/y+ fix.

## What you are expected to change

The layer-addition parameters in `system/snappyHexMeshDict` (first layer
thickness, expansion ratio, number of layers) and, if needed, the
surrounding `addLayersControls` tuning that lets those layers actually be
added without loosening `meshQualityControls`. Everything above this
section is the fixed contract; the layer stack is the thing that's broken.
