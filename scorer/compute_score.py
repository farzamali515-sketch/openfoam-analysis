"""
RubricTask grader for onera-m6-boundary-layer-repair.

Criteria
--------
yplus_valid   Wing-surface y+ average lands in a range consistent with the
              declared wall treatment: 30-300 for the wall-function BC set
              already in data/boundary_conditions.md, or <=5 if the agent
              switched to a low-Re-capable BC set (self-declared, not
              re-verified here - a from-scratch BC-type check would need
              the agent to submit its modified 0/ files, which this task's
              artifact schema does not currently require).
convergence   p/U/k/omega residuals all reached the 1e-5 target already
              declared in data/case/system/fvSolution's residualControl.
cl_accuracy   Submitted Cl within tolerance of the hidden reference.
cd_accuracy   Submitted Cd within tolerance of the hidden reference.

Import note: `grading.evaluation` is the shared package from the LBx
Prometheus template fork. This file will not import standalone in this
repository - port it into the fork once available (see repo root
README/DOCS for context on this gap).

TODO before this task can validate or run ground-truth: scorer/data/reference.json
does not exist yet. It must be generated FROM A GENUINE CONVERGED RUN, not
guessed - see scorer/data/README.md and solution/solve.sh's authoring-time
caveat for why no such run exists yet (the boundary-layer defect is still
unresolved as of this file being written).
"""

from grading.evaluation import (
    JsonArtifact,
    RubricCriterion,
    RubricTask,
    TrustedJson,
)

YPLUS_WALL_FUNCTION_RANGE = (30.0, 300.0)
YPLUS_RESOLVED_MAX = 5.0
RESIDUAL_TARGET = 1e-5


def evaluate(context):
    design = context.candidate
    reference = context.fixtures["reference"]

    yplus_avg = design.get("yPlus_average")
    low, high = YPLUS_WALL_FUNCTION_RANGE
    yplus_ok = yplus_avg is not None and (
        low <= yplus_avg <= high or yplus_avg <= YPLUS_RESOLVED_MAX
    )

    residual_fields = (
        "residual_p_final",
        "residual_U_final",
        "residual_k_final",
        "residual_omega_final",
    )
    residuals = [design.get(f) for f in residual_fields]
    converged = all(r is not None and r <= RESIDUAL_TARGET for r in residuals)

    cl_tol = reference["cl_tolerance"]
    cd_tol = reference["cd_tolerance"]
    cl_submitted = design.get("Cl")
    cd_submitted = design.get("Cd")
    cl_err = abs(cl_submitted - reference["Cl_ref"]) if cl_submitted is not None else float("inf")
    cd_err = abs(cd_submitted - reference["Cd_ref"]) if cd_submitted is not None else float("inf")

    return {
        "yplus_valid": 1.0 if yplus_ok else 0.0,
        "convergence": 1.0 if converged else 0.0,
        "cl_accuracy": max(0.0, 1.0 - cl_err / cl_tol) if cl_tol else 0.0,
        "cd_accuracy": max(0.0, 1.0 - cd_err / cd_tol) if cd_tol else 0.0,
    }


TASK = RubricTask(
    artifact=JsonArtifact(
        "force_coefficients.json",
        required_keys=(
            "Cl",
            "Cd",
            "CmPitch",
            "yPlus_min",
            "yPlus_max",
            "yPlus_average",
            "residual_p_final",
            "residual_U_final",
            "residual_k_final",
            "residual_omega_final",
        ),
    ),
    criteria=(
        RubricCriterion(
            "yplus_valid",
            weight=0.25,
            description="Wing-surface y+ is in a range valid for the declared wall treatment",
            required=True,
        ),
        RubricCriterion(
            "convergence",
            weight=0.25,
            description="p/U/k/omega residuals reached the declared 1e-5 target",
            required=True,
        ),
        RubricCriterion(
            "cl_accuracy",
            weight=0.30,
            description="Cl within tolerance of the reference solution",
            required=True,
        ),
        RubricCriterion(
            "cd_accuracy",
            weight=0.20,
            description="Cd within tolerance of the reference solution",
            required=True,
        ),
    ),
    evaluate=evaluate,
    fixtures=(TrustedJson("reference", "reference.json"),),
)
