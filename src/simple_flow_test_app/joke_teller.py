from __future__ import annotations

import argparse
import random
import sys
from collections.abc import Sequence


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


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        prog="joke-teller",
        description="Tell random offline jokes and collect ratings.",
    )


def positive_count(value: str) -> int:
    try:
        count = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("count must be a positive integer") from exc
    if count <= 0:
        raise argparse.ArgumentTypeError("count must be a positive integer")
    return count


def prompt_for_rating() -> int | None:
    while True:
        print("Rate this joke (0-5):")
        try:
            raw_rating = input()
        except EOFError:
            print("A rating is required.", file=sys.stderr)
            return None

        try:
            rating = int(raw_rating)
        except ValueError:
            print("Please enter a whole number from 0 to 5.", file=sys.stderr)
            continue
        if not 0 <= rating <= 5:
            print("Please enter a whole number from 0 to 5.", file=sys.stderr)
            continue
        return rating


def choose_joke(category: str | None = None) -> str:
    if category is None:
        jokes = tuple(joke for category_jokes in JOKES.values() for joke in category_jokes)
    else:
        jokes = JOKES[category]
    return random.choice(jokes)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    parser.add_argument(
        "--category",
        choices=tuple(JOKES),
        help="Limit the joke to a category.",
    )
    parser.add_argument(
        "--count",
        type=positive_count,
        default=1,
        help="Tell this many jokes, prompting for a rating after each one.",
    )
    args = parser.parse_args(argv)

    ratings: list[int] = []
    for _ in range(args.count):
        print(choose_joke(args.category))
        rating = prompt_for_rating()
        if rating is None:
            return 1
        ratings.append(rating)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
