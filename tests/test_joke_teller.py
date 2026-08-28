from __future__ import annotations

import subprocess
import sys
from os import environ
from pathlib import Path

from simple_flow_test_app.joke_teller import JOKES


def run_joke_teller(*args: str) -> subprocess.CompletedProcess[str]:
    project_root = Path(__file__).parents[1]
    child_environment = environ.copy()
    child_environment["PYTHONPATH"] = str(project_root / "src")
    return subprocess.run(
        [sys.executable, "-m", "simple_flow_test_app.joke_teller", *args],
        capture_output=True,
        text=True,
        env=child_environment,
        check=False,
    )


def test_default_invocation_prints_one_local_joke() -> None:
    result = run_joke_teller()

    assert result.returncode == 0
    assert result.stdout.strip()
    assert result.stdout.strip() in {joke for jokes in JOKES.values() for joke in jokes}


def test_all_option_prints_every_local_joke() -> None:
    result = run_joke_teller("--all")

    expected = [joke for jokes in JOKES.values() for joke in jokes]
    assert result.returncode == 0
    assert result.stdout.splitlines() == expected


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
