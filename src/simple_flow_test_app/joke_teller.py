from __future__ import annotations

import argparse
import random
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
        prog="joke",
        description="Tell one random offline joke.",
    )


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
    args = parser.parse_args(argv)
    print(choose_joke(args.category))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
