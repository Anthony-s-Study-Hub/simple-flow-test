from __future__ import annotations

import subprocess
import sys
from os import environ
from pathlib import Path

from simple_flow_test_app.joke_teller import JOKES


def run_joke_teller(
    *args: str,
    input_text: str = "",
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
    result = run_joke_teller(input_text="3\n")

    assert result.returncode == 0
    assert result.stdout.splitlines()[0] in {joke for jokes in JOKES.values() for joke in jokes}
    assert "Rate this joke (0-5):" in result.stdout


def test_category_selection_prints_a_joke_from_that_category() -> None:
    for category, jokes in JOKES.items():
        result = run_joke_teller("--category", category, input_text="4\n")

        assert result.returncode == 0
        assert result.stdout.splitlines()[0] in jokes
        assert "Rate this joke (0-5):" in result.stdout


def test_invalid_category_exits_with_a_helpful_error() -> None:
    result = run_joke_teller("--category", "unknown")

    assert result.returncode != 0
    assert "general" in result.stderr
    assert "programming" in result.stderr
    assert "dad" in result.stderr


def test_count_prints_n_jokes_and_prompts_after_each() -> None:
    result = run_joke_teller("--count", "3", input_text="1\n2\n5\n")

    all_jokes = {joke for jokes in JOKES.values() for joke in jokes}
    printed_jokes = [line for line in result.stdout.splitlines() if line in all_jokes]

    assert result.returncode == 0
    assert len(printed_jokes) == 3
    assert result.stdout.count("Rate this joke (0-5):") == 3


def test_invalid_ratings_are_reprompted_until_a_score_from_zero_to_five_is_given() -> None:
    result = run_joke_teller(input_text="7\nnope\n0\n")

    assert result.returncode == 0
    assert result.stdout.count("Rate this joke (0-5):") == 3
    assert "Please enter a whole number from 0 to 5." in result.stderr


def test_non_positive_count_exits_with_a_helpful_error() -> None:
    result = run_joke_teller("--count", "0")

    assert result.returncode != 0
    assert "positive integer" in result.stderr


def test_project_exposes_the_joke_teller_console_command() -> None:
    project_root = Path(__file__).parents[1]
    pyproject = (project_root / "pyproject.toml").read_text(encoding="utf-8")

    assert 'joke-teller = "simple_flow_test_app.joke_teller:main"' in pyproject
