from __future__ import annotations

import argparse
import json
import random
from collections.abc import Sequence
from pathlib import Path


JOKES: dict[str, tuple[str, ...]] = {
    "general": (
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "What do you call a bear with no teeth? A gummy bear!",
    ),
    "programming": (
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "There are 10 kinds of people: those who understand binary and those who do not.",
    ),
    "dad": (
        "I only know 25 letters of the alphabet. I do not know y.",
        "What do you call cheese that is not yours? Nacho cheese!",
    ),
}

DEFAULT_RATINGS_FILE = Path.home() / ".simple-flow-joke-teller" / "ratings.json"
RatingEntry = dict[str, int | str]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="joke",
        description="Tell one random offline joke.",
    )
    parser.add_argument(
        "--category",
        choices=tuple(JOKES),
        help="Limit the joke to a category.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Show jokes one at a time and collect 1-to-5 ratings.",
    )
    parser.add_argument(
        "--ratings-file",
        type=Path,
        default=DEFAULT_RATINGS_FILE,
        help="JSON file used to persist ratings.",
    )
    return parser


def choose_joke(category: str | None = None) -> str:
    if category is None:
        jokes = tuple(joke for category_jokes in JOKES.values() for joke in category_jokes)
    else:
        jokes = JOKES[category]
    return random.choice(jokes)


def _jokes_for_session(category: str | None = None) -> list[tuple[str, str]]:
    categories = (category,) if category is not None else tuple(JOKES)
    return [
        (f"{joke_category}-{index}", joke)
        for joke_category in categories
        for index, joke in enumerate(JOKES[joke_category], start=1)
    ]


def load_ratings(path: Path) -> dict[str, list[RatingEntry]]:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}

    ratings: dict[str, list[RatingEntry]] = {}
    for joke_id, values in raw.items():
        if not isinstance(joke_id, str) or not isinstance(values, list):
            continue
        valid_entries: list[RatingEntry] = []
        for value in values:
            if type(value) is int and 1 <= value <= 5:
                valid_entries.append({"score": value})
                continue
            if not isinstance(value, dict):
                continue
            score = value.get("score")
            if type(score) is not int or not 1 <= score <= 5:
                continue
            entry: RatingEntry = {"score": score}
            review = value.get("review")
            if isinstance(review, str) and review.strip():
                entry["review"] = review.strip()
            valid_entries.append(entry)
        if valid_entries:
            ratings[joke_id] = valid_entries
    return ratings


def save_ratings(path: Path, ratings: dict[str, list[RatingEntry]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ratings, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_interactive(category: str | None, ratings_file: Path) -> int:
    session_jokes = _jokes_for_session(category)
    random.shuffle(session_jokes)
    ratings = load_ratings(ratings_file)
    rated_count = 0

    for joke_id, joke in session_jokes:
        print(f"\n{joke}")
        while True:
            try:
                response = input("Rate this joke from 1 to 5, or q to quit: ").strip().lower()
            except EOFError:
                print()
                print(f"Session summary: rated {rated_count} joke(s).")
                return 0

            if response == "q":
                print(f"Session summary: rated {rated_count} joke(s).")
                return 0

            try:
                score = int(response)
            except ValueError:
                score = 0
            if not 1 <= score <= 5:
                print("Please enter a whole number from 1 to 5, or q to quit.")
                continue

            try:
                review_response = input("Optional review (press Enter to skip): ")
            except EOFError:
                review_response = ""

            entry: RatingEntry = {"score": score}
            review = review_response.strip()
            if review.lower() == "q":
                ratings.setdefault(joke_id, []).append(entry)
                save_ratings(ratings_file, ratings)
                rated_count += 1
                print(f"Session summary: rated {rated_count} joke(s).")
                return 0
            if review:
                entry["review"] = review

            ratings.setdefault(joke_id, []).append(entry)
            save_ratings(ratings_file, ratings)
            rated_count += 1
            break

    print("No more jokes to rate.")
    print(f"Session summary: rated {rated_count} joke(s).")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.interactive:
        return run_interactive(args.category, args.ratings_file)
    print(choose_joke(args.category))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
