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

The command is fully offline and does not require an API key or network access.

Run the tests with:

```powershell
python -m pytest
```
