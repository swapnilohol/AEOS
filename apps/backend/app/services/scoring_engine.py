"""
Scoring Calculation Engine.

Pure functions only (no DB, no I/O) so they're trivially unit-testable.
Documents the Final Score Formula, since the source prompt's own formula
section was cut off mid-sentence in the uploaded file — this is this
module's own design filling that gap, not a transcription of a missing spec.

Final Score Formula (per submission, bounded to [0, problem.max_score]):

    final_score = functional_score * performance_factor * penalty_factor

Where:
- functional_score: weighted pass-ratio already computed by the Execution
  Engine (sum of passed test weights / sum of all test weights * max_score).
  Already in [0, max_score] by construction.
- performance_factor: in [1 - performance_max_penalty_ratio, 1.0]. No
  penalty if average execution time of passed tests is at or under the
  target; scales down linearly beyond that, capped at the configured max
  penalty. This is a bounded heuristic, not a precise metric.
- penalty_factor: 1.0 normally; (1 - late_penalty_ratio) if the submission
  was made after the hackathon's end_time.

Since both factors are <= 1.0 and functional_score <= max_score, the
product never needs clamping upward — only rounding.

difficulty_multiplier is intentionally NOT part of this per-submission
formula. It only scales how a problem's best score contributes to a
student's aggregate leaderboard total, so a single submission's score
never exceeds its own problem's max_score. See leaderboard_engine.py.

quality_score is an optional, currently-unpopulated field (static code
quality analysis is out of scope for this MVP) — always None for now.
"""


def compute_performance_factor(
    avg_execution_time_ms: float | None,
    *,
    target_ms: int,
    max_penalty_ratio: float,
) -> float:
    if avg_execution_time_ms is None or avg_execution_time_ms <= target_ms or target_ms <= 0:
        return 1.0

    excess_ratio = min(1.0, (avg_execution_time_ms - target_ms) / target_ms)
    return round(1.0 - (max_penalty_ratio * excess_ratio), 4)


def compute_penalty_factor(is_late: bool, *, late_penalty_ratio: float) -> float:
    return round(1.0 - late_penalty_ratio, 4) if is_late else 1.0


def compute_final_score(
    functional_score: float,
    *,
    performance_factor: float,
    penalty_factor: float,
    max_score: float,
) -> float:
    final_score = functional_score * performance_factor * penalty_factor
    return round(max(0.0, min(final_score, max_score)), 2)
