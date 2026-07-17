from app.models import Base

EXPECTED_TABLES = {
    "roles",
    "users",
    "hackathons",
    "problems",
    "problem_tests",
    "submissions",
    "execution_results",
    "scores",
    "violations",
    "leaderboard_entries",
}


def test_all_tables_registered() -> None:
    assert EXPECTED_TABLES.issubset(set(Base.metadata.tables.keys()))
