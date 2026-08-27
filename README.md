# Simple Flow Joke Teller

An offline command-line joke teller with a small bundled joke collection.

Install it in editable mode:

```powershell
python -m pip install -e .
```

Tell a random joke:

```powershell
joke
```

Limit the result to a category:

```powershell
joke --category general
joke --category programming
joke --category dad
```

Run an interactive rating session:

```powershell
joke --interactive
joke --interactive --category programming
```

The interactive mode shows each available joke once per session and prompts
for a rating from 1 to 5, followed by an optional review. Press Enter to skip
the review; enter `q` at either prompt to quit. Ratings and written reviews
are stored locally in `~/.simple-flow-joke-teller/ratings.json`; use
`--ratings-file` to choose a different JSON file.

The command is fully offline and does not require an API key or network access.

Run the tests with:

```powershell
python -m pytest
```
