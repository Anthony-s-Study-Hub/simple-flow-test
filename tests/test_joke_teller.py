from __future__ import annotations

import json
import subprocess
import sys
from os import environ
from pathlib import Path

from simple_flow_test_app.joke_teller import JOKES


def run_joke_teller(
    *args: str,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).parents[1]
    child_environment = environ.copy()
    child_environment["PYTHONPATH"] = str(project_root / "src")
    return subprocess.run(
        [sys.executable, "-m", "simple_flow_test_app.joke_teller", *args],
        capture_output=True,
        text=True,
        env=child_environment,
        input=input_text,
        check=False,
    )


def test_default_invocation_prints_one_local_joke() -> None:
    result = run_joke_teller()

    assert result.returncode == 0
    assert result.stdout.strip()
    assert result.stdout.strip() in {joke for jokes in JOKES.values() for joke in jokes}


def test_category_selection_prints_a_joke_from_that_category() -> None:
    for category, jokes in JOKES.items():
        result = run_joke_teller("--category", category)

        assert result.returncode == 0
        assert result.stdout.strip() in jokes


def test_invalid_category_exits_with_a_helpful_error() -> None:
    result = run_joke_teller("--category", "unknown")

    assert result.returncode != 0
    assert "general" in result.stderr
    assert "programming" in result.stderr
    assert "dad" in result.stderr


def test_help_lists_supported_categories() -> None:
    result = run_joke_teller("--help")

    assert result.returncode == 0
    assert "general" in result.stdout
    assert "programming" in result.stdout
    assert "dad" in result.stdout


def test_interactive_mode_persists_ratings_and_quit_skips_current_joke(tmp_path: Path) -> None:
    ratings_file = tmp_path / "ratings.json"

    result = run_joke_teller(
        "--interactive",
        "--ratings-file",
        str(ratings_file),
        input_text="5\nq\n",
    )

    assert result.returncode == 0
    assert "Rate this joke from 1 to 5" in result.stdout
    assert "Session summary: rated 1 joke(s)." in result.stdout
    ratings = json.loads(ratings_file.read_text(encoding="utf-8"))
    assert sum(len(values) for values in ratings.values()) == 1
    assert {"score": 5} in [value for values in ratings.values() for value in values]


def test_interactive_mode_retries_invalid_ratings(tmp_path: Path) -> None:
    ratings_file = tmp_path / "ratings.json"

    result = run_joke_teller(
        "--interactive",
        "--ratings-file",
        str(ratings_file),
        input_text="0\nnot-a-number\n4\nq\n",
    )

    assert result.returncode == 0
    assert result.stdout.count("Please enter a whole number from 1 to 5, or q to quit.") == 2
    ratings = json.loads(ratings_file.read_text(encoding="utf-8"))
    assert sum(len(values) for values in ratings.values()) == 1


def test_interactive_mode_does_not_repeat_jokes_in_one_session(tmp_path: Path) -> None:
    ratings_file = tmp_path / "ratings.json"

    result = run_joke_teller(
        "--interactive",
        "--ratings-file",
        str(ratings_file),
        input_text="1\n\n2\n\n3\n\n4\n\n5\n\n1\n\n",
    )

    assert result.returncode == 0
    assert "Session summary: rated 6 joke(s)." in result.stdout
    ratings = json.loads(ratings_file.read_text(encoding="utf-8"))
    assert len(ratings) == 6


def test_malformed_ratings_file_is_ignored(tmp_path: Path) -> None:
    ratings_file = tmp_path / "ratings.json"
    ratings_file.write_text("not valid json", encoding="utf-8")

    result = run_joke_teller(
        "--interactive",
        "--ratings-file",
        str(ratings_file),
        input_text="3\nq\n",
    )

    assert result.returncode == 0
    ratings = json.loads(ratings_file.read_text(encoding="utf-8"))
    assert sum(len(values) for values in ratings.values()) == 1


def test_interactive_mode_accepts_and_persists_an_optional_review(tmp_path: Path) -> None:
    ratings_file = tmp_path / "ratings.json"

    result = run_joke_teller(
        "--interactive",
        "--ratings-file",
        str(ratings_file),
        input_text="5\nAbsolutely hilarious!\nq\n",
    )

    assert result.returncode == 0
    assert "Optional review" in result.stdout
    ratings = json.loads(ratings_file.read_text(encoding="utf-8"))
    entries = [entry for values in ratings.values() for entry in values]
    assert {"score": 5, "review": "Absolutely hilarious!"} in entries


def test_interactive_mode_allows_skipping_an_optional_review(tmp_path: Path) -> None:
    ratings_file = tmp_path / "ratings.json"

    result = run_joke_teller(
        "--interactive",
        "--ratings-file",
        str(ratings_file),
        input_text="4\n\nq\n",
    )

    assert result.returncode == 0
    assert result.stdout.count("Optional review") == 1
    ratings = json.loads(ratings_file.read_text(encoding="utf-8"))
    entries = [entry for values in ratings.values() for entry in values]
    assert {"score": 4} in entries
    assert all("review" not in entry for entry in entries)


def test_interactive_mode_keeps_reviews_in_the_same_file_for_later_runs(tmp_path: Path) -> None:
    ratings_file = tmp_path / "ratings.json"

    first_result = run_joke_teller(
        "--interactive",
        "--ratings-file",
        str(ratings_file),
        input_text="2\nNeeds a stronger punchline.\nq\n",
    )
    second_result = run_joke_teller(
        "--interactive",
        "--ratings-file",
        str(ratings_file),
        input_text="q\n",
    )

    assert first_result.returncode == 0
    assert second_result.returncode == 0
    ratings = json.loads(ratings_file.read_text(encoding="utf-8"))
    entries = [entry for values in ratings.values() for entry in values]
    assert {"score": 2, "review": "Needs a stronger punchline."} in entries
