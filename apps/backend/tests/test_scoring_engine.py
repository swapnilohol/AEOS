from app.services.leaderboard_engine import BestProblemScore, compute_weighted_total, rank_totals
from app.services.scoring_engine import (
    compute_final_score,
    compute_penalty_factor,
    compute_performance_factor,
)


# --- Performance factor ---


def test_performance_factor_no_penalty_when_at_or_under_target() -> None:
    assert compute_performance_factor(1000, target_ms=1000, max_penalty_ratio=0.1) == 1.0
    assert compute_performance_factor(500, target_ms=1000, max_penalty_ratio=0.1) == 1.0


def test_performance_factor_no_penalty_when_time_unknown() -> None:
    assert compute_performance_factor(None, target_ms=1000, max_penalty_ratio=0.1) == 1.0


def test_performance_factor_penalizes_slow_execution() -> None:
    factor = compute_performance_factor(2000, target_ms=1000, max_penalty_ratio=0.1)
    assert factor < 1.0
    assert factor >= 0.9  # capped at max_penalty_ratio


def test_performance_factor_never_exceeds_max_penalty() -> None:
    # Wildly over target should still cap at (1 - max_penalty_ratio)
    factor = compute_performance_factor(100_000, target_ms=1000, max_penalty_ratio=0.1)
    assert factor == 0.9


# --- Penalty factor ---


def test_penalty_factor_full_credit_when_on_time() -> None:
    assert compute_penalty_factor(False, late_penalty_ratio=0.2) == 1.0


def test_penalty_factor_applies_late_deduction() -> None:
    assert compute_penalty_factor(True, late_penalty_ratio=0.2) == 0.8


# --- Final score ---


def test_final_score_perfect_case() -> None:
    score = compute_final_score(100, performance_factor=1.0, penalty_factor=1.0, max_score=100)
    assert score == 100.0


def test_final_score_applies_both_factors() -> None:
    score = compute_final_score(100, performance_factor=0.9, penalty_factor=0.8, max_score=100)
    assert score == 72.0


def test_final_score_never_exceeds_max_score() -> None:
    # Defensive clamp even if functional_score somehow exceeded max_score
    score = compute_final_score(150, performance_factor=1.0, penalty_factor=1.0, max_score=100)
    assert score == 100.0


def test_final_score_never_negative() -> None:
    score = compute_final_score(0, performance_factor=1.0, penalty_factor=1.0, max_score=100)
    assert score == 0.0


# --- Leaderboard aggregation ---


def test_weighted_total_sums_best_scores_with_difficulty() -> None:
    scores = [
        BestProblemScore(problem_id="p1", best_final_score=80, difficulty_multiplier=1.0),
        BestProblemScore(problem_id="p2", best_final_score=50, difficulty_multiplier=2.0),
    ]
    assert compute_weighted_total(scores) == 180.0  # 80*1.0 + 50*2.0


def test_rank_totals_orders_descending() -> None:
    ranks = rank_totals([("alice", 90.0), ("bob", 100.0), ("carol", 80.0)])
    assert ranks["bob"] == 1
    assert ranks["alice"] == 2
    assert ranks["carol"] == 3


def test_rank_totals_breaks_ties_by_user_id() -> None:
    ranks = rank_totals([("bbb", 50.0), ("aaa", 50.0)])
    assert ranks["aaa"] == 1
    assert ranks["bbb"] == 2
