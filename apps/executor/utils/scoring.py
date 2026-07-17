def compute_score(max_score: int, test_weights: list[float], passed_flags: list[bool]) -> float:
    """Weighted proportion of test weight passed, scaled to max_score.

    Returns 0.0 if there are no tests to avoid a division by zero.
    """
    total_weight = sum(test_weights)
    if total_weight <= 0:
        return 0.0

    earned_weight = sum(w for w, passed in zip(test_weights, passed_flags) if passed)
    return round((earned_weight / total_weight) * max_score, 2)
