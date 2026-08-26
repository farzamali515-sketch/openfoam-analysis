# ONERA M6 Wing Analysis — Documentation

Documentation of the data used in the `ONERAV2` steady RANS analysis
(mesh: `../../ONERAV2/`).

| File | Covers |
|---|---|
| [01-geometry.md](01-geometry.md) | Wing model, axis convention, bounding box, reference dimensions |
| [02-mesh.md](02-mesh.md) | Domain/background mesh, surface refinement, mesh quality, boundary-layer setup and its known failure |
| [03-flow-conditions.md](03-flow-conditions.md) | User-given and assumed flow conditions, regime, turbulence quantities |
| [04-boundary-conditions.md](04-boundary-conditions.md) | Per-patch BC set for U, p, k, omega, nut |
| [05-solver-settings.md](05-solver-settings.md) | fvSchemes, fvSolution, controlDict, function objects |
| [06-results.md](06-results.md) | Cl/Cd/CmPitch, convergence, and why this run's numbers should not be trusted yet |

Each file states plainly which values came from the user, which were
assumed (and why), and which were computed — see the "Assumed / derived"
sections in `03-flow-conditions.md` and `06-results.md` in particular.

**Bottom line:** the case is fully set up and runs cleanly, but the
underlying mesh has no boundary layer on the wing (see `02-mesh.md`), so
the Cl/Cd in `06-results.md` are not yet trustworthy — treat this as a
verified case setup with a pending mesh fix, not a finished result.
