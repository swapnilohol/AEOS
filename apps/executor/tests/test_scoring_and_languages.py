import pytest

from images.language_configs import get_language_config
from utils.scoring import compute_score


def test_compute_score_all_passed() -> None:
    assert compute_score(100, [1.0, 1.0, 2.0], [True, True, True]) == 100.0


def test_compute_score_partial_pass() -> None:
    # 1 of 2 equal-weight tests passed -> half credit
    assert compute_score(100, [1.0, 1.0], [True, False]) == 50.0


def test_compute_score_none_passed() -> None:
    assert compute_score(100, [1.0, 1.0], [False, False]) == 0.0


def test_compute_score_weighted() -> None:
    # hidden test worth more weight than public test
    score = compute_score(100, [1.0, 3.0], [True, False])
    assert score == 25.0


def test_compute_score_no_tests_does_not_divide_by_zero() -> None:
    assert compute_score(100, [], []) == 0.0


@pytest.mark.parametrize("language", ["python", "javascript", "java", "cpp"])
def test_all_required_languages_are_configured(language: str) -> None:
    config = get_language_config(language)
    assert config.image
    assert config.source_filename
    assert "input.txt" in config.run_cmd


def test_unsupported_language_raises() -> None:
    with pytest.raises(ValueError):
        get_language_config("cobol")


def test_language_lookup_is_case_insensitive() -> None:
    assert get_language_config("Python").image == get_language_config("python").image
