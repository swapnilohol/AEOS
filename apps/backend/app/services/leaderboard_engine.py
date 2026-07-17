from dataclasses import dataclass


@dataclass
class BestProblemScore:
    problem_id: str
    best_final_score: float
    difficulty_multiplier: float


def compute_weighted_total(best_scores: list[BestProblemScore]) -> float:
    """A student's leaderboard total: their best final_score per problem,
    each scaled by that problem's difficulty_multiplier, summed. This is
    where difficulty weighting applies — never at the per-submission level
    (see scoring_engine.py's docstring)."""
    return round(sum(s.best_final_score * s.difficulty_multiplier for s in best_scores), 2)


def rank_totals(user_totals: list[tuple[str, float]]) -> dict[str, int]:
    """Assigns 1-based ranks by total score, descending. Ties are broken by
    user_id ordering (a documented simplification — not by earliest
    achievement time) since the target is 10 concurrent students, not a
    tie-sensitive competition ladder."""
    ordered = sorted(user_totals, key=lambda item: (-item[1], item[0]))
    return {user_id: rank for rank, (user_id, _total) in enumerate(ordered, start=1)}
